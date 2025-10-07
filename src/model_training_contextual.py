import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

from src.smart_predictor import (
    compute_similarity,
    compute_degree_score,
    compute_prestige_score,
    extract_domain_from_text,
)

DATA_PATH = Path("data/data_train_clean.json")
MODEL_PATH = Path("models/model_contextual.pkl")

def extract_features(row):
    # 1️⃣ Concaténer les textes
    desc = row.get("description", "")
    diplomas = " ".join(d.get("title", "") for d in row.get("diplomas", []))
    exps = " ".join(e.get("title", "") + " " + e.get("company", "") for e in row.get("experiences", []))
    past_titles = " ".join(c.get("title", "") for c in row.get("pastCourses", []))
    past_desc = " ".join(c.get("course_description", "") for c in row.get("pastCourses", []))
    full_text = f"{desc} {diplomas} {exps} {past_titles} {past_desc}"

    # 2️⃣ Calcul des indicateurs
    similarity_self = compute_similarity(desc, past_desc)  # Similarité interne : enseignement ↔ cours donnés
    degree_score = compute_degree_score(row.get("diplomas", []))
    prestige_score = compute_prestige_score(row.get("experiences", []))
    avg_stars = np.mean([c.get("numberOfStars", 4.0) for c in row.get("pastCourses", [])])
    domain = extract_domain_from_text(full_text)

    return {
        "similarity_self": similarity_self,
        "degree_score": degree_score,
        "prestige_score": prestige_score,
        "avg_stars": avg_stars,
        "domain": domain
    }

def main():
    print("🚀 Entraînement du modèle contextuel...")
    df = pd.read_json(DATA_PATH)
    df = df.fillna("")

    features = df.apply(extract_features, axis=1, result_type="expand")
    features["target"] = df["avg_stars"]

    # One-hot encode domain
    features = pd.get_dummies(features, columns=["domain"])

    X = features.drop("target", axis=1)
    y = features["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(
        n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"✅ Entraînement terminé : MAE={mae:.3f}, R²={r2:.3f}")

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"📦 Modèle sauvegardé dans {MODEL_PATH.as_posix()}")

if __name__ == "__main__":
    main()
