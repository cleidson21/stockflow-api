from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.fornecedor import Fornecedor
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate, FornecedorResponse
from app.schemas.erro import ErrorResponse, ValidationErrorResponse
from app.security.auth import require_roles
from app.models.usuario import Role

router = APIRouter(
    prefix="/fornecedores",
    tags=["Fornecedores"]
)

@router.post(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=FornecedorResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        403: {"model": ErrorResponse, "description": "Você não possui permissão para executar esta operação."},
        409: {"model": ErrorResponse, "description": "CNPJ ou email já cadastrado."},
        422: {"model": ValidationErrorResponse, "description": "Erro de validação."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def criar_fornecedor(fornecedor_in: FornecedorCreate, db: Session = Depends(get_db)):
    novo_fornecedor = Fornecedor(
        nome=fornecedor_in.nome,
        cnpj=fornecedor_in.cnpj,
        telefone=fornecedor_in.telefone,
        email=fornecedor_in.email
    )
    db.add(novo_fornecedor)
    try:
        db.commit()
        db.refresh(novo_fornecedor)
        return novo_fornecedor
    except IntegrityError as e:
        db.rollback()
        # Verificar o SQLSTATE
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
            diag = getattr(e.orig, "diag", None)
            constraint_name = getattr(diag, "constraint_name", "") if diag else ""
            
            if "cnpj" in constraint_name:
                mensagem = "Já existe um fornecedor com este CNPJ."
            elif "email" in constraint_name:
                mensagem = "Já existe um fornecedor com este email."
            else:
                mensagem = "CNPJ ou email já cadastrado."
                
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=mensagem
            )
        raise e

@router.get(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=List[FornecedorResponse],
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def listar_fornecedores(db: Session = Depends(get_db)):
    stmt = select(Fornecedor).order_by(Fornecedor.id)
    return db.scalars(stmt).all()

@router.get(
    "/{fornecedor_id}",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=FornecedorResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        404: {"model": ErrorResponse, "description": "Fornecedor não encontrado."},
        422: {"model": ValidationErrorResponse, "description": "Parâmetro inválido."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def buscar_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )
    return fornecedor

@router.put(
    "/{fornecedor_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=FornecedorResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        403: {"model": ErrorResponse, "description": "Você não possui permissão para executar esta operação."},
        404: {"model": ErrorResponse, "description": "Fornecedor não encontrado."},
        409: {"model": ErrorResponse, "description": "CNPJ ou email já cadastrado."},
        422: {"model": ValidationErrorResponse, "description": "Erro de validação."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def atualizar_fornecedor(fornecedor_id: int, fornecedor_in: FornecedorUpdate, db: Session = Depends(get_db)):
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )
    
    fornecedor.nome = fornecedor_in.nome
    fornecedor.cnpj = fornecedor_in.cnpj
    fornecedor.telefone = fornecedor_in.telefone
    fornecedor.email = fornecedor_in.email
    
    try:
        db.commit()
        db.refresh(fornecedor)
        return fornecedor
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
            diag = getattr(e.orig, "diag", None)
            constraint_name = getattr(diag, "constraint_name", "") if diag else ""
            
            if "cnpj" in constraint_name:
                mensagem = "Já existe um fornecedor com este CNPJ."
            elif "email" in constraint_name:
                mensagem = "Já existe um fornecedor com este email."
            else:
                mensagem = "CNPJ ou email já cadastrado."
                
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=mensagem
            )
        raise e

@router.delete(
    "/{fornecedor_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        403: {"model": ErrorResponse, "description": "Você não possui permissão para executar esta operação."},
        404: {"model": ErrorResponse, "description": "Fornecedor não encontrado."},
        409: {"model": ErrorResponse, "description": "O fornecedor não pode ser removido pois possui registros relacionados."},
        422: {"model": ValidationErrorResponse, "description": "Parâmetro inválido."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def excluir_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )
    
    try:
        from sqlalchemy import delete
        stmt = delete(Fornecedor).where(Fornecedor.id == fornecedor_id)
        db.execute(stmt)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23503":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="O fornecedor não pode ser removido pois possui registros relacionados."
            )
        raise e
