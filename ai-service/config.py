"""
config.py — Ortam Değişkenleri Yönetimi
-----------------------------------------
.env dosyasından proje yapılandırmasını yükler.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını oku
load_dotenv(Path(__file__).parent / ".env")


class Settings:
    """Uygulama genelinde kullanılan yapılandırma sabitleri."""

    # ── OpenAI API ───────────────────────────────────────────────────
    EXTERNAL_API_KEY: str = os.getenv("EXTERNAL_API_KEY", "")
    EXTERNAL_API_BASE_URL: str = os.getenv(
        "EXTERNAL_API_BASE_URL", "https://api.openai.com/v1"
    )
    EXTERNAL_MODEL_NAME: str = os.getenv("EXTERNAL_MODEL_NAME", "gpt-4o-mini")

    # ── Google OAuth ─────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")

    # ── JWT ──────────────────────────────────────────────────────────
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-secret-in-production")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

    # ── Sunucu ───────────────────────────────────────────────────────
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))


settings = Settings()
