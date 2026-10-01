from pydantic import BaseModel, Field, ConfigDict

class CategoriaBase(BaseModel):
    nome: str = Field(..., max_length=100)

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
