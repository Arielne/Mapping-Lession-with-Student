from time import perf_counter

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

from app.config import settings

ALGORITHM_NAME = "binary_jaccard_ngram_v1"
TOKEN_PATTERN = r"(?u)\b\w\w+\b"


def build_matches(student_text: str, course_documents: list[dict], top_k: int) -> dict:
    started_at = perf_counter()
    texts = [student_text] + [course["normalized_text"] for course in course_documents]

    vectorizer = CountVectorizer(
        binary=True,
        ngram_range=(1, 2),
        token_pattern=TOKEN_PATTERN,
        max_features=settings.matching_max_features,
    )
    matrix = vectorizer.fit_transform(texts).astype(bool)
    feature_names = np.array(vectorizer.get_feature_names_out())
    student_vector = matrix[0].toarray()[0]
    student_active_terms = int(student_vector.sum())

    results = []
    for index, course in enumerate(course_documents, start=1):
        course_vector = matrix[index].toarray()[0]
        intersection_mask = np.logical_and(student_vector, course_vector)
        union_mask = np.logical_or(student_vector, course_vector)
        union = int(union_mask.sum())
        score = 0.0 if union == 0 else float(intersection_mask.sum() / union)
        matched_terms = feature_names[intersection_mask].tolist()
        results.append(
            {
                "course_document_id": course["_id"],
                "course_title": course["course_title"],
                "score": score,
                "matched_terms": matched_terms[:50],
                "student_active_terms": student_active_terms,
                "course_active_terms": int(course_vector.sum()),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    ranked_results = [
        {**item, "rank": rank}
        for rank, item in enumerate(results[:top_k], start=1)
    ]
    processing_time_ms = (perf_counter() - started_at) * 1000

    return {
        "algorithm_name": ALGORITHM_NAME,
        "processing_time_ms": processing_time_ms,
        "vocabulary_size": len(feature_names),
        "results": ranked_results,
    }


def calculate_ground_truth_metrics(results: list[dict], ground_truth_course_id) -> tuple[bool | None, bool | None]:
    if ground_truth_course_id is None:
        return None, None

    ground_truth = str(ground_truth_course_id)
    top1_correct = bool(results and str(results[0]["course_document_id"]) == ground_truth)
    hit_at_3 = any(str(item["course_document_id"]) == ground_truth for item in results[:3])
    return top1_correct, hit_at_3
