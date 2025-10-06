import json
import joblib
from pathlib import Path
from src.preprocessing import build_features_from_row

MODEL_PATH = Path("models/model_stationF.pkl")

def predict_from_json(input_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    model = joblib.load(MODEL_PATH)
    X = build_features_from_row(payload)
    pred = float(model.predict(X)[0])
    return {"predicted_score": pred}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Predict satisfaction score from a JSON payload.")
    parser.add_argument("--input", required=True, help="Path to JSON file containing teacher/course profile.")
    args = parser.parse_args()

    result = predict_from_json(args.input)
    print(result)
