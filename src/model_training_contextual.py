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
    DOMAIN_KEYWORDS,
)

# === CONFIGURATION ===
DATA_PATH = Path("data/data_train_test.json")
MODEL_PATH = Path("models/model_contextual_realistic.pkl")

# === GÉNÉRATION DE DONNÉES SYNTHÉTIQUES ===
def simulate_course_pairings(df: pd.DataFrame):
    """Crée un dataset réaliste (professeur x cours à venir) avec des notes simulées."""
    simulated = []
    for _, prof in df.iterrows():
        base = prof.to_dict()
        profile_text = " ".join([
            base.get("description", ""),
            " ".join(d.get("title", "") for d in base.get("diplomas", [])),
            " ".join(e.get("title", "") for e in base.get("experiences", []))
        ])
        prof_domain = extract_domain_from_text(profile_text)

        for domain_name, keywords in DOMAIN_KEYWORDS.items():
            course_text = " ".join(keywords)
            sim = compute_similarity(profile_text, course_text)

            # Note simulée : élevée si le domaine correspond, sinon basse
            base_note = 4.6 if domain_name == prof_domain else 2.7
            note = base_note + np.random.normal(0, 0.3)
            note = max(1.0, min(5.0, note))

            simulated.append({
                "professorId": base.get("professorId"),
                "prof_domain": prof_domain,
                "course_domain": domain_name,
                "similarity": sim,
                "degree_score": compute_degree_score(base.get("diplomas", [])),
                "prestige_score": compute_prestige_score(base.get("experiences", [])),
                "n_experiences": len(base.get("experiences", [])),
                "n_diplomas": len(base.get("diplomas", [])),
                "avg_stars": np.mean([c.get("numberOfStars", 4.0) for c in base.get("pastCourses", [])]),
                "target": round(note, 2)
            })
    return pd.DataFrame(simulated)


# === ENTRAÎNEMENT DU MODÈLE ===
def main():
    print("🚀 Entraînement du modèle contextuel réaliste...")

    # Chargement du dataset enrichi
    df = pd.read_json(DATA_PATH)
    print(f"✅ Dataset chargé ({len(df)} profils enseignants)")

    # Génération de données synthétiques réalistes
    synthetic_df = simulate_course_pairings(df)
    print(f"🧩 Données générées : {synthetic_df.shape[0]} paires prof–cours")

    # One-hot encoding des domaines
    synthetic_df = pd.get_dummies(synthetic_df, columns=["prof_domain", "course_domain"])

    # Définition des features et de la cible
    X = synthetic_df.drop(columns=["target", "professorId"])
    y = synthetic_df["target"]

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Modèle
    model = GradientBoostingRegressor(
        n_estimators=400,
        learning_rate=0.05,
        max_depth=5,
        random_state=42
    )

    # Entraînement
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Évaluation
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"✅ Entraînement terminé : MAE={mae:.3f}, R²={r2:.3f}")

    # Sauvegarde
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"📦 Modèle sauvegardé dans : {MODEL_PATH.resolve()}")

if __name__ == "__main__":
    main()
