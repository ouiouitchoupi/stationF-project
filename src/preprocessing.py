from __future__ import annotations
from typing import Dict, Any, List
import numpy as np
import pandas as pd

def count_list(lst) -> int:
    return len(lst) if isinstance(lst, list) else 0

def build_features_from_row(row: Dict[str, Any]) -> pd.DataFrame:
    """
    Construit les features minimales attendues par le pipeline :
    - num_courses, num_diplomas, num_experiences, city
    Le 'row' est un dict contenant (au minimum) :
      - pastCourses: List[dict] (optionnel)
      - diplomas: List[dict] (optionnel)
      - experiences: List[dict] (optionnel)
      - city: str (optionnel)
    """
    num_courses = count_list(row.get("pastCourses"))
    num_diplomas = count_list(row.get("diplomas"))
    num_experiences = count_list(row.get("experiences"))
    city = row.get("city")

    X = pd.DataFrame([{
        "num_courses": num_courses,
        "num_diplomas": num_diplomas,
        "num_experiences": num_experiences,
        "city": city
    }])
    return X

def build_training_xy(df: pd.DataFrame):
    """
    Construit X, y pour l'entraînement à partir du DataFrame JSON initial.
    y = moyenne des 'numberOfStars' des 'pastCourses'
    """
    def extract_avg_rating(row):
        pcs = row.get("pastCourses", None)
        if isinstance(pcs, list) and len(pcs) > 0:
            stars = [c.get("numberOfStars") for c in pcs if isinstance(c, dict) and "numberOfStars" in c]
            stars = [s for s in stars if s is not None]
            if len(stars) > 0:
                return float(np.mean(stars))
        return np.nan

    X = pd.DataFrame({
        "num_courses": df.get("pastCourses", []).apply(count_list),
        "num_diplomas": df.get("diplomas", []).apply(count_list),
        "num_experiences": df.get("experiences", []).apply(count_list),
        "city": df.get("city", None)
    })

    y = df.apply(extract_avg_rating, axis=1)
    mask = y.notna()
    return X[mask], y[mask]
