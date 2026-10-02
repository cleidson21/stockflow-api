from pydantic import BaseModel, Field, ConfigDict

class FornecedorBase(BaseModel):
    nome: str = Field(..., max_length=150)
    cnpj: str = Field(..., min_length=14, max_length=14, pattern=r'^\d{14}$')
    telefone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=254)

class FornecedorCreate(FornecedorBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Fornecedor Exemplo",
                "cnpj": "12345678000199",
                "telefone": "75999999999",
                "email": "contato@example.com"
            }
        }
    )

class FornecedorUpdate(FornecedorBase):
    pass

class FornecedorResponse(FornecedorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
