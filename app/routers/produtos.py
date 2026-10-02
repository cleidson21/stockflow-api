from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models.fornecedor import Fornecedor
from app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutoResponse

router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)

def validar_relacionamentos(db: Session, categoria_id: int, fornecedor_id: int):
    if not db.get(Categoria, categoria_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada."
        )
    if not db.get(Fornecedor, fornecedor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )

@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(produto_in: ProdutoCreate, db: Session = Depends(get_db)):
    validar_relacionamentos(db, produto_in.categoria_id, produto_in.fornecedor_id)
    
    novo_produto = Produto(
        nome=produto_in.nome,
        sku=produto_in.sku,
        preco_custo=produto_in.preco_custo,
        preco_venda=produto_in.preco_venda,
        estoque_minimo=produto_in.estoque_minimo,
        categoria_id=produto_in.categoria_id,
        fornecedor_id=produto_in.fornecedor_id
    )
    
    db.add(novo_produto)
    try:
        db.commit()
        db.refresh(novo_produto)
        return novo_produto
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate"):
            if e.orig.sqlstate == "23505":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um produto com este SKU."
                )
            elif e.orig.sqlstate == "23503":
                # Condição de corrida onde categoria ou fornecedor foi apagado concorrentemente
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Referência inválida para categoria ou fornecedor."
                )
        raise e

@router.get("/consultas/estoque-minimo", response_model=List[ProdutoResponse])
def listar_produtos_estoque_minimo(db: Session = Depends(get_db)):
    stmt = select(Produto).where(Produto.quantidade_em_estoque <= Produto.estoque_minimo).order_by(Produto.id)
    return db.scalars(stmt).all()

@router.get("", response_model=List[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    stmt = select(Produto).order_by(Produto.id)
    return db.scalars(stmt).all()

@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    return produto

@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(produto_id: int, produto_in: ProdutoUpdate, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    
    validar_relacionamentos(db, produto_in.categoria_id, produto_in.fornecedor_id)
    
    produto.nome = produto_in.nome
    produto.sku = produto_in.sku
    produto.preco_custo = produto_in.preco_custo
    produto.preco_venda = produto_in.preco_venda
    produto.estoque_minimo = produto_in.estoque_minimo
    produto.categoria_id = produto_in.categoria_id
    produto.fornecedor_id = produto_in.fornecedor_id
    
    try:
        db.commit()
        db.refresh(produto)
        return produto
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate"):
            if e.orig.sqlstate == "23505":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um produto com este SKU."
                )
            elif e.orig.sqlstate == "23503":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Referência inválida para categoria ou fornecedor."
                )
        raise e

@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    
    try:
        db.delete(produto)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23503":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O produto não pode ser removido pois possui movimentações relacionadas."
            )
        raise e
