from typing import List
from sqlalchemy import String, Integer, Identity, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cnpj: Mapped[str] = mapped_column(String(14), nullable=False, unique=True)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)

    produtos: Mapped[List["Produto"]] = relationship(back_populates="fornecedor")
    movimentacoes: Mapped[List["MovimentacaoEstoque"]] = relationship(back_populates="fornecedor")

    __table_args__ = (
        CheckConstraint(
            "char_length(cnpj) = 14 AND cnpj ~ '^[0-9]+$'",
            name="ck_fornecedor_cnpj_formato"
        ),
    )
