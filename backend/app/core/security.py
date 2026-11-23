import hashlib
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings

# Standard Argon2id configuration (OWASP recommended parameters)
_hasher = PasswordHasher(
    time_cost=3,        # Iterations
    memory_cost=65536,  # 64 MB RAM
    parallelism=4,      # Threads
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Hashes a plaintext password using Argon2id with random salt."""
    return _hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against the stored Argon2id hash."""
    try:
        return _hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def hash_token(token: str) -> str:
    """Computes a SHA-256 digest of a refresh token for secure database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def generate_secure_token() -> str:
    """Generates a cryptographically secure random token string."""
    return secrets.token_urlsafe(32)
def create_access_token(
    subject: str,
    role: str = "user",
    expires_delta: timedelta = None,
) -> str:
    """Creates a cryptographically signed JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
def decode_access_token(token: str) -> dict:
    """Decodes and validates a JWT access token. Raises jwt.PyJWTError if invalid."""
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )