from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import field_validator

class Settings(BaseSettings):
    DATABASE_URL: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Auth settings
    SECRET_KEY: str
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # Storage settings
    STORAGE_PROVIDER: str = "local"
    CORS_ORIGINS: str = ""
    CLAIM_UPLOAD_DIR: str = "storage/claims"
    IDENTITY_DOCUMENT_UPLOAD_DIR: str = "storage/identity-documents"
    S3_BUCKET_NAME: str | None = None
    S3_REGION: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    S3_ENDPOINT_URL: str | None = None
    S3_PUBLIC_URL: str | None = None
    S3_FORCE_PATH_STYLE: bool = False


    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()  # type: ignore[call-arg]

