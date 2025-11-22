from __future__ import annotations

import bcrypt

_BCRYPT_PREFIXES = (b"$2a$", b"$2b$", b"$2y$")


def is_bcrypt_hash(value: str | None) -> bool:
    """Return True if *value* looks like a bcrypt hash string."""
    if not value:
        return False
    try:
        raw = value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return raw.startswith(_BCRYPT_PREFIXES)


def hash_password(password: str) -> str:
    """Hash *password* using bcrypt and return the encoded hash string."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str | None) -> bool:
    """Verify *password* against a stored bcrypt *password_hash*."""
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Raised if the stored hash is not a valid bcrypt hash
        return False
