from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class TipoMovimentacao(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"

class MovimentacaoCreate(BaseModel):
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: int = Field(..., gt=0)

    model_config = ConfigDict(extra="forbid")

class MovimentacaoResponse(BaseModel):
    id: int
    tipo: TipoMovimentacao
    quantidade: int
    data: datetime
    produto_id: int
    fornecedor_id: int

    model_config = ConfigDict(from_attributes=True)
