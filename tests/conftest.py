import os
import pytest
from sqlalchemy import text

# Configurar o banco de dados para testes antes dos imports da aplicação
os.environ.setdefault("DB_NAME", "stockflow_test")
os.environ.setdefault("JWT_SECRET_KEY", "stockflow_test_secret_only_for_automated_tests_123456")

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

@pytest.fixture(autouse=True)
def clean_database(verify_test_database):
    """
    Limpa o banco de dados antes e depois de cada teste.
    Somente executa se a guarda de segurança já validou o banco conectado.
    """
    def _clean():
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text("DELETE FROM movimentacoes_estoque"))
                conn.execute(text("DELETE FROM produtos"))
                conn.execute(text("DELETE FROM fornecedores"))
                conn.execute(text("DELETE FROM categorias"))
                conn.execute(text("DELETE FROM usuarios"))

    _clean()
    yield
    _clean()

@pytest.fixture
def client(admin_headers):
    with TestClient(app) as test_client:
        test_client.headers.update(admin_headers)
        yield test_client

@pytest.fixture
def unauthenticated_client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def admin_headers():
    from app.database import SessionLocal
    from app.models.usuario import Usuario, Role
    from app.security.passwords import hash_password
    from app.security.jwt import create_access_token
    
    with SessionLocal() as db:
        admin = Usuario(username="test_admin", password_hash=hash_password("admin_pass"), role=Role.ADMIN)
        db.add(admin)
        db.commit()
    
    token = create_access_token("test_admin")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def funcionario_headers():
    from app.database import SessionLocal
    from app.models.usuario import Usuario, Role
    from app.security.passwords import hash_password
    from app.security.jwt import create_access_token
    
    with SessionLocal() as db:
        func = Usuario(username="test_func", password_hash=hash_password("func_pass"), role=Role.FUNCIONARIO)
        db.add(func)
        db.commit()
    
    token = create_access_token("test_func")
    return {"Authorization": f"Bearer {token}"}
