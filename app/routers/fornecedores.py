from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.fornecedor import Fornecedor
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate, FornecedorResponse

router = APIRouter(
    prefix="/fornecedores",
    tags=["Fornecedores"]
)

@router.post("", response_model=FornecedorResponse, status_code=status.HTTP_201_CREATED)
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=mensagem
            )
        raise e

@router.get("", response_model=List[FornecedorResponse])
def listar_fornecedores(db: Session = Depends(get_db)):
    stmt = select(Fornecedor).order_by(Fornecedor.id)
    return db.scalars(stmt).all()

@router.get("/{fornecedor_id}", response_model=FornecedorResponse)
def buscar_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )
    return fornecedor

@router.put("/{fornecedor_id}", response_model=FornecedorResponse)
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=mensagem
            )
        raise e

@router.delete("/{fornecedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )
    
    try:
        db.delete(fornecedor)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23503":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O fornecedor não pode ser removido pois possui registros relacionados."
            )
        raise e
