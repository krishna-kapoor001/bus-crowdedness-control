import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DTC Smart Occupancy System (DSOS)"
    API_V1_STR: str = "/api/v1"
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    PROCESSED_DATA_DIR: str = os.path.join(BASE_DIR, "data", "processed")
    RAW_DATA_DIR: str = os.path.join(BASE_DIR, "data", "raw")
    MODELS_DIR: str = os.path.join(BASE_DIR, "models_artifacts")

    # High-Concurrency Settings
    CACHE_MAX_SIZE: int = 32768
    CACHE_TTL_SECONDS: int = 300
    ENABLE_IN_MEMORY_PRECOMPUTE: bool = True
    ENABLE_GZIP_COMPRESSION: bool = True
    GZIP_MIN_SIZE: int = 512

    # Database URL: Auto-detect busroute.db or flowpulse.db, or custom Postgres
    @property
    def DATABASE_URL(self) -> str:
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        busroute_db = os.path.join(self.DATA_DIR, "busroute.db")
        if os.path.exists(busroute_db):
            return f"sqlite:///{busroute_db}"
        return f"sqlite:///{os.path.join(self.DATA_DIR, 'flowpulse.db')}"

    class Config:
        case_sensitive = True

settings = Settings()
