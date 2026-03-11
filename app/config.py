import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_base_url: str
    app_id: str
    client_secret: str
    nuvemshop_auth_url: str
    nuvemshop_token_url: str
    db_path: str
    default_coupon_param: str


def _read_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def load_settings() -> Settings:
    app_id = _read_required_env("NUVEMSHOP_APP_ID")
    client_secret = _read_required_env("NUVEMSHOP_CLIENT_SECRET")

    return Settings(
        app_base_url=os.getenv("APP_BASE_URL", "http://localhost:5000").rstrip("/"),
        app_id=app_id,
        client_secret=client_secret,
        nuvemshop_auth_url=os.getenv(
            "NUVEMSHOP_AUTH_URL",
            "https://www.nuvemshop.com.br/apps/authorize",
        ),
        nuvemshop_token_url=os.getenv(
            "NUVEMSHOP_TOKEN_URL",
            "https://www.nuvemshop.com.br/apps/token",
        ),
        db_path=os.getenv("DATABASE_PATH", "instance/app.sqlite3"),
        default_coupon_param=os.getenv("DEFAULT_COUPON_PARAM", "coupon"),
    )
