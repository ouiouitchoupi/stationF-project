import pandas as pd
import numpy as np
from pathlib import Path
import json

DATA_PATH = Path("data/data_train.json")

def main():
    print("🔍 Vérification du dataset :", DATA_PATH)

    # === 1. Charger le JSON ===
    try:
        df = pd.read_json(DATA_PATH)
    except ValueError:
        # Si le JSON contient plusieurs lignes indépendantes
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = [json.loads(line) for line in f]
        df = pd.DataFrame(data)

    print(f"✅ Fichier chargé avec {len(df)} lignes et {len(df.columns)} colonnes.\n")

    # === 2. Aperçu général ===
    print("📋 Aperçu général des colonnes :\n", df.dtypes, "\n")

    # === 3. Vérification des valeurs manquantes ===
    missing = df.isna().sum()
    print("❓ Valeurs manquantes :\n", missing[missing > 0], "\n")

    # === 4. Vérification des structures attendues ===
    expected_lists = ["diplomas", "experiences", "pastCourses"]
    for col in expected_lists:
        if col in df.columns:
            invalid = df[col].apply(lambda x: not isinstance(x, list)).sum()
            if invalid > 0:
                print(f"⚠️ {invalid} entrées dans '{col}' ne sont pas des listes !")
        else:
            print(f"⚠️ Colonne '{col}' absente du dataset.")

    # === 5. Vérifier la colonne 'city' ===
    if "city" in df.columns:
        unique_cities = df["city"].dropna().unique()
        print(f"🏙️ Villes uniques ({len(unique_cities)}): {unique_cities[:10]}")
    else:
        print("⚠️ Pas de colonne 'city' trouvée.")

    # === 6. Vérifier les doublons ===
    duplicates = df.duplicated(subset=["fistname", "lastname"], keep=False).sum() if "fistname" in df.columns else 0
    if duplicates > 0:
        print(f"⚠️ {duplicates} doublons trouvés sur (fistname, lastname).")
    else:
        print("✅ Aucun doublon exact détecté.")

    # === 7. Vérifier les notes des cours passés ===
    def get_avg_stars(courses):
        if isinstance(courses, list) and courses:
            stars = [c.get("numberOfStars") for c in courses if isinstance(c, dict)]
            stars = [s for s in stars if isinstance(s, (int, float))]
            if stars:
                return np.mean(stars)
        return np.nan

    if "pastCourses" in df.columns:
        df["avg_stars"] = df["pastCourses"].apply(get_avg_stars)
        print("\n📊 Statistiques des notes passées :")
        print(df["avg_stars"].describe())

        # === Nettoyage optionnel ===
    drop_cols = ["fistname", "lastname", "skills"]
    for col in drop_cols:
        if col in df.columns:
            df.drop(columns=col, inplace=True)
            print(f"🧹 Colonne supprimée : {col}")

    # Si city est unique, on la supprime
    if "city" in df.columns and df["city"].nunique() == 1:
        df.drop(columns=["city"], inplace=True)
        print("🏙️ Colonne 'city' supprimée (valeur unique).")

    # Sauvegarde du dataset propre
    clean_path = DATA_PATH.parent / "data_train_clean.json"
    df.to_json(clean_path, orient="records", force_ascii=False, indent=2)
    print(f"\n🧽 Dataset nettoyé sauvegardé sous : {clean_path}")


    print("\n✅ Vérification terminée.")

if __name__ == "__main__":
    main()
