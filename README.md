# Station F — Satisfaction Predictor

Prédit la note de satisfaction d'un cours à partir du profil enseignant + contexte.

## 1) Entraînement

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

# Placez votre dataset
# data/data_train.json

python -m src.model_training

uvicorn api.app:app --reload --host 0.0.0.0 --port 8000


python -m src.model_training