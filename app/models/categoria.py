from typing import List
from sqlalchemy import String, Integer, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    produtos: Mapped[List["Produto"]] = relationship(back_populates="categoria")
