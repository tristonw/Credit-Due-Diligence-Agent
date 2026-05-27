from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-4-7"
    database_url: str = "sqlite:///./digital_employee.db"

    # High-level promotions (>= this level) require human expert approval.
    expert_approval_level: int = 5
    # Experience curve: needed(level) = base * level ** exponent
    exp_base: int = 100
    exp_exponent: float = 1.6


settings = Settings()
