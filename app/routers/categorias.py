from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from app.schemas.erro import ErrorResponse, ValidationErrorResponse
from app.security.auth import require_roles
from app.models.usuario import Role

router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"]
)

@router.post(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        403: {"model": ErrorResponse, "description": "Você não possui permissão para executar esta operação."},
        409: {"model": ErrorResponse, "description": "Categoria já existe com este nome."},
        422: {"model": ValidationErrorResponse, "description": "Erro de validação."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def criar_categoria(categoria_in: CategoriaCreate, db: Session = Depends(get_db)):
    nova_categoria = Categoria(nome=categoria_in.nome)
    db.add(nova_categoria)
    try:
        db.commit()
        db.refresh(nova_categoria)
        return nova_categoria
    except IntegrityError as e:
        db.rollback()
        # Verificar o SQLSTATE original do driver psycopg
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma categoria com este nome."
            )
        # Se for outro IntegrityError não previsto, repassa
        raise e

@router.get(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=List[CategoriaResponse],
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def listar_categorias(db: Session = Depends(get_db)):
    stmt = select(Categoria).order_by(Categoria.id)
    resultado = db.scalars(stmt).all()
    return resultado

@router.get(
    "/{categoria_id}",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=CategoriaResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        404: {"model": ErrorResponse, "description": "Categoria não encontrada."},
        422: {"model": ValidationErrorResponse, "description": "Parâmetro inválido."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def buscar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada."
        )
    return categoria

@router.put(
    "/{categoria_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=CategoriaResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        403: {"model": ErrorResponse, "description": "Você não possui permissão para executar esta operação."},
        404: {"model": ErrorResponse, "description": "Categoria não encontrada."},
        409: {"model": ErrorResponse, "description": "Conflito de nome duplicado."},
        422: {"model": ValidationErrorResponse, "description": "Erro de validação."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def atualizar_categoria(categoria_id: int, categoria_in: CategoriaUpdate, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada."
        )
    
    categoria.nome = categoria_in.nome
    try:
        db.commit()
        db.refresh(categoria)
        return categoria
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma categoria com este nome."
            )
        raise e

@router.delete(
    "/{categoria_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        403: {"model": ErrorResponse, "description": "Você não possui permissão para executar esta operação."},
        404: {"model": ErrorResponse, "description": "Categoria não encontrada."},
        409: {"model": ErrorResponse, "description": "A categoria não pode ser removida pois possui produtos relacionados."},
        422: {"model": ValidationErrorResponse, "description": "Parâmetro inválido."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def excluir_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada."
        )
    
    try:
        from sqlalchemy import delete
        stmt = delete(Categoria).where(Categoria.id == categoria_id)
        db.execute(stmt)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23503":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A categoria não pode ser removida pois possui produtos relacionados."
            )
        raise e
