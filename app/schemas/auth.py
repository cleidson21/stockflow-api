from pydantic import BaseModel, ConfigDict

class LoginRequest(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "senha-exemplo"
            }
        }
    )

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
