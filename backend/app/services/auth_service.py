"""Password hashing utilities."""

import hashlib

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# bcrypt has a 72-byte limit; pre-hash with SHA256 to support any password length


def _prehash_for_bcrypt(password: str) -> str:
    """Pre-hash password so bcrypt input stays under 72 bytes."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    """Hash a plain password (supports any length)."""
    return pwd_context.hash(_prehash_for_bcrypt(password))


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a hash."""
    return pwd_context.verify(_prehash_for_bcrypt(plain), hashed)
