import re
from time import perf_counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings
from app.services.text_normalization_service import ALL_SKILLS, STOPWORDS, extract_skills, normalize_text

ALGORITHM_NAME = "tfidf_cosine_v1"
EXPLANATION_ALGORITHM_NAME = "keyword_overlap_v1"
BASELINE_ALGORITHM_NAME = "binary_jaccard_ngram_v1"
TOKEN_PATTERN = r"(?u)\b\w[\w+#.\-]+\b"


def _course_group_key(course: dict) -> str:
    course_id = course.get("course_id")
    if course_id:
        return str(course_id)
    title = normalize_text(course.get("course_title", ""))
    return title or str(course.get("_id"))


def _contains_skill(text: str, skill: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", text))


def compute_keyword_overlap(student_text: str, course_text: str) -> dict:
    student_normalized = normalize_text(student_text)
    course_normalized = normalize_text(course_text)
    student_skills = set(extract_skills(student_normalized))
    course_skills = set(extract_skills(course_normalized))

    if not course_skills:
        course_skills = {skill for skill in ALL_SKILLS if _contains_skill(course_normalized, skill)}

    matched_keywords = sorted(student_skills & course_skills)
    missing_keywords = sorted(course_skills - student_skills)
    overlap_score = 0.0 if not course_skills else len(matched_keywords) / len(course_skills)
    return {
        "algorithm_name": EXPLANATION_ALGORITHM_NAME,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "overlap_score": overlap_score,
    }


def _build_explanation(course_title: str, matched_keywords: list[str], missing_keywords: list[str]) -> str:
    if matched_keywords:
        return (
            f"This course matches your CV because it shares skills such as "
            f"{', '.join(matched_keywords[:5])}."
        )
    if missing_keywords:
        return (
            f"This course can help you build skills such as "
            f"{', '.join(missing_keywords[:5])}."
        )
    return f"{course_title} is ranked by text similarity, but no benchmark keyword overlap was detected."


def compute_tfidf_cosine_matches(student_text: str, course_documents: list[dict], top_k: int) -> dict:
    started_at = perf_counter()
    texts = [student_text] + [
        f"{course.get('course_title', '')} {course.get('normalized_text', '')}"
        for course in course_documents
    ]
    vectorizer = TfidfVectorizer(
        token_pattern=TOKEN_PATTERN,
        ngram_range=(1, 2),
        stop_words=list(STOPWORDS),
        max_features=settings.matching_max_features,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(texts)
    scores = cosine_similarity(matrix[0], matrix[1:]).flatten()
    vocabulary_size = len(vectorizer.get_feature_names_out())

    grouped: dict[str, dict] = {}
    for index, course in enumerate(course_documents):
        course_text = f"{course.get('course_title', '')} {course.get('normalized_text', '')}"
        keyword_data = compute_keyword_overlap(student_text, course_text)
        score = float(scores[index])
        course_id = str(course.get("course_id") or course.get("_id"))
        course_document_id = course.get("_id")
        matched_keywords = keyword_data["matched_keywords"]
        missing_keywords = keyword_data["missing_keywords"]
        item = {
            "course_id": course_id,
            "course_document_id": course_document_id,
            "source_course_document_id": course_document_id,
            "course_title": course.get("course_title", "Untitled course"),
            "score": score,
            "match_score": score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "explanation": _build_explanation(course.get("course_title", "This course"), matched_keywords, missing_keywords),
            "matched_terms": matched_keywords,
            "recommendation_reason": _build_explanation(
                course.get("course_title", "This course"),
                matched_keywords,
                missing_keywords,
            ),
            "relevant_skills": matched_keywords,
            "missing_or_recommended_skills": missing_keywords,
            "suggested_learning_outcomes": missing_keywords,
            "score_breakdown": {
                "tfidf_cosine_score": score,
                "keyword_overlap_score": keyword_data["overlap_score"],
            },
            "algorithm_name": ALGORITHM_NAME,
            "explanation_algorithm_name": EXPLANATION_ALGORITHM_NAME,
            "baseline_algorithm_name": BASELINE_ALGORITHM_NAME,
            "student_active_terms": int(matrix[0].count_nonzero()),
            "course_active_terms": int(matrix[index + 1].count_nonzero()),
        }

        group_key = _course_group_key(course)
        current = grouped.get(group_key)
        if current is None or item["score"] > current["score"]:
            grouped[group_key] = item

    results = sorted(grouped.values(), key=lambda item: item["score"], reverse=True)[:top_k]
    ranked_results = [{**item, "rank": rank} for rank, item in enumerate(results, start=1)]
    return {
        "algorithm_name": ALGORITHM_NAME,
        "processing_time_ms": (perf_counter() - started_at) * 1000,
        "vocabulary_size": vocabulary_size,
        "results": ranked_results,
        "recommendations": ranked_results,
    }


def build_matches(student_text: str, course_documents: list[dict], top_k: int) -> dict:
    return compute_tfidf_cosine_matches(student_text, course_documents, top_k)


def calculate_ground_truth_metrics(results: list[dict], ground_truth_course_id) -> tuple[bool | None, bool | None]:
    if ground_truth_course_id is None:
        return None, None

    ground_truth = str(ground_truth_course_id)
    top1_correct = bool(results and str(results[0].get("course_document_id")) == ground_truth)
    hit_at_3 = any(str(item.get("course_document_id")) == ground_truth for item in results[:3])
    return top1_correct, hit_at_3
