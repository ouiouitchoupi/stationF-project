import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingRegressor

from src.preprocessing import extract_training_features

# === Emplacements ===
DATA_PATH = Path("data/data_train_clean.json")  # ton dataset propre
MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "model_stationF.pkl"
PLOTS_TRUE_PRED = MODEL_DIR / "true_vs_pred.png"
PLOTS_ERR_HIST  = MODEL_DIR / "errors_distribution.png"
LOG_PATH        = MODEL_DIR / "training_log.txt"


def main():
    print("🚀 Début de l'entraînement du modèle Station F...\n")

    # === 1. Charger les données ===
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"❌ Fichier introuvable : {DATA_PATH}")

    df = pd.read_json(DATA_PATH)
    print(f"✅ Données chargées ({len(df)} lignes, {len(df.columns)} colonnes)")
    print(f"Colonnes disponibles : {list(df.columns)}\n")

    # Vérification de colonnes inutiles restantes
    forbidden_cols = {"fistname", "lastname", "skills"}
    remaining = [c for c in df.columns if c in forbidden_cols]
    if remaining:
        raise ValueError(f"⚠️ Ton dataset contient encore des colonnes inutiles : {remaining}. Supprime-les avant d'entraîner le modèle.")

    # === 2. Extraction des features ===
    X, y = extract_training_features(df)
    print(f"✅ Features extraites : {list(X.columns)}")
    print(f"Nombre d'exemples utilisables : {len(X)}\n")

    # === 3. Split jeu de données ===
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"📊 Jeu d'entraînement : {len(X_train)} échantillons")
    print(f"📊 Jeu de test        : {len(X_test)} échantillons\n")

    # === 4. Construction du pipeline ===
    numeric_features = ["num_courses", "num_diplomas", "num_experiences"]

    # Vérifie si 'city' existe encore dans le dataset
    categorical_features = []
    if "city" in X.columns:
        categorical_features = ["city"]

    text_feature = "text"

    # Construction dynamique des transformateurs
    transformers = [("num", "passthrough", numeric_features)]
    if categorical_features:
        transformers.append(("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features))
    transformers.append(("txt", TfidfVectorizer(
        max_features=8000, ngram_range=(1, 2), min_df=2, strip_accents="unicode"
    ), text_feature))

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
        verbose_feature_names_out=False
    )

    # === 5. Modèle + recherche d'hyperparamètres ===
    gbr = GradientBoostingRegressor(random_state=42)
    pipe = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("regressor", gbr)
    ])

    param_distributions = {
        "regressor__n_estimators": [150, 200, 300, 400],
        "regressor__learning_rate": [0.03, 0.05, 0.08, 0.1],
        "regressor__max_depth": [2, 3, 4, 5],
        "regressor__subsample": [0.7, 0.85, 1.0],
        "regressor__min_samples_leaf": [1, 2, 3, 5],
    }

    print("🔍 Lancement du tuning d'hyperparamètres (RandomizedSearchCV)...\n")
    search = RandomizedSearchCV(
        pipe,
        param_distributions=param_distributions,
        n_iter=20,
        scoring="neg_mean_absolute_error",
        cv=3,
        random_state=42,
        verbose=1,
        n_jobs=-1
    )

    search.fit(X_train, y_train)
    model = search.best_estimator_

    # === 6. Évaluation du modèle ===
    y_pred = model.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)

    print("\n✅ Entraînement terminé avec succès !")
    print(f"Best params: {search.best_params_}")
    print(f"MAE  : {mae:.3f}")
    print(f"RMSE : {rmse:.3f}")
    print(f"R²   : {r2:.3f}\n")

    # === 7. Sauvegarde du modèle ===
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"📦 Modèle sauvegardé : {MODEL_PATH.as_posix()}")

    # === 8. Graphiques de performance ===
    plt.figure(figsize=(6, 6))
    plt.scatter(y_test, y_pred, alpha=0.6)
    lo, hi = float(min(y_test.min(), y_pred.min())), float(max(y_test.max(), y_pred.max()))
    plt.plot([lo, hi], [lo, hi], color="red", linewidth=2)
    plt.title("Vraies valeurs vs Prédictions")
    plt.xlabel("Valeurs réelles")
    plt.ylabel("Valeurs prédites")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(PLOTS_TRUE_PRED, dpi=140)
    plt.close()

    errors = y_test - y_pred
    plt.figure(figsize=(6, 4))
    plt.hist(errors, bins=25, edgecolor="black")
    plt.title("Distribution des erreurs")
    plt.xlabel("Erreur (réelle - prédite)")
    plt.ylabel("Fréquence")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(PLOTS_ERR_HIST, dpi=140)
    plt.close()

    # === 9. Sauvegarde des logs ===
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(
            f"best={search.best_params_} | MAE={mae:.3f} | RMSE={rmse:.3f} | R2={r2:.3f}\n"
        )

    print(f"🧾 Logs : {LOG_PATH.as_posix()}")
    print(f"🖼️ Graphs sauvegardés : {PLOTS_TRUE_PRED.name}, {PLOTS_ERR_HIST.name}\n")
    print("🎯 Modèle prêt à être utilisé par ton API FastAPI !")


if __name__ == "__main__":
    main()
