import logging

from fastapi import FastAPI

from app.exceptions import add_exception_handlers
from app.routers import auth, categorias, fornecedores, movimentacoes, produtos

app_logger = logging.getLogger("app")
if not app_logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    app_logger.addHandler(handler)
    # Sem handlers, WARNING no root é tratado como o padrão do logging.
    if app_logger.level == logging.NOTSET and logging.getLogger().level == logging.WARNING:
        app_logger.setLevel(logging.INFO)

app = FastAPI(
    title="StockFlow API",
    description="REST API para gerenciamento de estoque.",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(fornecedores.router)
app.include_router(produtos.router)
app.include_router(movimentacoes.router)

add_exception_handlers(app)

@app.get(
    "/",
    summary="Root Endpoint",
    description="Retorna o status básico do projeto."
)
def root():
    return {"project": "StockFlow API", "status": "running"}


@app.get(
    "/health",
    summary="Health check",
    description="Confirma que a aplicação está em execução e consegue responder a requisições HTTP.",
)
def health():
    return {"status": "healthy"}
