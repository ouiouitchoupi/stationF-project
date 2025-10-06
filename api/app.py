from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from src.preprocessing import build_features_from_row

app = FastAPI()
model = joblib.load("models/model_stationF.pkl")

class PredictRequest(BaseModel):
    city: str | None = None
    diplomas: list | None = None
    experiences: list | None = None
    pastCourses: list | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(req: PredictRequest):
    row = req.model_dump()
    X = build_features_from_row(row)
    # On garde les features utilisées pour l’entraînement
    X = X[["num_courses", "num_diplomas", "num_experiences"]]
    y_pred = model.predict(X)
    return {"predicted_score": float(y_pred[0])}
