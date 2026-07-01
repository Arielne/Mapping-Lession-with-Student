from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import get_database
from app.security import decode_access_token
from app.utils import to_object_id

bearer_scheme = HTTPBearer(auto_error=False)


def require_database():
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database chua san sang. Hay cau hinh MONGODB_URL va kiem tra ket noi.",
        )
    return db


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db=Depends(require_database),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thieu access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token thieu user id.")

    user = await db.users.find_one({"_id": to_object_id(user_id)})
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nguoi dung khong ton tai.")
    return user


async def require_admin(current_user=Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chi admin moi duoc thuc hien.")
    return current_user


async def require_student(current_user=Depends(get_current_user)):
    if current_user.get("role") not in {"user", "student"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chi user/hoc vien moi duoc thuc hien.")
    return current_user
