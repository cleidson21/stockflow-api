from sqlalchemy import Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from enum import Enum

class Role(str, Enum):
    ADMIN = "ADMIN"
    FUNCIONARIO = "FUNCIONARIO"

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('ADMIN', 'FUNCIONARIO')", name="check_role_valido"),
    )
