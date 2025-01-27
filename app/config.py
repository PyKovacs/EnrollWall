from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "enrollwall_", "env_file": ".env"}

    # HASH_SECRET_KEY: str
    # HASH_ALGORITHM: str
    DB_URL: str = "sqlite:///./enrollwall.db"
