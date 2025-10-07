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
)

# === Configuration ===
app = FastAPI(
    title="Station F Satisfaction Predictor",
    version="3.0",
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

# === Modèle ===
MODEL_PATH = Path("models/model_contextual.pkl")
try:
    model = joblib.load(MODEL_PATH)
    print("✅ Modèle chargé avec succès.")
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
    return {"status": "ok"}

@app.post("/api/predict")
def predict(req: PredictionRequest):
    try:
        teacher = req.teacher_profile
        course = req.course_to_predict

        profile_text = " ".join([
            teacher.description,
            " ".join(d.title for d in teacher.diplomas),
            " ".join(e.title for e in teacher.experiences),
        ])
        course_text = f"{course.title} {course.description}"

        features = {
            "similarity_self": compute_similarity(profile_text, course_text),
            "degree_score": compute_degree_score([d.dict() for d in teacher.diplomas]),
            "prestige_score": compute_prestige_score([e.dict() for e in teacher.experiences]),
            "avg_stars": np.mean([c.numberOfStars for c in teacher.pastCourses]),
            "domain": extract_domain_from_text(profile_text),
        }

        X = pd.DataFrame([features])
        X = pd.get_dummies(X)
        for col in model.feature_names_in_:
            if col not in X.columns:
                X[col] = 0
        X = X[model.feature_names_in_]

        y_pred = model.predict(X)[0]
        return {"predicted_score": round(float(y_pred), 2)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {e}")

# === Frontend (après les routes API) ===
BASE_DIR = Path(__file__).parent
frontend_dir = (BASE_DIR / "frontend").resolve()

# Sert les fichiers statiques (js, css)
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Sert index.html sur /
@app.get("/", response_class=FileResponse)
def serve_index():
    return frontend_dir / "index.html"
