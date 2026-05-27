from app.utils.keyword_extractor import SKILL_DICTIONARY


def build_binary_vector(keywords_found: list[str]) -> dict[str, int]:
    found = set(keywords_found)
    return {skill: 1 if skill in found else 0 for skill in SKILL_DICTIONARY}

