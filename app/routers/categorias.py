from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse

router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"]
)

@router.post("", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma categoria com este nome."
            )
        # Se for outro IntegrityError não previsto, repassa
        raise e

@router.get("", response_model=List[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    stmt = select(Categoria).order_by(Categoria.id)
    resultado = db.scalars(stmt).all()
    return resultado

@router.get("/{categoria_id}", response_model=CategoriaResponse)
def buscar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada."
        )
    return categoria

@router.put("/{categoria_id}", response_model=CategoriaResponse)
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma categoria com este nome."
            )
        raise e

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada."
        )
    
    try:
        db.delete(categoria)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23503":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A categoria não pode ser removida pois possui produtos relacionados."
            )
        raise e
