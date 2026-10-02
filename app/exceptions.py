import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

def add_exception_handlers(app: FastAPI):
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # Map HTTP status codes to standard error categories
        status_code = exc.status_code
        if status_code == 400:
            error_cat = "bad_request"
        elif status_code == 404:
            error_cat = "not_found"
        elif status_code == 409:
            error_cat = "conflict"
        elif status_code == 405:
            error_cat = "method_not_allowed"
        else:
            error_cat = "http_error"

        return JSONResponse(
            status_code=status_code,
            content={
                "status": status_code,
                "error": error_cat,
                "message": exc.detail,
                "details": None
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Format the validation errors securely
        details = []
        for error in exc.errors():
            details.append({
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "type": error.get("type")
            })
            
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": 422,
                "error": "validation_error",
                "message": "Dados de entrada inválidos.",
                "details": details
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Log the internal details for the server administrators
        logger.exception(f"Erro inesperado: {exc}")
        
        # Return generic secure message to the client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": 500,
                "error": "internal_error",
                "message": "Erro interno do servidor.",
                "details": None
            }
        )
