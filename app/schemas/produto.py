from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ProdutoBase(BaseModel):
    nome: str = Field(..., max_length=150)
    sku: str = Field(..., max_length=50)
    preco_custo: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)
    preco_venda: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)
    estoque_minimo: int = Field(..., ge=0)
    categoria_id: int
    fornecedor_id: int

class ProdutoCreate(ProdutoBase):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "nome": "Teclado",
                "sku": "TEC-001",
                "preco_custo": "100.00",
                "preco_venda": "150.00",
                "estoque_minimo": 5,
                "categoria_id": 1,
                "fornecedor_id": 1
            }
        }
    )

class ProdutoUpdate(ProdutoBase):
    model_config = ConfigDict(extra="forbid")

class ProdutoResponse(ProdutoBase):
    id: int
    quantidade_em_estoque: int
    data_cadastro: datetime

    model_config = ConfigDict(from_attributes=True)
