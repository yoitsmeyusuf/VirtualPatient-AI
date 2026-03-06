"""
auth.py — Google OAuth + JWT Kimlik Doğrulama
-------------------------------------------------
1. Frontend'den gelen Google ID token'ı doğrular.
2. Kullanıcı bilgisiyle JWT oluşturur.
3. Korumalı endpoint'ler için JWT doğrulama dependency'si sağlar.
4. DEV MODE: GOOGLE_CLIENT_ID boşsa geliştirici girişi aktif olur.
"""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings

# ── Bearer token scheme ──────────────────────────────────────────────
_bearer = HTTPBearer(auto_error=False)

# ── Dev mode kontrolü ────────────────────────────────────────────────
_DEV_MODE = not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == "YOUR_GOOGLE_CLIENT_ID_HERE"


# ═══════════════════════════════════════════════════════════════════════
# GOOGLE TOKEN DOĞRULAMA
# ═══════════════════════════════════════════════════════════════════════

async def verify_google_token(token: str) -> dict:
    """
    Google ID token'ı doğrular. Dev modda sahte kullanıcı döner.
    """
    # DEV MODE — Google Client ID ayarlanmamışsa
    if _DEV_MODE:
        return {
            "sub": "dev-user-001",
            "email": "dev@antrenman.ai",
            "name": "Geliştirici",
            "picture": "",
        }

    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as g_requests

        idinfo = id_token.verify_oauth2_token(
            token,
            g_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        return {
            "sub": idinfo["sub"],
            "email": idinfo.get("email", ""),
            "name": idinfo.get("name", ""),
            "picture": idinfo.get("picture", ""),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Geçersiz Google token: {exc}",
        )


# ═══════════════════════════════════════════════════════════════════════
# JWT OLUŞTURMA & DOĞRULAMA
# ═══════════════════════════════════════════════════════════════════════

def create_jwt(user_data: dict) -> str:
    """Kullanıcı bilgisiyle imzalı JWT oluşturur."""
    payload = {
        **user_data,
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=settings.JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_jwt(token: str) -> dict:
    """JWT'yi çözer ve payload döner."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token süresi dolmuş, tekrar giriş yapın.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz token.",
        )


# ═══════════════════════════════════════════════════════════════════════
# FASTAPI DEPENDENCY — Korumalı endpoint'ler için
# ═══════════════════════════════════════════════════════════════════════

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """
    Authorization header'dan JWT'yi çıkarır ve kullanıcıyı döner.
    Token yoksa veya geçersizse 401 fırlatır.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Giriş yapmanız gerekiyor.",
        )
    return decode_jwt(credentials.credentials)
