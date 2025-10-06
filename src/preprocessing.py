from __future__ import annotations
from typing import Any, Dict, Iterable
import pandas as pd
import numpy as np

# ---------- Helpers ----------
def _safe_len(x: Any) -> int:
    return len(x) if isinstance(x, list) else 0

def _join_text(items: Iterable[Dict[str, Any]], keys=("title", "level", "company")) -> str:
    """Concatène proprement quelques champs textuels d'une liste d'objets."""
    if not isinstance(items, list):
        return ""
    parts = []
    for obj in items:
        if isinstance(obj, dict):
            for k in keys:
                v = obj.get(k)
                if isinstance(v, str) and v.strip():
                    parts.append(v.strip())
    return " ".join(parts)

def _combine_text_from_row(row: Dict[str, Any]) -> str:
    """Texte global pour TF-IDF : description + diplomas + experiences."""
    desc = row.get("description") or ""
    dipl_text = _join_text(row.get("diplomas"), keys=("title", "level"))
    exp_text  = _join_text(row.get("experiences"), keys=("title", "company", "city"))
    city = row.get("city") or ""
    return " ".join([str(desc), dipl_text, exp_text, str(city)]).strip()

# ---------- Features pour prédiction (API) ----------
def build_features_from_row(row: Dict[str, Any]) -> pd.DataFrame:
    """
    Construit exactement les features attendues par le pipeline entraîné :
      - num_courses, num_diplomas, num_experiences (numériques)
      - city (catégorielle)
      - text (TF-IDF)
    """
    X = pd.DataFrame([{
        "num_courses": _safe_len(row.get("pastCourses")),
        "num_diplomas": _safe_len(row.get("diplomas")),
        "num_experiences": _safe_len(row.get("experiences")),
        "city": (row.get("city") or "Unknown"),
        "text": _combine_text_from_row(row),
    }])
    return X

# ---------- Features + cible pour l'entraînement ----------
def extract_training_features(df: pd.DataFrame):
    """
    X :
      - num_courses / num_diplomas / num_experiences / city / text
    y :
      - moyenne des numberOfStars dans pastCourses
    """
    def avg_stars(courses):
        if isinstance(courses, list) and courses:
            stars = [c.get("numberOfStars") for c in courses if isinstance(c, dict)]
            stars = [s for s in stars if s is not None]
            if stars:
                return float(np.mean(stars))
        return np.nan

    # Crée les features de base
    X = pd.DataFrame({
        "num_courses": df.get("pastCourses", pd.Series([[]]*len(df))).apply(_safe_len),
        "num_diplomas": df.get("diplomas", pd.Series([[]]*len(df))).apply(_safe_len),
        "num_experiences": df.get("experiences", pd.Series([[]]*len(df))).apply(_safe_len),
    })

    # Gestion robuste de la colonne city
    if "city" in df.columns:
        X["city"] = df["city"].fillna("Unknown")
    else:
        X["city"] = ["Unknown"] * len(df)

    # Ajoute la feature textuelle combinée
    X["text"] = df.apply(lambda r: _combine_text_from_row(r), axis=1)

    # Crée la cible
    y = df.apply(lambda r: avg_stars(r.get("pastCourses")), axis=1)
    mask = y.notna()
    return X[mask].reset_index(drop=True), y[mask].reset_index(drop=True)
