import time
from typing import Any


def active_keywords(vector: dict[str, int]) -> set[str]:
    return {key for key, value in vector.items() if value == 1}


def jaccard_score(student_vector: dict[str, int], course_vector: dict[str, int]) -> float:
    student_active = active_keywords(student_vector)
    course_active = active_keywords(course_vector)
    union = student_active | course_active
    if not union:
        return 0.0
    return len(student_active & course_active) / len(union)


def rank_courses(student_vector: dict[str, int], courses: list[dict[str, Any]]) -> list[dict]:
    results: list[dict] = []
    student_active = active_keywords(student_vector)
    for course in courses:
        started = time.perf_counter()
        course_vector = course.get("binary_vector") or {}
        score = jaccard_score(student_vector, course_vector)
        elapsed_ms = (time.perf_counter() - started) * 1000
        course_active = active_keywords(course_vector)
        results.append(
            {
                "course_document_id": course["_id"],
                "course_id": str(course["_id"]),
                "course_title": course["title"],
                "match_score": round(score, 4),
                "matched_keywords": sorted(student_active & course_active),
                "student_keywords": sorted(student_active),
                "course_keywords": sorted(course_active),
                "algorithm": "Jaccard Binary Vector",
                "processing_time_ms": round(elapsed_ms, 2),
            }
        )

    results.sort(key=lambda item: item["match_score"], reverse=True)
    for index, result in enumerate(results, start=1):
        result["rank"] = index
    return results

