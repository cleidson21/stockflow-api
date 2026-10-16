"""Manipuladores globais de exceção e padronização de respostas de erro da API."""
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def add_exception_handlers(app: FastAPI) -> None:
    """Registra os manipuladores de exceção na aplicação FastAPI."""

    # Captura exceções HTTPException do FastAPI e erros HTTP nativos do Starlette (404/405)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        status_code = exc.status_code
        if status_code == 400:
            error_cat = "bad_request"
        elif status_code == 401:
            error_cat = "unauthorized"
        elif status_code == 403:
            error_cat = "forbidden"
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
            # Preserva headers originais (necessário para 'WWW-Authenticate: Bearer' no 401)
            headers=getattr(exc, "headers", None),
            content={
                "status": status_code,
                "error": error_cat,
                "message": exc.detail,
                "details": None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Filtra estritamente loc, msg e type, omitindo input/ctx para evitar reflexão de dados brutos
        details = []
        for error in exc.errors():
            details.append({
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "type": error.get("type"),
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": 422,
                "error": "validation_error",
                "message": "Dados de entrada inválidos.",
                "details": details,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Prioriza o padrão da rota (ex: /produtos/{id}) em vez de valores dinâmicos concretos
        route = request.scope.get("route")
        route_pattern = route.path if route and hasattr(route, "path") else "<rota_nao_identificada>"

        # Metadados estruturados para rastreabilidade sem exposição de dados sensíveis da requisição
        extra_data = {
            "event_type": "unhandled_exception",
            "http_method": request.method,
            "route": route_pattern,
            "exception_type": exc.__class__.__name__,
        }

        # Registra metadados no LogRecord (extra) e formata mensagem para saídas sem suporte a campos estruturados
        logger.exception(
            f"Erro inesperado: {exc} | event_type={extra_data['event_type']} "
            f"http_method={extra_data['http_method']} route={extra_data['route']} "
            f"exception_type={extra_data['exception_type']}",
            extra=extra_data,
        )

        # Resposta genérica fixa: isolamento estrito contra vazamento de detalhes internos ao cliente
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": 500,
                "error": "internal_error",
                "message": "Erro interno do servidor.",
                "details": None,
            },
        )
