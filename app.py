from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from pydantic import BaseModel
from src.smart_predictor import (
    compute_similarity,
    compute_degree_score,
    compute_prestige_score,
    extract_domain_from_text,
)

# ==========================================
# 🚀 CONFIGURATION DE L'APPLICATION
# ==========================================
app = FastAPI(
    title="Station F Satisfaction Predictor",
    version="5.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🤖 CHARGEMENT DU NOUVEAU MODÈLE   
# ==========================================
MODEL_PATH = Path("models/model_contextual_randomforest.pkl")
try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Modèle Random Forest chargé depuis {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"❌ Erreur lors du chargement du modèle : {e}")

# ==========================================
# 🧱 SCHÉMAS DE DONNÉES
# ==========================================
class Diploma(BaseModel):
    level: str
    title: str

class Experience(BaseModel):
    company: str
    title: str
    description: str
    duration: str

class PastCourse(BaseModel):
    title: str
    description: str
    numberOfStars: float

class Professor(BaseModel):
    fistname: str
    lastname: str
    city: str
    description: str
    diplomas: list[Diploma]
    experiences: list[Experience]
    pastCourses: list[PastCourse]

class Course(BaseModel):
    title: str
    description: str

class PredictionRequest(BaseModel):
    professor: Professor
    course: Course


# ==========================================
# 🔮 ROUTE DE PRÉDICTION
# ==========================================
@app.post("/api/predict")
def predict(req: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Modèle non chargé.")

    try:
        prof = req.professor
        course = req.course

        # 1️⃣ Texte global du profil
        profile_text = " ".join([
            prof.description,
            " ".join(d.title for d in prof.diplomas),
            " ".join(e.title for e in prof.experiences),
            " ".join(c.title for c in prof.pastCourses)
        ])

        # 2️⃣ Détection des domaines
        prof_domain = extract_domain_from_text(profile_text)
        course_domain = extract_domain_from_text(course.description)

        # 3️⃣ Calcul des features (alignées avec ton modèle)
        similarity = compute_similarity(profile_text, f"{course.title} {course.description}")
        degree_score = compute_degree_score([d.dict() for d in prof.diplomas])
        prestige_score = compute_prestige_score([e.dict() for e in prof.experiences])
        avg_stars = np.mean([c.numberOfStars for c in prof.pastCourses])

        features = {
            "similarity": similarity,
            "degree_score": degree_score,
            "prestige_score": prestige_score,
            "avg_stars": avg_stars,
        }

        # 4️⃣ Encodage des domaines (mêmes noms que dans ton modèle)
        domains = ["informatique", "maths", "français", "physique", "chimie", "histoire"]
        for d in domains:
            features[f"prof_domain_{d}"] = 1 if prof_domain == d else 0
            features[f"course_domain_{d}"] = 1 if course_domain == d else 0

        # 5️⃣ Préparation du DataFrame (sécurisée)
        X = pd.DataFrame([features])
        for col in model.feature_names_in_:
            if col not in X.columns:
                X[col] = 0
        X = X[model.feature_names_in_]

        # 6️⃣ Prédiction
        y_pred = model.predict(X)[0]
        print(f"✅ Prédiction réussie : {y_pred:.2f}")

        return {"gradeAverage": round(float(y_pred), 2)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {e}")


# ==========================================
# 🖥️ SERVEUR FRONTEND
# ==========================================
BASE_DIR = Path(__file__).parent
frontend_dir = (BASE_DIR / "frontend").resolve()
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/", response_class=FileResponse)
def serve_index():
    return frontend_dir / "index.html"
