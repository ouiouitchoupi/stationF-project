import requests
import json

# === CONFIGURATION ===
# 🔧 change cette URL si ton ngrok te donne une nouvelle adresse
API_URL = "https://uncontaminable-vita-overtly.ngrok-free.dev/api/predict"

def send_prediction_request(teacher_profile, course_to_predict):
    payload = {
        "teacher_profile": teacher_profile,
        "course_to_predict": course_to_predict
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        print(f"✅ Note prédite : {response.json()['predicted_score']} / 5")
    else:
        print(f"❌ Erreur {response.status_code}: {response.text}")


# === EXEMPLES DE PROFILS ===

# 1️⃣ Prof de français enseigne Python → note basse attendue
prof_français = {
    "description": "Professeur de littérature française, 10 ans d'expérience à la Sorbonne.",
    "city": "Paris",
    "diplomas": [{"title": "Master Lettres Modernes", "level": "Master"}],
    "experiences": [{"title": "Professeur de Français", "company": "Sorbonne"}],
    "pastCourses": [{"title": "Grammaire avancée", "numberOfStars": 4.8}]
}

cours_python = {
    "title": "Programmation Python",
    "description": "Introduction à la programmation, aux boucles et aux structures de données."
}

print("=== Test 1 : Prof de français → Cours Python ===")
send_prediction_request(prof_français, cours_python)


# 2️⃣ Prof d’informatique enseigne Python → note haute attendue
prof_info = {
    "description": "Formateur en développement web et Python, enseignant depuis 8 ans en école d’ingénieurs.",
    "city": "Lyon",
    "diplomas": [{"title": "Master Informatique", "level": "Master"}],
    "experiences": [{"title": "Formateur Python", "company": "École 42"}],
    "pastCourses": [{"title": "Programmation Python avancée", "numberOfStars": 4.7}]
}

print("\n=== Test 2 : Prof d’informatique → Cours Python ===")
send_prediction_request(prof_info, cours_python)


# 3️⃣ Prof de maths enseigne littérature → note moyenne/basse attendue
prof_maths = {
    "description": "Professeur de mathématiques appliquées, expert en probabilités et modélisation.",
    "city": "Toulouse",
    "diplomas": [{"title": "Doctorat en Mathématiques", "level": "Doctorat"}],
    "experiences": [{"title": "Enseignant-Chercheur", "company": "Université de Toulouse"}],
    "pastCourses": [{"title": "Statistiques avancées", "numberOfStars": 4.6}]
}

cours_litt = {
    "title": "Analyse littéraire française",
    "description": "Étude approfondie de textes classiques et modernes."
}

print("\n=== Test 3 : Prof de maths → Cours de littérature ===")
send_prediction_request(prof_maths, cours_litt)
