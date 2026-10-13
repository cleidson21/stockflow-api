from typing import List, Optional
from pydantic import AwareDatetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.produto import Produto
from app.models.movimentacao import MovimentacaoEstoque
from app.models.fornecedor import Fornecedor
from app.schemas.movimentacao import MovimentacaoCreate, MovimentacaoResponse, TipoMovimentacao
from app.schemas.erro import ErrorResponse, ValidationErrorResponse
from app.security.auth import require_roles
from app.models.usuario import Role

router = APIRouter(
    prefix="/movimentacoes",
    tags=["Movimentações"]
)

@router.post(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=MovimentacaoResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        404: {"model": ErrorResponse, "description": "Produto não encontrado."},
        409: {"model": ErrorResponse, "description": "Estoque insuficiente para a saída solicitada."},
        422: {"model": ValidationErrorResponse, "description": "Erro de validação."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def criar_movimentacao(mov_in: MovimentacaoCreate, db: Session = Depends(get_db)):
    try:
        stmt = select(Produto).where(Produto.id == mov_in.produto_id).with_for_update()
        produto = db.scalars(stmt).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado."
            )
        
        if mov_in.tipo == TipoMovimentacao.ENTRADA:
            produto.quantidade_em_estoque += mov_in.quantidade
        elif mov_in.tipo == TipoMovimentacao.SAIDA:
            if mov_in.quantidade > produto.quantidade_em_estoque:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Estoque insuficiente para a saída solicitada."
                )
            produto.quantidade_em_estoque -= mov_in.quantidade
            
        nova_movimentacao = MovimentacaoEstoque(
            tipo=mov_in.tipo.value,
            quantidade=mov_in.quantidade,
            produto_id=produto.id,
            fornecedor_id=produto.fornecedor_id
        )
        db.add(nova_movimentacao)
        db.commit()
        
        db.refresh(nova_movimentacao)
        return nova_movimentacao
    except IntegrityError as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise e




@router.get(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=List[MovimentacaoResponse],
    responses={
        400: {"model": ErrorResponse, "description": "data_inicio não pode ser posterior a data_fim."},
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        404: {"model": ErrorResponse, "description": "Fornecedor explicitamente não encontrado."},
        422: {"model": ValidationErrorResponse, "description": "Parâmetro inválido."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def listar_movimentacoes(
    db: Session = Depends(get_db),
    data_inicio: Optional[AwareDatetime] = None,
    data_fim: Optional[AwareDatetime] = None,
    fornecedor_id: Optional[int] = None
):
    if data_inicio and data_fim and data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="data_inicio não pode ser posterior a data_fim."
        )

    stmt = select(MovimentacaoEstoque)

    if fornecedor_id is not None:
        if not db.get(Fornecedor, fornecedor_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fornecedor não encontrado."
            )
        stmt = stmt.where(MovimentacaoEstoque.fornecedor_id == fornecedor_id)

    if data_inicio:
        stmt = stmt.where(MovimentacaoEstoque.data >= data_inicio)
    if data_fim:
        stmt = stmt.where(MovimentacaoEstoque.data <= data_fim)

    stmt = stmt.order_by(MovimentacaoEstoque.id)
    return db.scalars(stmt).all()

@router.get(
    "/{movimentacao_id}",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=MovimentacaoResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        404: {"model": ErrorResponse, "description": "Movimentação não encontrada."},
        422: {"model": ValidationErrorResponse, "description": "Parâmetro inválido."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
def buscar_movimentacao(movimentacao_id: int, db: Session = Depends(get_db)):
    movimentacao = db.get(MovimentacaoEstoque, movimentacao_id)
    if not movimentacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimentação não encontrada."
        )
    return movimentacao
