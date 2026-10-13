from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.erro import ErrorResponse, ValidationErrorResponse
from app.models.usuario import Usuario
from app.security.passwords import verify_password
from app.security.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        422: {"model": ValidationErrorResponse, "description": "Erro de validação."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica um usuário e retorna um JWT access token.
    """
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
