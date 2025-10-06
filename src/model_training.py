import pandas as pd
from pycaret.regression import setup, compare_models, finalize_model, save_model

# === 1. Charger les données ===
df = pd.read_json("data/data_train.json")

# === 2. Construire les features de base ===
def extract_avg_rating(row):
    if isinstance(row.get("pastCourses"), list) and len(row["pastCourses"]) > 0:
        stars = [c.get("numberOfStars") for c in row["pastCourses"] if "numberOfStars" in c]
        if stars:
            return sum(stars) / len(stars)
    return None

df["target"] = df.apply(extract_avg_rating, axis=1)
df["num_courses"] = df["pastCourses"].apply(lambda x: len(x) if isinstance(x, list) else 0)
df["num_diplomas"] = df["diplomas"].apply(lambda x: len(x) if isinstance(x, list) else 0)
df["num_experiences"] = df["experiences"].apply(lambda x: len(x) if isinstance(x, list) else 0)
df["city"] = df["city"].fillna("Unknown")

# === 3. Préparer le jeu de données ===
data = df[["num_courses", "num_diplomas", "num_experiences", "city", "target"]].dropna()

# === 4. Configuration PyCaret ===
s = setup(
    data=data,
    target="target",
    session_id=42,
    normalize=True,
    silent=True,
    verbose=False
)

# === 5. Comparer et trouver le meilleur modèle ===
best = compare_models()

# === 6. Entraîner le modèle final ===
final_model = finalize_model(best)

# === 7. Sauvegarder le modèle ===
save_model(final_model, "models/model_stationF_pycaret")

print("✅ Modèle PyCaret entraîné et sauvegardé : models/model_stationF_pycaret.pkl")
