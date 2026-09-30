from datetime import datetime
from sqlalchemy import String, Integer, Identity, CheckConstraint, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(7), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=func.current_timestamp()
    )
    produto_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("produtos.id", ondelete="RESTRICT"), 
        nullable=False
    )
    fornecedor_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("fornecedores.id", ondelete="RESTRICT"), 
        nullable=False
    )

    produto: Mapped["Produto"] = relationship(back_populates="movimentacoes")
    fornecedor: Mapped["Fornecedor"] = relationship(back_populates="movimentacoes")

    __table_args__ = (
        CheckConstraint("tipo IN ('ENTRADA', 'SAIDA')", name="ck_movimentacao_tipo_valido"),
        CheckConstraint("quantidade > 0", name="ck_movimentacao_quantidade_positiva"),
        Index("ix_movimentacao_produto_id", "produto_id"),
        Index("ix_movimentacao_data", "data"),
        Index("ix_movimentacao_fornecedor_data", "fornecedor_id", "data"),
    )
