import getpass
import os
import sys
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = os.getenv("COURSEMATCH_BASE_URL", "http://127.0.0.1:8000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@coursematch.local")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
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
    except URLError as exc:
        raise RuntimeError(
            f"Khong ket noi duoc API tai {BASE_URL}. "
            "Hay chay server: .\\.venv\\Scripts\\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"
        ) from exc


def main() -> int:
    password = ADMIN_PASSWORD or getpass.getpass("Admin password: ")
    response, login_body = request_json(
        "POST",
        "/auth/login",
        json_body={"email": ADMIN_EMAIL, "password": password},
    )
    token = login_body.get("access_token") if isinstance(login_body, dict) else None
    if response.status_code == 200 and token:
        print_result("admin login", "pass")
    else:
        print_result("admin login", "fail", f"HTTP {response.status_code}")
        return 1

    headers = {"Authorization": f"Bearer {token}"}

    response, me_body = request_json("GET", "/auth/me", headers=headers)
    if response.status_code == 200 and me_body.get("role") == "admin":
        print_result("admin auth/me", "pass")
    else:
        print_result("admin auth/me", "fail", f"HTTP {response.status_code}")
        return 1

    create_payload = {
        "title": "MongoDB for Beginners",
        "category": "Database",
        "level": "Beginner",
        "skills": ["MongoDB", "NoSQL"],
        "description": "Khoa hoc MongoDB danh cho nguoi moi",
        "duration_weeks": 6,
        "is_active": True,
    }
    response, course = request_json("POST", "/courses", headers=headers, json_body=create_payload)
    course_id = course.get("id") if isinstance(course, dict) else None
    if response.status_code == 201 and course_id:
        print_result("admin create course", "pass")
    else:
        print_result("admin create course", "fail", f"HTTP {response.status_code}")
        return 1

    response, updated = request_json(
        "PUT",
        f"/courses/{course_id}",
        headers=headers,
        json_body={"duration_weeks": 7},
    )
    if response.status_code == 200 and updated.get("duration_weeks") == 7:
        print_result("admin update course", "pass")
    else:
        print_result("admin update course", "fail", f"HTTP {response.status_code}")
        return 1

    response, _ = request_json("DELETE", f"/courses/{course_id}", headers=headers)
    if response.status_code == 200:
        print_result("admin delete course", "pass")
    else:
        print_result("admin delete course", "fail", f"HTTP {response.status_code}")
        return 1

    response, active_courses = request_json("GET", "/courses")
    active_ids = {course["id"] for course in active_courses} if isinstance(active_courses, list) else set()
    if response.status_code == 200 and course_id not in active_ids:
        print_result("soft delete hidden from public list", "pass")
    else:
        print_result("soft delete hidden from public list", "fail", f"HTTP {response.status_code}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
