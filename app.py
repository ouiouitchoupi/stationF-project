from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel

from src.smart_predictor import (
    compute_similarity,
    compute_degree_score,
    compute_prestige_score,
    extract_domain_from_text,
    DOMAIN_KEYWORDS,
)

# === Configuration ===
app = FastAPI(
    title="Station F Satisfaction Predictor",
    version="4.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs"
)

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Chargement du modèle ===
MODEL_PATH = Path("models/model_contextual_realistic.pkl")
try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Modèle chargé : {MODEL_PATH.name}")
except Exception as e:
    print(f"⚠️ Erreur lors du chargement du modèle : {e}")
    model = None


# === Schémas Pydantic ===
class Diploma(BaseModel):
    title: str
    level: str


class Experience(BaseModel):
    title: str
    company: str


class PastCourse(BaseModel):
    title: str
    numberOfStars: float


class TeacherProfile(BaseModel):
    description: str
    city: str
    diplomas: list[Diploma]
    experiences: list[Experience]
    pastCourses: list[PastCourse]


class CourseToPredict(BaseModel):
    title: str
    description: str


class PredictionRequest(BaseModel):
    teacher_profile: TeacherProfile
    course_to_predict: CourseToPredict


# === Routes API ===
@app.get("/api/health")
def health():
    return {"status": "ok", "model": "model_contextual_realistic", "ready": model is not None}


@app.post("/api/predict")
def predict(req: PredictionRequest):
    try:
        # Convertir les objets Pydantic en dictionnaires normaux
        teacher = req.teacher_profile.dict()
        course = req.course_to_predict.dict()

        # Construire les textes
        profile_text = " ".join([
            teacher.get("description", ""),
            " ".join(d.get("title", "") for d in teacher.get("diplomas", [])),
            " ".join(e.get("title", "") + " " + e.get("company", "") for e in teacher.get("experiences", [])),
        ])
        course_text = f"{course.get('title', '')} {course.get('description', '')}"

        # Extraire les domaines
        prof_domain = extract_domain_from_text(profile_text)
        course_domain = extract_domain_from_text(course_text)

        # Features numériques
        features = {
            "similarity": compute_similarity(profile_text, course_text),
            "degree_score": compute_degree_score(teacher.get("diplomas", [])),
            "prestige_score": compute_prestige_score(teacher.get("experiences", [])),
            "n_experiences": len(teacher.get("experiences", [])),
            "n_diplomas": len(teacher.get("diplomas", [])),
            "avg_stars": np.mean([c.get("numberOfStars", 4.0) for c in teacher.get("pastCourses", [])])
        }

        # One-hot des domaines
        for d in DOMAIN_KEYWORDS.keys():
            features[f"prof_domain_{d}"] = 1 if d == prof_domain else 0
            features[f"course_domain_{d}"] = 1 if d == course_domain else 0

        # Conversion en DataFrame et alignement avec le modèle
        X = pd.DataFrame([features])
        for col in model.feature_names_in_:
            if col not in X.columns:
                X[col] = 0
        X = X[model.feature_names_in_]

        # Prédiction
        y_pred = model.predict(X)[0]
        return {"predicted_score": round(float(y_pred), 2)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {e}")



BASE_DIR = Path(__file__).parent
frontend_dir = (BASE_DIR / "frontend").resolve()

if frontend_dir.exists():
    # Sert les fichiers statiques (JS, CSS)
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    # Sert index.html à la racine
    @app.get("/", response_class=FileResponse)
    def serve_index():
        return frontend_dir / "index.html"
else:
    print("⚠️ Dossier frontend introuvable :", frontend_dir)
