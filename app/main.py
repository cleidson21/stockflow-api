from fastapi import FastAPI

app = FastAPI(
    title="StockFlow API",
    description="REST API para gerenciamento de estoque.",
    version="0.1.0",
)

from app.routers import categorias, fornecedores, produtos, movimentacoes
from app.exceptions import add_exception_handlers

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
