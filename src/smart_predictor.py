import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================
# 🔹 DICTIONNAIRES DE RÉFÉRENCE
# ==========================

# Pondération par niveau de diplôme
DEGREE_LEVEL_SCORES = {
    "Certificat": 0.7,
    "Licence": 0.9,
    "Maîtrise": 1.0,
    "Master": 1.0,
    "Doctorat": 1.2,
}

# Écoles prestigieuses (impact positif sur la note)
PRESTIGIOUS_SCHOOLS = [
    "Polytechnique", "ENS", "Sorbonne", "École 42", "HEC", "CentraleSupélec", "Télécom Paris"
]

# Dictionnaire de domaines et mots-clés associés
DOMAIN_KEYWORDS = {
    "informatique": ["programmation", "développement", "python", "web", "java", "react", "c++", "ia", "html", "css"],
    "maths": ["algèbre", "analyse", "probabilités", "statistiques", "géométrie", "calcul", "modélisation"],
    "français": ["littérature", "rédaction", "grammaire", "langue", "orthographe", "expression"],
    "physique": ["électricité", "mécanique", "thermodynamique", "optique"],
    "chimie": ["molécules", "réactions", "chimique", "matière"],
    "histoire": ["civilisation", "géographie", "société", "culture", "politique"]
}


# ==========================
# 🔹 UTILITAIRES DE TEXTE
# ==========================

def extract_domain_from_text(text: str) -> str:
    text = text.lower()
    domain_scores = {d: sum(k in text for k in kws) for d, kws in DOMAIN_KEYWORDS.items()}
    return max(domain_scores, key=domain_scores.get)


def compute_similarity(text_a: str, text_b: str) -> float:
    vectorizer = TfidfVectorizer(stop_words=None)
    tfidf = vectorizer.fit_transform([text_a, text_b])
    return float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])


def compute_degree_score(diplomas: list) -> float:
    if not diplomas:
        return 1.0
    scores = [DEGREE_LEVEL_SCORES.get(d.get("level", ""), 1.0) for d in diplomas]
    return round(np.mean(scores), 2)


def compute_prestige_score(experiences: list) -> float:
    if not experiences:
        return 0.0
    count = 0
    for e in experiences:
        company = e.get("company", "").lower()
        if any(p.lower() in company for p in PRESTIGIOUS_SCHOOLS):
            count += 1
    return round(count / len(experiences), 2)


# ==========================
# 🔹 PRÉDICTION CONTEXTUELLE
# ==========================

def predict_course_score(profile: dict, course: dict) -> float:
    """Calcule la note de satisfaction probable d'un professeur pour un cours donné."""

    # ---- 1. Préparation du texte global du profil
    profile_text = " ".join([
        profile.get("description", ""),
        " ".join([d.get("title", "") for d in profile.get("diplomas", [])]),
        " ".join([e.get("title", "") for e in profile.get("experiences", [])]),
        " ".join([c.get("title", "") for c in profile.get("pastCourses", [])])
    ])

    # ---- 2. Similarité entre profil et cours
    course_text = f"{course.get('title', '')} {course.get('description', '')}"
    similarity = compute_similarity(profile_text, course_text)

    # ---- 3. Moyenne des notes passées
    past = profile.get("pastCourses", [])
    avg_stars = np.mean([c.get("numberOfStars", 4.0) for c in past]) if past else 4.0

    # ---- 4. Niveau d’étude
    degree_score = compute_degree_score(profile.get("diplomas", []))

    # ---- 5. Prestige des écoles
    prestige_score = compute_prestige_score(profile.get("experiences", []))

    # ---- 6. Compatibilité des domaines
    profile_domain = extract_domain_from_text(profile_text)
    course_domain = extract_domain_from_text(course_text)
    domain_match = 1.0 if profile_domain == course_domain else 0.7

    # ---- 7. Pondération finale
    final_score = (
        (avg_stars * 0.5)
        + (similarity * 2.0)
        + (degree_score * 0.2)
        + (prestige_score * 0.2)
    ) * domain_match

    return round(min(final_score, 5.0), 2)
