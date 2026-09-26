from fastapi import FastAPI

app = FastAPI(
    title="StockFlow API",
    description="REST API para gerenciamento de estoque.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"project": "StockFlow API", "status": "running"}
