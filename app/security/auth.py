from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.security.jwt import decode_access_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> Usuario:
    exception_unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise exception_unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
        username: str | None = payload.get("sub")
        if username is None:
            raise exception_unauthorized
    except jwt.ExpiredSignatureError:
        raise exception_unauthorized
    except jwt.InvalidTokenError:
        raise exception_unauthorized

    # O papel vem do banco a cada requisição, permitindo aplicar mudanças de acesso.
    # A sessão é compartilhada: commits cabem aos endpoints; get_db fecha a sessão.
    usuario = db.scalar(select(Usuario).where(Usuario.username == username))

    if usuario is None:
        raise exception_unauthorized

    return usuario


def require_roles(*allowed_roles: str) -> Callable[[Usuario], Usuario]:
    def role_checker(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para executar esta operação.",
            )
        return current_user
    return role_checker
