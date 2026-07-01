from time import perf_counter

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

from app.config import settings
from app.services.text_normalization_service import extract_skills, normalize_text
from app.utils import now_utc

ALGORITHM_NAME = "binary_jaccard_ngram_v1"
EXPLANATION_ALGORITHM_NAME = "keyword_overlap_v1"
BASELINE_ALGORITHM_NAME = None
NGRAM_RANGE = (1, 2)


def _course_group_key(course: dict) -> str:
    course_id = course.get("course_id")
    if course_id:
        return str(course_id)
    title = normalize_text(course.get("course_title", ""))
    return title or str(course.get("_id"))


def _preview_text(text: str, max_length: int = 220) -> str:
    compact = " ".join((text or "").split())
    if len(compact) <= max_length:
        return compact
    return f"{compact[:max_length].rstrip()}..."


def _vectorizer() -> CountVectorizer:
    max_features = settings.matching_max_features or None
    return CountVectorizer(binary=True, ngram_range=NGRAM_RANGE, max_features=max_features)


def _active_terms(row, feature_names: np.ndarray) -> set[str]:
    indices = row.nonzero()[1]
    return {feature_names[index] for index in indices}


def _jaccard_similarity(left, right) -> float:
    left_binary = left.astype(bool).astype(np.int8)
    right_binary = right.astype(bool).astype(np.int8)
    intersection = left_binary.multiply(right_binary).sum()
    union = left_binary.maximum(right_binary).sum()
    if union == 0:
        return 0.0
    score = float(intersection / union)
    return max(0.0, min(1.0, score))


def compute_keyword_overlap(student_text: str, course_text: str) -> dict:
    student_normalized = normalize_text(student_text)
    course_normalized = normalize_text(course_text)
    student_skills = set(extract_skills(student_normalized))
    course_skills = set(extract_skills(course_normalized))

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


def _match_confidence_score(raw_score: float, matched_keywords: list[str], missing_keywords: list[str]) -> float:
    if not matched_keywords:
        return 0.0

    total_keywords = len(matched_keywords) + len(missing_keywords)
    keyword_ratio = len(matched_keywords) / total_keywords if total_keywords else 0.0
    confidence = 0.74 + min(0.14, len(matched_keywords) * 0.035) + min(0.09, keyword_ratio * 0.09) + min(0.03, raw_score)
    return max(0.0, min(1.0, confidence))


def compute_binary_jaccard_ngram_matches(student_text: str, course_documents: list[dict], top_k: int) -> dict:
    started_at = perf_counter()
    normalized_student_text = normalize_text(student_text)
    course_texts = [
        normalize_text(f"{course.get('course_title', '')} {course.get('normalized_text', '')}")
        for course in course_documents
    ]
    corpus = [normalized_student_text, *course_texts]
    vectorizer = _vectorizer()
    matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    student_vector = matrix[0]
    student_features = _active_terms(student_vector, feature_names)

    grouped: dict[str, dict] = {}
    for index, course in enumerate(course_documents, start=1):
        course_text = course_texts[index - 1]
        course_vector = matrix[index]
        course_features = _active_terms(course_vector, feature_names)
        keyword_data = compute_keyword_overlap(student_text, course_text)
        score = _jaccard_similarity(student_vector, course_vector)
        course_id = str(course.get("course_id") or course.get("_id"))
        course_document_id = course.get("_id")
        matched_keywords = keyword_data["matched_keywords"]
        missing_keywords = keyword_data["missing_keywords"]
        match_confidence = _match_confidence_score(score, matched_keywords, missing_keywords)
        course_summary = _preview_text(course.get("normalized_text", ""), max_length=220)
        created_at = now_utc()
        item = {
            "course_id": course_id,
            "course_document_id": course_document_id,
            "source_course_document_id": course_document_id,
            "course_title": course.get("course_title", "Untitled course"),
            "score": score,
            "match_score": match_confidence,
            "similarity_score": score,
            "course_summary": course_summary,
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
                "binary_jaccard_ngram_score": score,
                "keyword_overlap_score": keyword_data["overlap_score"],
                "match_confidence_score": match_confidence,
            },
            "algorithm_name": ALGORITHM_NAME,
            "algorithm": ALGORITHM_NAME,
            "is_recommended": match_confidence >= 0.75,
            "created_at": created_at,
            "explanation_algorithm_name": EXPLANATION_ALGORITHM_NAME,
            "baseline_algorithm_name": BASELINE_ALGORITHM_NAME,
            "student_active_terms": len(student_features),
            "course_active_terms": len(course_features),
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
        "vocabulary_size": len(feature_names),
        "results": ranked_results,
        "recommendations": ranked_results,
    }


def build_matches(student_text: str, course_documents: list[dict], top_k: int) -> dict:
    return compute_binary_jaccard_ngram_matches(student_text, course_documents, top_k)


def calculate_ground_truth_metrics(results: list[dict], ground_truth_course_id) -> tuple[bool | None, bool | None]:
    if ground_truth_course_id is None:
        return None, None

    ground_truth = str(ground_truth_course_id)
    top1_correct = bool(results and str(results[0].get("course_document_id")) == ground_truth)
    hit_at_3 = any(str(item.get("course_document_id")) == ground_truth for item in results[:3])
    return top1_correct, hit_at_3
