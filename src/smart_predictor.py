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
    """Détecte le domaine dominant dans un texte."""
    if not isinstance(text, str) or not text.strip():
        return "autre"
    text = text.lower()
    domain_scores = {d: sum(k in text for k in kws) for d, kws in DOMAIN_KEYWORDS.items()}
    return max(domain_scores, key=domain_scores.get)


def compute_similarity(text_a: str, text_b: str) -> float:
    """Mesure la similarité sémantique entre deux textes via TF-IDF."""
    if not text_a or not text_b:
        return 0.0
    vectorizer = TfidfVectorizer(stop_words=None)
    tfidf = vectorizer.fit_transform([text_a, text_b])
    return float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])


def compute_degree_score(diplomas: list) -> float:
    """Score moyen selon le niveau de diplôme."""
    if not diplomas:
        return 1.0
    scores = [DEGREE_LEVEL_SCORES.get(d.get("level", ""), 1.0) for d in diplomas]
    return round(np.mean(scores), 2)


def compute_prestige_score(experiences: list) -> float:
    """Score selon la proportion d’expériences dans des institutions prestigieuses."""
    if not experiences:
        return 0.0
    count = 0
    for e in experiences:
        company = e.get("company", "").lower()
        if any(p.lower() in company for p in PRESTIGIOUS_SCHOOLS):
            count += 1
    return round(count / len(experiences), 2)
