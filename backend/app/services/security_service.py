from pwdlib import PasswordHash


# Create password hashing instance using Argon2
password_hash = PasswordHash.recommended()


# Hash a plain-text password
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# Verify a password against its stored hash
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )