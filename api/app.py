from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import joblib
from pathlib import Path

from src.preprocessing import build_features_from_row

app = FastAPI(title="Station F Satisfaction Predictor", version="1.0.0")

MODEL_PATH = Path("models/model_stationF.pkl")
model = joblib.load(MODEL_PATH)

# --- Schémas d'entrée (souples pour accepter des champs en plus) ---
class PastCourse(BaseModel):
    numberOfStars: Optional[float] = None
    # autres champs ignorés si présents

class PredictRequest(BaseModel):
    city: Optional[str] = None
    diplomas: Optional[List[Dict[str, Any]]] = None
    experiences: Optional[List[Dict[str, Any]]] = None
    pastCourses: Optional[List[PastCourse]] = Field(default=None, description="Historique des cours précédents (optionnel)")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(req: PredictRequest):
    # convertir le modèle Pydantic en dict brut
    row = req.model_dump()
    X = build_features_from_row(row)
    yhat = float(model.predict(X)[0])
    return {"predicted_score": yhat}
