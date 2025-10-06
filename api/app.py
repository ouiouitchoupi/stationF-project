from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import joblib
import pandas as pd
from pathlib import Path

from src.preprocessing import build_features_from_row

app = FastAPI(title="Station F Satisfaction Predictor (Optimized)", version="2.0")

MODEL_PATH = Path("models/model_stationF.pkl")
if not MODEL_PATH.exists():
    raise RuntimeError("Modèle introuvable. Entraîne-le avec: python -m src.model_training")

model = joblib.load(MODEL_PATH)

# --------- Schémas d'entrée ----------
class PredictRequest(BaseModel):
    city: Optional[str] = None
    description: Optional[str] = None
    diplomas: Optional[List[Dict[str, Any]]] = None
    experiences: Optional[List[Dict[str, Any]]] = None
    pastCourses: Optional[List[Dict[str, Any]]] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(req: PredictRequest):
    try:
        X = build_features_from_row(req.model_dump())
        # Le pipeline contient déjà tout : OHE + TF-IDF + modèle
        y_pred = model.predict(X)[0]
        return {"predicted_score": round(float(y_pred), 3)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur de prédiction : {e}")
