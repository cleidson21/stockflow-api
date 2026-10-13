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
from app.schemas.erro import ErrorResponse, ValidationErrorResponse
from app.security.auth import require_roles
from app.models.usuario import Role

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

@router.post(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        403: {"model": ErrorResponse, "description": "Você não possui permissão para executar esta operação."},
        404: {"model": ErrorResponse, "description": "Categoria ou Fornecedor não encontrado."},
        409: {"model": ErrorResponse, "description": "Já existe um produto com este SKU ou falha de concorrência com FK."},
        422: {"model": ValidationErrorResponse, "description": "Erro de validação."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
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
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe um produto com este SKU."
                )
            elif e.orig.sqlstate == "23503":
                # Condição de corrida onde categoria ou fornecedor foi apagado concorrentemente
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Referência inválida para categoria ou fornecedor."
                )
        raise e

@router.get(
    "/consultas/estoque-minimo",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=List[ProdutoResponse],
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def listar_produtos_estoque_minimo(db: Session = Depends(get_db)):
    stmt = select(Produto).where(Produto.quantidade_em_estoque <= Produto.estoque_minimo).order_by(Produto.id)
    return db.scalars(stmt).all()

@router.get(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=List[ProdutoResponse],
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def listar_produtos(db: Session = Depends(get_db)):
    stmt = select(Produto).order_by(Produto.id)
    return db.scalars(stmt).all()

@router.get(
    "/{produto_id}",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=ProdutoResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        404: {"model": ErrorResponse, "description": "Produto não encontrado."},
        422: {"model": ValidationErrorResponse, "description": "Parâmetro inválido."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    return produto

@router.put(
    "/{produto_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=ProdutoResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        403: {"model": ErrorResponse, "description": "Você não possui permissão para executar esta operação."},
        404: {"model": ErrorResponse, "description": "Produto, Categoria ou Fornecedor não encontrado."},
        409: {"model": ErrorResponse, "description": "Conflito de SKU duplicado ou falha de concorrência."},
        422: {"model": ValidationErrorResponse, "description": "Erro de validação."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
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
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe um produto com este SKU."
                )
            elif e.orig.sqlstate == "23503":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Referência inválida para categoria ou fornecedor."
                )
        raise e

@router.delete(
    "/{produto_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        403: {"model": ErrorResponse, "description": "Você não possui permissão para executar esta operação."},
        404: {"model": ErrorResponse, "description": "Produto não encontrado."},
        409: {"model": ErrorResponse, "description": "O produto não pode ser removido pois possui movimentações relacionadas."},
        422: {"model": ValidationErrorResponse, "description": "Parâmetro inválido."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    
    try:
        from sqlalchemy import delete
        stmt = delete(Produto).where(Produto.id == produto_id)
        db.execute(stmt)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23503":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="O produto não pode ser removido pois possui movimentações relacionadas."
            )
        raise e
