import joblib
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

from src.preprocessing import build_training_xy

DATA_PATH = Path("data/data_train.json")
MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "model_stationF.pkl"

def train_and_save():
    # 1) Chargement
    df = pd.read_json(DATA_PATH)
    X, y = build_training_xy(df)

    # 2) Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3) Pipeline
    num_features = ["num_courses", "num_diplomas", "num_experiences"]
    cat_features = ["city"]

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median"))
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocess = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, num_features),
            ("cat", categorical_transformer, cat_features),
        ],
        remainder="drop"
    )

    model = Pipeline(steps=[
        ("preprocess", preprocess),
        ("regressor", RandomForestRegressor(n_estimators=200, random_state=42))
    ])

    # 4) Train
    model.fit(X_train, y_train)

    # 5) Eval
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("✅ Modèle entraîné et sauvegardé :", MODEL_PATH.as_posix())
    print(f"MAE: {mae:.3f} | RMSE: {rmse:.3f}")

if __name__ == "__main__":
    train_and_save()
