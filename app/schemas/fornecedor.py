from pydantic import BaseModel, Field, ConfigDict

class FornecedorBase(BaseModel):
    nome: str = Field(..., max_length=150)
    cnpj: str = Field(..., min_length=14, max_length=14, pattern=r'^\d{14}$')
    telefone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=254)

class FornecedorCreate(FornecedorBase):
    pass

class FornecedorUpdate(FornecedorBase):
    pass

class FornecedorResponse(FornecedorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
