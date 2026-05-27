import re

SKILL_DICTIONARY = [
    "Python",
    "Pandas",
    "SQL",
    "React",
    "FastAPI",
    "MongoDB",
    "Power BI",
    "Machine Learning",
    "Excel",
    "English",
    "Communication",
    "Data Visualization",
    "NumPy",
    "Scikit-learn",
    "JavaScript",
    "HTML",
    "CSS",
    "Docker",
    "Git",
    "Statistics",
]

SYNONYMS = {
    "Data Visualization": ["data visualization", "data visualisation", "visualization"],
    "Machine Learning": ["machine learning", "ml"],
    "Power BI": ["power bi", "powerbi"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "JavaScript": ["javascript", "js"],
}


def _contains_term(text: str, term: str) -> bool:
    pattern = r"(?<![a-z0-9+#])" + re.escape(term.lower()) + r"(?![a-z0-9+#])"
    return re.search(pattern, text) is not None


def extract_keywords(cleaned_text: str) -> list[str]:
    found: list[str] = []
    for skill in SKILL_DICTIONARY:
        terms = SYNONYMS.get(skill, [skill.lower()])
        if any(_contains_term(cleaned_text, term) for term in terms):
            found.append(skill)
    return found

