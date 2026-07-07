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
        "data analyst",
        "data cleaning",
        "data visualization",
        "business reporting",
        "statistics",
        "pandas",
        "numpy",
        "etl",
    ],
    "ai_machine_learning": [
        "machine learning",
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
        "api",
        "jwt",
        "authentication",
        "file upload",
        "binary file storage",
        "swagger",
        "deployment",
        "backend",
        "frontend",
        "django",
        "nodejs",
        "database",
    ],
    "ui_ux_design": [
        "ui ux",
        "ui design",
        "ux design",
        "user experience",
        "user research",
        "figma",
        "wireframe",
        "wireframing",
        "prototype",
        "prototyping",
        "interaction design",
        "design system",
        "mobile design",
        "usability testing",
    ],
    "digital_marketing": [
        "digital marketing",
        "marketing analytics",
        "seo",
        "content marketing",
        "copywriting",
        "social media",
        "content strategy",
        "campaign analysis",
        "customer behavior",
        "email marketing",
        "brand strategy",
    ],
    "business_management": [
        "business model",
        "startup",
        "entrepreneurship",
        "project management",
        "business strategy",
        "market research",
        "operations management",
        "finance",
        "accounting",
        "human resource",
    ],
    "language_communication": [
        "english communication",
        "toeic",
        "ielts",
        "presentation",
        "academic writing",
        "business writing",
        "email writing",
        "listening",
        "speaking",
        "pronunciation",
        "translation",
    ],
    "education_edtech": [
        "education",
        "edtech",
        "instructional design",
        "curriculum design",
        "learning assessment",
        "teaching method",
        "e-learning",
        "training program",
    ],
    "cybersecurity": [
        "cybersecurity",
        "web security",
        "secure coding",
        "identity access management",
        "cloud security",
        "digital forensics",
        "network security",
        "penetration testing",
    ],
    "media_content": [
        "video editing",
        "motion design",
        "graphic design",
        "photography",
        "storytelling",
        "content creation",
        "visual communication",
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
    "data analytics": "data analysis",
    "data analyst": "data analyst",
    "ml": "machine learning",
    "tri tue nhan tao": "artificial intelligence",
    "ai foundation": "artificial intelligence",
    "ai product": "artificial intelligence",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "rest api": "restful api",
    "restful": "restful api",
    "mongo db": "mongodb",
    "reactjs": "react",
    "react.js": "react",
    "node.js": "nodejs",
    "node js": "nodejs",
    "json web token": "jwt",
    "auth": "authentication",
    "ux/ui": "ui ux",
    "ui/ux": "ui ux",
    "ux research": "user research",
    "wireframes": "wireframe",
    "wire framing": "wireframing",
    "search engine optimization": "seo",
    "mang xa hoi": "social media",
    "tieng anh giao tiep": "english communication",
    "giao tiep tieng anh": "english communication",
    "thuyet trinh": "presentation",
    "viet email": "email writing",
    "khoi nghiep": "startup",
    "quan tri du an": "project management",
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
