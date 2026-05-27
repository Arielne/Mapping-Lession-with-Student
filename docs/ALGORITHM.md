# Binary Vector Matching Algorithm

**Algorithm:** Jaccard Similarity trên Binary Keyword Vector  
**Version:** 1.0

---

## 1. Algorithm Goal

Đo mức độ tương đồng giữa **nhu cầu học tập của học viên** và **nội dung một khóa học** dựa trên tập kỹ năng/từ khóa chung, sử dụng vector nhị phân 0/1 và công thức Jaccard Similarity.

**Không phải:** so sánh bytes file, so sánh full-text, hay embedding vector.  
**Là:** so sánh hai tập kỹ năng dưới dạng vector nhị phân.

---

## 2. Input

| Input | Nguồn | Format |
|-------|-------|--------|
| Student document | Student upload CV/DOCX/PDF | Đã được xử lý → `binary_vector` |
| Course documents | Admin upload syllabus/PDF/DOCX | Đã được xử lý → `binary_vector` |

Cả hai phải có `processing_status = "processed"` trước khi matching.

---

## 3. Keyword Dictionary (SKILL_DICTIONARY)

Bộ từ khóa/kỹ năng cố định dùng làm chiều (dimension) của vector:

```python
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
    # ... thêm từ khóa tùy đồ án
]
```

**Nguyên tắc:**
- Tất cả documents (course + student) dùng **cùng một** SKILL_DICTIONARY.
- Vector phải có **tất cả** key từ SKILL_DICTIONARY (để union/intersection tính được).
- Nếu bổ sung từ khóa, phải re-process tất cả documents.

---

## 4. Binary Vector

### Cách tạo

```python
def build_binary_vector(keywords_found: list[str]) -> dict[str, int]:
    """
    keywords_found: danh sách từ khóa tìm thấy trong document
    Trả về: dict với tất cả key từ SKILL_DICTIONARY, value 0 hoặc 1
    """
    return {
        skill: (1 if skill in keywords_found else 0)
        for skill in SKILL_DICTIONARY
    }
```

### Ví dụ

Học viên SV01 – "Muốn học Python, Pandas, Data Visualization":
```json
{
  "Python": 1,
  "Pandas": 1,
  "SQL": 0,
  "React": 0,
  "FastAPI": 0,
  "MongoDB": 0,
  "Power BI": 0,
  "Machine Learning": 0,
  "Excel": 0,
  "English": 0,
  "Communication": 0,
  "Data Visualization": 1
}
```

Khóa học A – "Python for Data Analysis" (dạy Python, Pandas, SQL, Data Visualization):
```json
{
  "Python": 1,
  "Pandas": 1,
  "SQL": 1,
  "React": 0,
  "FastAPI": 0,
  "MongoDB": 0,
  "Power BI": 0,
  "Machine Learning": 0,
  "Excel": 0,
  "English": 0,
  "Communication": 0,
  "Data Visualization": 1
}
```

---

## 5. Jaccard Similarity

### Công thức

```
J(A, B) = |A ∩ B| / |A ∪ B|
```

Trong đó:
- `A` = tập kỹ năng của học viên có giá trị `1`
- `B` = tập kỹ năng của khóa học có giá trị `1`
- `|A ∩ B|` = số kỹ năng xuất hiện trong **cả hai**
- `|A ∪ B|` = số kỹ năng xuất hiện trong **ít nhất một**

### Ví dụ tính tay

```
A = {Python, Pandas, Data Visualization}          (3 kỹ năng)
B = {Python, Pandas, SQL, Data Visualization}     (4 kỹ năng)

A ∩ B = {Python, Pandas, Data Visualization}      → |∩| = 3
A ∪ B = {Python, Pandas, SQL, Data Visualization} → |∪| = 4

J(A, B) = 3 / 4 = 0.75
```

### Ví dụ với học viên SV01 và Khóa học A

```
A (SV01): Python=1, Pandas=1, Data Visualization=1
B (Course A): Python=1, Pandas=1, SQL=1, Data Visualization=1

A_active = {Python, Pandas, Data Visualization}
B_active = {Python, Pandas, SQL, Data Visualization}

Intersection = {Python, Pandas, Data Visualization} → 3
Union        = {Python, Pandas, SQL, Data Visualization} → 4

Score = 3/4 = 0.75
```

---

## 6. Pseudocode Python

```python
def jaccard_score(student_vector: dict, course_vector: dict) -> float:
    """
    Tính Jaccard Similarity giữa hai binary vector.
    
    Args:
        student_vector: dict {skill: 0 or 1} của học viên
        course_vector:  dict {skill: 0 or 1} của khóa học
    
    Returns:
        float: Jaccard score trong khoảng [0.0, 1.0]
    """
    student_active = {
        key for key, value in student_vector.items()
        if value == 1
    }

    course_active = {
        key for key, value in course_vector.items()
        if value == 1
    }

    union = student_active | course_active
    if not union:
        return 0.0

    intersection = student_active & course_active
    return len(intersection) / len(union)


def rank_courses(
    student_vector: dict,
    courses: list[dict]
) -> list[dict]:
    """
    Xếp hạng tất cả khóa học theo Jaccard score.
    
    Args:
        student_vector: binary vector của học viên
        courses: list of {id, title, binary_vector}
    
    Returns:
        list[dict] sorted by score descending, with rank assigned
    """
    import time
    
    results = []
    for course in courses:
        start = time.time()
        score = jaccard_score(student_vector, course["binary_vector"])
        elapsed_ms = (time.time() - start) * 1000
        
        student_active = {k for k, v in student_vector.items() if v == 1}
        course_active  = {k for k, v in course["binary_vector"].items() if v == 1}
        
        results.append({
            "course_id": course["id"],
            "course_title": course["title"],
            "match_score": round(score, 4),
            "matched_keywords": list(student_active & course_active),
            "student_keywords": list(student_active),
            "course_keywords": list(course_active),
            "processing_time_ms": round(elapsed_ms, 2),
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Assign ranks
    for i, result in enumerate(results):
        result["rank"] = i + 1
    
    return results
```

---

## 7. Ranking

Kết quả được xếp hạng theo `match_score` từ cao đến thấp:

| Rank | Course | Score |
|------|--------|-------|
| 1 | Python for Data Analysis | 0.75 |
| 2 | Data Science Fundamentals | 0.50 |
| 3 | Excel & Power BI | 0.25 |
| 4 | Web Development with React | 0.10 |

API trả về top-K (mặc định K=3) theo query param `?k=3`.

---

## 8. Match Result Example

**Tình huống:** SV01 muốn học Python, Pandas, Data Visualization.

**Khóa học trong hệ thống:**

| Khóa học | Kỹ năng dạy | Score vs SV01 |
|----------|------------|---------------|
| Python for Data Analysis | Python, Pandas, SQL, Data Viz | **0.75** |
| Data Science with ML | Python, Pandas, ML, Scikit-learn | **0.50** |
| Web Dev với React | React, JavaScript, HTML, CSS | **0.00** |

**Output từ `/matching/top/SV01_doc_id?k=3`:**

```json
{
  "results": [
    {
      "rank": 1,
      "course_title": "Python for Data Analysis",
      "match_score": 0.75,
      "matched_keywords": ["Python", "Pandas", "Data Visualization"]
    },
    {
      "rank": 2,
      "course_title": "Data Science with ML",
      "match_score": 0.50,
      "matched_keywords": ["Python", "Pandas"]
    },
    {
      "rank": 3,
      "course_title": "Web Dev với React",
      "match_score": 0.00,
      "matched_keywords": []
    }
  ]
}
```

---

## 9. Evaluation Metrics

### Top-1 Accuracy

```
Ý nghĩa: Tỷ lệ học viên mà khóa học dự đoán top-1 trùng với nhãn thật.

Công thức:
  Top-1 Accuracy = (số SV có top-1 predicted ∈ validated_course_ids)
                   / (tổng số SV có nhãn)

Ví dụ:
  15 học viên có nhãn, 11 người được dự đoán đúng top-1
  Top-1 Accuracy = 11 / 15 = 0.73 = 73%
```

### Hit Rate@3

```
Ý nghĩa: Tỷ lệ học viên có ít nhất 1 trong top-3 khóa học dự đoán
         trùng với nhãn thật.

Công thức:
  Hit Rate@3 = (số SV có ít nhất 1 trong top-3 ∈ validated_course_ids)
               / (tổng số SV có nhãn)

Ví dụ:
  15 học viên có nhãn, 13 người có nhãn đúng trong top-3
  Hit Rate@3 = 13 / 15 = 0.87 = 87%
```

### Average Processing Time

```
Ý nghĩa: Thời gian trung bình để tính Jaccard cho 1 cặp (student, course).

Công thức:
  Avg Time = mean(match_results.processing_time_ms)
```

---

## 10. Algorithm Limitations

| Limitation | Mô tả | Hướng cải thiện |
|------------|-------|-----------------|
| **Keyword matching chỉ dựa vào từ vựng** | "ML" và "Machine Learning" có thể không match | Synonym mapping |
| **Không xét trọng số từ khóa** | "Python" và "Communication" có trọng số bằng nhau | TF-IDF weighting |
| **SKILL_DICTIONARY cố định** | Thiếu từ khóa → không detect được | Mở rộng dictionary liên tục |
| **Không xét ngữ cảnh** | "Python" trong "not Python" vẫn tính là 1 | NLP context analysis |
| **Tốt nhất với tài liệu có từ khóa rõ ràng** | CV viết mơ hồ → vector thưa | Hướng dẫn học viên viết rõ kỹ năng |

**Phù hợp với đồ án vì:** Jaccard là thuật toán cơ bản, dễ implement, dễ giải thích, có thể đo lường được bằng Top-1 Accuracy và Hit Rate@3 – phù hợp với yêu cầu môn học.
