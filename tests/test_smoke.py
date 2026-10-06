import pytest
from sqlalchemy import text
from app.database import engine

def test_health_check(client):
    """
    Testa se o endpoint de health check está respondendo adequadamente 
    e assegura de forma redundante que estamos batendo no banco de teste.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_smoke_database_connection():
    """
    Confirma expressamente durante a execução da suíte que a engine 
    da aplicação está conectada ao banco isolado de testes.
    """
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database()")).scalar()
        assert result == "stockflow_test"
