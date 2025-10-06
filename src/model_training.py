import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# === 1. Charger le dataset ===
df = pd.read_json("data/data_train.json")

# === 2. Extraire la cible (note moyenne des cours passés) ===
def extract_avg_rating(row):
    if isinstance(row.get("pastCourses"), list) and len(row["pastCourses"]) > 0:
        stars = [c.get("numberOfStars") for c in row["pastCourses"] if "numberOfStars" in c]
        if len(stars) > 0:
            return np.mean(stars)
    return np.nan

df["target"] = df.apply(extract_avg_rating, axis=1)

# === 3. Créer des features simples ===
df["num_courses"] = df["pastCourses"].apply(lambda x: len(x) if isinstance(x, list) else 0)
df["num_diplomas"] = df["diplomas"].apply(lambda x: len(x) if isinstance(x, list) else 0)
df["num_experiences"] = df["experiences"].apply(lambda x: len(x) if isinstance(x, list) else 0)
df["city"] = df["city"].fillna("Unknown")

# === 4. Garder seulement les colonnes utiles ===
X = df[["num_courses", "num_diplomas", "num_experiences"]]
y = df["target"].fillna(df["target"].mean())

# === 5. Split train/test ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === 6. Entraîner un modèle ===
model = RandomForestRegressor(n_estimators=150, random_state=42)
model.fit(X_train, y_train)

# === 7. Évaluer le modèle ===
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"✅ Entraînement terminé !")
print(f"MAE : {mae:.3f}")
print(f"RMSE : {rmse:.3f}")

# === 8. Sauvegarder le modèle ===
Path("models").mkdir(exist_ok=True)
joblib.dump(model, "models/model_stationF.pkl")
print("📦 Modèle sauvegardé : models/model_stationF.pkl")
