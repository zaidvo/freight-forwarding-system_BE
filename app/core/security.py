import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status

from app.core.config import settings


JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"pbkdf2_sha256$100000${salt}${password_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, stored_hash = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False

        candidate_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
        return hmac.compare_digest(candidate_hash.hex(), stored_hash)
    except ValueError:
        return False


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_password_reset_token() -> str:
    return secrets.token_urlsafe(32)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expires_at = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": subject, "exp": int(expires_at.timestamp())}
    return _encode_jwt(payload)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
        signing_input = f"{header_segment}.{payload_segment}".encode()
        expected_signature = _sign(signing_input)

        if not hmac.compare_digest(_base64url_decode(signature_segment), expected_signature):
            raise ValueError("Invalid token signature")

        payload = json.loads(_base64url_decode(payload_segment))
        if int(payload["exp"]) < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("Token expired")

        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def _encode_jwt(payload: dict[str, Any]) -> str:
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_segment = _base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_segment = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signature_segment = _base64url_encode(_sign(f"{header_segment}.{payload_segment}".encode()))
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def _sign(value: bytes) -> bytes:
    return hmac.new(settings.jwt_secret_key.encode(), value, hashlib.sha256).digest()


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
