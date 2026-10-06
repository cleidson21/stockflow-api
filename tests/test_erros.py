import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.exceptions import add_exception_handlers

def test_erros_padronizados_400(client):
    # Intervalo temporal invalido
    response = client.get("/movimentacoes?data_inicio=2026-10-10T00:00:00Z&data_fim=2026-10-01T00:00:00Z")
    assert response.status_code == 400
    body = response.json()
    assert body["status"] == 400
    assert body["error"] == "bad_request"
    assert "message" in body

def test_erros_padronizados_404(client):
    response = client.get("/produtos/99999")
    assert response.status_code == 404
    body = response.json()
    assert body["status"] == 404
    assert body["error"] == "not_found"
    assert "message" in body
    assert "DATABASE_URL" not in body["message"]

def test_erros_padronizados_409(client):
    # Criar duplicado para disparar 409
    client.post("/categorias", json={"nome": "Duplicado Error"})
    response = client.post("/categorias", json={"nome": "Duplicado Error"})
    assert response.status_code == 409
    body = response.json()
    assert body["status"] == 409
    assert body["error"] == "conflict"
    assert "message" in body
    assert "constraint" not in body["message"].lower()

def test_erros_padronizados_422(client):
    # Body sem campos obrigatorios ou nome vazio. Se nome vazio for 422
    response = client.post("/categorias", json={}) 
    assert response.status_code == 422
    body = response.json()
    assert body["status"] == 422
    assert body["error"] == "validation_error"
    assert "message" in body
    assert isinstance(body.get("details"), list)

def test_handler_500_seguro(caplog):
    app_teste = FastAPI()
    add_exception_handlers(app_teste)
    
    @app_teste.get("/falha-controlada")
    def falha():
        raise RuntimeError("segredo-interno-de-teste")
        
    client_local = TestClient(app_teste, raise_server_exceptions=False)
    response = client_local.get("/falha-controlada")
    
    assert response.status_code == 500
    body = response.json()
    assert body["status"] == 500
    assert body["error"] == "internal_error"
    assert body["message"] == "Erro interno do servidor."
    
    # Confirmar que o segredo nao esta no body
    assert "segredo-interno-de-teste" not in response.text
    
    # Confirmar que log capturou o erro real
    assert any("segredo-interno-de-teste" in rec.message for rec in caplog.records if rec.levelno >= 40)
