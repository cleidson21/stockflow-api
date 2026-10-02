from pydantic import BaseModel, Field, ConfigDict

class CategoriaBase(BaseModel):
    nome: str = Field(..., max_length=100)

class CategoriaCreate(CategoriaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Eletrônicos"
            }
        }
    )
class CategoriaUpdate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
