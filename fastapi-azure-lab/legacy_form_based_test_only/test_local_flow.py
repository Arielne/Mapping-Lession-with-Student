import os
import sys
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = os.getenv("COURSEMATCH_BASE_URL", "http://127.0.0.1:8000")
STUDENT_EMAIL = "student.demo@coursematch.local"
STUDENT_PASSWORD = os.getenv("STUDENT_DEMO_PASSWORD", "StudentDemo@123")
TIMEOUT_SECONDS = 10


def print_result(name: str, status: str, detail: str = "") -> None:
    suffix = f" - {detail}" if detail else ""
    print(f"{name}: {status}{suffix}")


class Response:
    def __init__(self, status_code: int):
        self.status_code = status_code


def request_json(method: str, path: str, headers: dict | None = None, json_body=None):
    request_headers = {"Accept": "application/json", **(headers or {})}
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    request = Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=request_headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw_body = response.read().decode("utf-8")
            body = json.loads(raw_body) if raw_body else None
            return Response(response.status), body
    except HTTPError as exc:
        raw_body = exc.read().decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else None
        except ValueError:
            body = None
        return Response(exc.code), body


def main() -> int:
    passed = True
    register_ok = False

    register_payload = {
        "full_name": "Student Demo",
        "email": STUDENT_EMAIL,
        "password": STUDENT_PASSWORD,
    }
    response, _ = request_json("POST", "/auth/register", json_body=register_payload)
    if response.status_code == 201:
        register_ok = True
    elif response.status_code == 409:
        register_ok = True
    else:
        passed = False

    response, login_body = request_json(
        "POST",
        "/auth/login",
        json_body={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD},
    )
    token = login_body.get("access_token") if isinstance(login_body, dict) else None
    if register_ok and response.status_code == 200 and token:
        print_result("student register/login", "pass")
    else:
        print_result("student register/login", "fail", f"HTTP {response.status_code}")
        return 1

    headers = {"Authorization": f"Bearer {token}"}

    response, me_body = request_json("GET", "/auth/me", headers=headers)
    if response.status_code == 200 and me_body.get("role") == "student":
        print_result("student auth/me", "pass")
    else:
        print_result("student auth/me", "fail", f"HTTP {response.status_code}")
        passed = False

    response, _ = request_json(
        "POST",
        "/courses",
        headers=headers,
        json_body={
            "title": "Forbidden Student Course",
            "category": "Database",
            "level": "Beginner",
            "skills": ["MongoDB"],
            "description": "This should not be created by a student.",
            "duration_weeks": 1,
            "is_active": True,
        },
    )
    if response.status_code == 403:
        print_result("student forbidden create course", "pass")
    else:
        print_result(
            "student forbidden create course",
            "fail",
            f"expected HTTP 403, got {response.status_code}",
        )
        passed = False

    need_payload = {
        "desired_category": "Data Analysis",
        "current_level": "Beginner",
        "desired_skills": ["Python", "Pandas", "Data Visualization"],
        "learning_goal": "Hoc phan tich du lieu bang Python",
    }
    response, need_body = request_json(
        "POST",
        "/learning-needs",
        headers=headers,
        json_body=need_payload,
    )
    need_id = need_body.get("id") if isinstance(need_body, dict) else None
    if response.status_code == 201 and need_id:
        print_result("create learning need", "pass")
    else:
        print_result("create learning need", "fail", f"HTTP {response.status_code}")
        return 1

    response, recommendations = request_json(
        "GET",
        f"/recommendations/{need_id}",
        headers=headers,
    )
    has_recommendation = (
        response.status_code == 200
        and isinstance(recommendations, list)
        and len(recommendations) > 0
        and all(
            "match_score" in recommendation and "matched_skills" in recommendation
            for recommendation in recommendations
        )
    )
    if has_recommendation:
        print_result("recommendations", "pass", f"{len(recommendations)} results")
    else:
        print_result("recommendations", "fail", f"HTTP {response.status_code}")
        return 1

    course_id = recommendations[0]["course"]["id"]
    response, _ = request_json(
        "POST",
        "/registrations",
        headers=headers,
        json_body={"course_id": course_id},
    )
    if response.status_code == 201:
        print_result("registration", "pass")
    elif response.status_code == 409:
        print_result("registration", "already exists")
    else:
        print_result("registration", "fail", f"HTTP {response.status_code}")
        passed = False

    response, registrations = request_json("GET", "/registrations/me", headers=headers)
    if response.status_code == 200 and isinstance(registrations, list) and registrations:
        print_result("get my registrations", "pass")
    else:
        print_result("get my registrations", "fail", f"HTTP {response.status_code}")
        passed = False

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
