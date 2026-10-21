from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ProdutoBase(BaseModel):
    nome: str = Field(..., max_length=150)
    sku: str = Field(..., max_length=50)
    preco_custo: Decimal = Field(
        ...,
        ge=0,
        max_digits=12,
        decimal_places=2,
        description=(
            "Preço de custo não negativo, validado como Decimal: até 12 dígitos "
            "no total, no máximo 10 na parte inteira e 2 casas decimais. "
            "Zeros finais na parte decimal são desconsiderados nesses limites. "
            "Na entrada, aceita número JSON ou string decimal; prefira string "
            "para preservar a representação decimal. Nas respostas, é "
            "serializado como string, sem impor duas casas decimais fixas."
        ),
        examples=["0.00", "100.00", "9999999999.99"],
    )
    preco_venda: Decimal = Field(
        ...,
        ge=0,
        max_digits=12,
        decimal_places=2,
        description=(
            "Preço de venda não negativo, validado como Decimal: até 12 dígitos "
            "no total, no máximo 10 na parte inteira e 2 casas decimais. "
            "Zeros finais na parte decimal são desconsiderados nesses limites. "
            "Na entrada, aceita número JSON ou string decimal; prefira string "
            "para preservar a representação decimal. Nas respostas, é "
            "serializado como string, sem impor duas casas decimais fixas."
        ),
        examples=["0.00", "100.00", "9999999999.99"],
    )
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
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "nome": "Teclado atualizado",
                "sku": "TEC-001",
                "preco_custo": "110.00",
                "preco_venda": "160.00",
                "estoque_minimo": 8,
                "categoria_id": 1,
                "fornecedor_id": 1
            }
        }
    )

class ProdutoResponse(ProdutoBase):
    id: int
    quantidade_em_estoque: int
    data_cadastro: datetime

    model_config = ConfigDict(from_attributes=True)
