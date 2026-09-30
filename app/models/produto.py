from typing import List
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, Identity, CheckConstraint, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    preco_custo: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    preco_venda: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantidade_em_estoque: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    estoque_minimo: Mapped[int] = mapped_column(Integer, nullable=False)
    data_cadastro: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=func.current_timestamp()
    )
    categoria_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("categorias.id", ondelete="RESTRICT"), 
        nullable=False
    )
    fornecedor_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("fornecedores.id", ondelete="RESTRICT"), 
        nullable=False
    )

    categoria: Mapped["Categoria"] = relationship(back_populates="produtos")
    fornecedor: Mapped["Fornecedor"] = relationship(back_populates="produtos")
    movimentacoes: Mapped[List["MovimentacaoEstoque"]] = relationship(back_populates="produto")

    __table_args__ = (
        CheckConstraint("preco_custo >= 0", name="ck_produto_preco_custo_nao_negativo"),
        CheckConstraint("preco_venda >= 0", name="ck_produto_preco_venda_nao_negativo"),
        CheckConstraint("quantidade_em_estoque >= 0", name="ck_produto_quantidade_nao_negativa"),
        CheckConstraint("estoque_minimo >= 0", name="ck_produto_estoque_minimo_nao_negativo"),
        Index("ix_produto_categoria_id", "categoria_id"),
        Index("ix_produto_fornecedor_id", "fornecedor_id"),
    )
