from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.erro import ErrorResponse, ValidationErrorResponse
from app.security.jwt import create_access_token
from app.security.passwords import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description=(
        "Endpoint público que autentica `username` e `password`, sem exigir um "
        "JWT anterior. Os dois campos são obrigatórios, o corpo segue "
        "`LoginRequest` e campos extras são rejeitados. Credenciais válidas "
        "retornam um access token com `token_type=\"bearer\"`, que pode ser usado "
        "nas rotas protegidas conforme as permissões do usuário. Usuário "
        "inexistente e senha incorreta retornam a mesma resposta genérica, sem "
        "revelar qual credencial falhou."
    ),
    responses={
        200: {
            "model": TokenResponse,
            "description": "Autenticação concluída; o token do exemplo é sintético e não utilizável.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "jwt-exemplo-nao-utilizavel",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "model": ErrorResponse,
            "description": (
                "Usuário inexistente ou senha incorreta. A mensagem é idêntica "
                "nos dois casos."
            ),
            "headers": {
                "WWW-Authenticate": {
                    "description": "Esquema indicado pela resposta de autenticação recusada.",
                    "schema": {"type": "string", "example": "Bearer"}
                }
            },
            "content": {
                "application/json": {
                    "example": {
                        "status": 401,
                        "error": "unauthorized",
                        "message": "Credenciais inválidas.",
                        "details": None
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "Corpo ausente ou incompatível com LoginRequest.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 422,
                        "error": "validation_error",
                        "message": "Dados de entrada inválidos.",
                        "details": [
                            {
                                "loc": ["body", "extra"],
                                "msg": "Extra inputs are not permitted",
                                "type": "extra_forbidden"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "model": ErrorResponse,
            "description": (
                "Falha interna inesperada, inclusive uma eventual falha de "
                "verificação criptográfica não convertida em 401."
            ),
            "content": {
                "application/json": {
                    "example": {
                        "status": 500,
                        "error": "internal_error",
                        "message": "Erro interno do servidor.",
                        "details": None
                    }
                }
            }
        },
    },
)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Autentica um usuário e retorna um JWT access token."""
    usuario = db.scalar(select(Usuario).where(Usuario.username == request.username))

    exception_unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not usuario:
        raise exception_unauthorized

    if not verify_password(request.password, usuario.password_hash):
        raise exception_unauthorized

    access_token = create_access_token(subject=usuario.username)

    return TokenResponse(access_token=access_token)
