import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    app_name: str = "CourseMatch Document Matching API"
    app_env: str = (os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or "development").lower()
    mongodb_url: str | None = os.getenv("MONGODB_URL")
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME") or os.getenv("DB_NAME", "coursematch_document_db")
    jwt_secret_key: str | None = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM") or os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    frontend_url: str | None = os.getenv("FRONTEND_URL")
    allowed_origins: str | None = os.getenv("ALLOWED_ORIGINS")
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    matching_max_features: int = int(os.getenv("MATCHING_MAX_FEATURES", "500"))

    @property
    def is_production(self) -> bool:
        return self.app_env in {"production", "prod", "azure"} or bool(os.getenv("WEBSITE_SITE_NAME"))


settings = Settings()
