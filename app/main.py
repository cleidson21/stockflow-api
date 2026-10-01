from fastapi import FastAPI

app = FastAPI(
    title="StockFlow API",
    description="REST API para gerenciamento de estoque.",
    version="0.1.0",
)

from app.routers import categorias
app.include_router(categorias.router)


@app.get("/")
def root():
    return {"project": "StockFlow API", "status": "running"}


@app.get(
    "/health",
    summary="Health check",
    description="Confirma que a aplicação está em execução e consegue responder a requisições HTTP.",
)
def health():
    return {"status": "ok"}
