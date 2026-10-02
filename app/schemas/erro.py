from typing import Any, List, Optional
from pydantic import BaseModel

class ErrorDetail(BaseModel):
    loc: List[str | int]
    msg: str
    type: str

class ErrorResponse(BaseModel):
    status: int
    error: str
    message: str
    details: Optional[Any] = None

class ValidationErrorResponse(BaseModel):
    status: int
    error: str
    message: str
    details: List[ErrorDetail]
