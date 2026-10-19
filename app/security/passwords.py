from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

password_hash = PasswordHash((Argon2Hasher(),))


def hash_password(password: str) -> str:
    """Gera um hash Argon2 com salt aleatório, sem aplicar política de senha."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica a senha; hashes não reconhecidos geram UnknownHashError."""
    return password_hash.verify(password, hashed_password)
