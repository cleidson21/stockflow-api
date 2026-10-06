import os
import pytest
from sqlalchemy import text

# Configurar o banco de dados para testes antes dos imports da aplicação
os.environ["DB_NAME"] = "stockflow_test"

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine

@pytest.fixture(scope="session", autouse=True)
def verify_test_database():
    """
    Guarda de segurança obrigatória.
    Impede que a suíte de testes rode no banco de desenvolvimento, 
    abortando a execução se o banco conectado não for 'stockflow_test'.
    """
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database()")).scalar()
        if result != "stockflow_test":
            pytest.exit(f"Testes abortados: banco conectado não é stockflow_test. O banco atual é {result}.")

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
