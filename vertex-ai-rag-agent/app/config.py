"""Environment-driven settings. No secrets in code; everything comes from env vars."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # GCP / Vertex AI
    gcp_project: str
    gcp_region: str = "us-central1"
    gemini_model: str = "gemini-2.0-flash-001"
    embedding_model: str = "text-embedding-005"

    # Cloud SQL (private IP via Cloud SQL connector or VPC connector on Cloud Run)
    db_host: str = "127.0.0.1"  # Cloud SQL Auth Proxy / connector sidecar in prod
    db_port: int = 5432
    db_name: str = "rag"
    db_user: str = "rag_app"
    db_password: str = ""  # injected from Secret Manager at deploy time

    # Retrieval / generation limits
    top_k: int = 5
    embedding_dims: int = 768
    max_output_tokens: int = 512
    temperature: float = 0.2

    # Ingestion
    chunk_size: int = 1000  # characters
    chunk_overlap: int = 200

    @property
    def db_dsn(self) -> str:
        return (
            f"host={self.db_host} port={self.db_port} dbname={self.db_name} "
            f"user={self.db_user} password={self.db_password}"
        )


settings = Settings()
