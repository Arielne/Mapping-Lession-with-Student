import re
import unicodedata


SKILL_GROUPS = {
    "data_analyst_bi": [
        "python",
        "sql",
        "excel",
        "power bi",
        "tableau",
        "dashboard",
        "data analysis",
        "data cleaning",
        "data visualization",
        "business reporting",
        "statistics",
        "pandas",
    ],
    "ai_machine_learning": [
        "machine learning",
        "ai",
        "artificial intelligence",
        "deep learning",
        "neural network",
        "classification",
        "regression",
        "model evaluation",
        "scikit-learn",
        "computer vision",
        "feature engineering",
        "data preprocessing",
    ],
    "web_backend": [
        "fastapi",
        "mongodb",
        "gridfs",
        "react",
        "restful api",
        "jwt",
        "authentication",
        "file upload",
        "binary file storage",
        "swagger",
        "deployment",
        "backend",
        "frontend",
    ],
}

ALL_SKILLS = list(dict.fromkeys(skill for skills in SKILL_GROUPS.values() for skill in skills))

SYNONYM_MAP = {
    "powerbi": "power bi",
    "bi dashboard": "dashboard",
    "visualisation": "data visualization",
    "data visualisation": "data visualization",
    "clean data": "data cleaning",
    "data cleansing": "data cleaning",
    "reporting": "business reporting",
    "business intelligence": "business reporting",
    "ml": "machine learning",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "rest api": "restful api",
    "restful": "restful api",
    "mongo db": "mongodb",
    "reactjs": "react",
    "react.js": "react",
    "json web token": "jwt",
    "auth": "authentication",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "about",
    "your",
    "you",
    "we",
    "our",
    "can",
    "will",
    "course",
    "student",
    "learn",
    "learning",
    "skill",
    "skills",
    "va",
    "voi",
    "cua",
    "cac",
    "cho",
    "trong",
    "mot",
    "la",
    "co",
    "duoc",
    "hoc",
    "khoa",
}


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(character for character in normalized if not unicodedata.combining(character))


def _replace_synonyms(text: str) -> str:
    for source, target in SYNONYM_MAP.items():
        text = re.sub(rf"(?<!\w){re.escape(source)}(?!\w)", target, text)
    return text


def normalize_text(text: str) -> str:
    cleaned = unicodedata.normalize("NFKC", text or "").lower()
    cleaned = _strip_accents(cleaned)
    cleaned = _replace_synonyms(cleaned)
    cleaned = re.sub(r"[^a-z0-9+#.\-\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    tokens = [token for token in cleaned.split() if token not in STOPWORDS]
    return " ".join(tokens)


def extract_skills(text: str) -> list[str]:
    normalized = normalize_text(text)
    skills = []
    for skill in ALL_SKILLS:
        if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", normalized):
            skills.append(skill)
    return skills


def preview_text(text: str, limit: int = 280) -> str:
    compact = re.sub(r"\s+", " ", text or "").strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."
