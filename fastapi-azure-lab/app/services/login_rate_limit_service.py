from time import monotonic
from threading import Lock

from fastapi import HTTPException, Request, status

from app.config import settings

_attempts_by_key: dict[str, list[float]] = {}
_lock = Lock()


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _key(email: str, request: Request) -> str:
    return f"{email.strip().lower()}|{_client_ip(request)}"


def _active_attempts(now: float, attempts: list[float]) -> list[float]:
    window_start = now - settings.login_rate_limit_window_seconds
    return [attempt for attempt in attempts if attempt >= window_start]


def ensure_login_allowed(email: str, request: Request) -> None:
    key = _key(email, request)
    now = monotonic()

    with _lock:
        attempts = _active_attempts(now, _attempts_by_key.get(key, []))
        _attempts_by_key[key] = attempts
        if len(attempts) >= settings.login_rate_limit_attempts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Dang nhap sai qua nhieu lan. Vui long thu lai sau.",
                headers={"Retry-After": str(settings.login_rate_limit_window_seconds)},
            )


def record_failed_login(email: str, request: Request) -> None:
    key = _key(email, request)
    now = monotonic()

    with _lock:
        attempts = _active_attempts(now, _attempts_by_key.get(key, []))
        attempts.append(now)
        _attempts_by_key[key] = attempts


def reset_login_attempts(email: str, request: Request) -> None:
    key = _key(email, request)
    with _lock:
        _attempts_by_key.pop(key, None)
