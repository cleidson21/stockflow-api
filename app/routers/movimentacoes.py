from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.produto import Produto
from app.models.movimentacao import MovimentacaoEstoque
from app.schemas.movimentacao import MovimentacaoCreate, MovimentacaoResponse, TipoMovimentacao

router = APIRouter(
    prefix="/movimentacoes",
    tags=["Movimentações"]
)

@router.post("", response_model=MovimentacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_movimentacao(mov_in: MovimentacaoCreate, db: Session = Depends(get_db)):
    try:
        with db.begin():
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
                        status_code=status.HTTP_400_BAD_REQUEST,
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
        
        db.refresh(nova_movimentacao)
        return nova_movimentacao
    except IntegrityError as e:
        # O contexto with db.begin() já realizou o rollback.
        raise e


@router.get("", response_model=List[MovimentacaoResponse])
def listar_movimentacoes(db: Session = Depends(get_db)):
    stmt = select(MovimentacaoEstoque).order_by(MovimentacaoEstoque.id)
    return db.scalars(stmt).all()

@router.get("/{movimentacao_id}", response_model=MovimentacaoResponse)
def buscar_movimentacao(movimentacao_id: int, db: Session = Depends(get_db)):
    movimentacao = db.get(MovimentacaoEstoque, movimentacao_id)
    if not movimentacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimentação não encontrada."
        )
    return movimentacao
