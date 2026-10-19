from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.models.usuario import Usuario, Role
from app.security.passwords import hash_password
from app.security.jwt import create_access_token, decode_access_token
from app.security.auth import get_current_user
from app.config import settings

@pytest.fixture
def config_jwt_teste(monkeypatch):
    config = SimpleNamespace(
        jwt_secret_key="segredo-ficticio-exclusivo-dos-testes-jwt-0123456789-abcdefghijklmnop",
        jwt_algorithm="HS256",
        access_token_expire_minutes=60,
    )
    # Substitui apenas a referência do módulo JWT; monkeypatch restaura ao final.
    monkeypatch.setattr("app.security.jwt.settings", config)
    return config


@pytest.fixture
def create_test_users(verify_test_database):
    from app.database import SessionLocal
    with SessionLocal() as db:
        admin = Usuario(username="admin", password_hash=hash_password("senha-admin"), role=Role.ADMIN)
        funcionario = Usuario(username="func", password_hash=hash_password("senha-func"), role=Role.FUNCIONARIO)
        db.add_all([admin, funcionario])
        db.commit()
    yield
    with SessionLocal() as db:
        db.execute(Usuario.__table__.delete().where(Usuario.username.in_(["admin", "func", "deletado"])))
        db.commit()

def test_login_admin_valido(unauthenticated_client, create_test_users):
    assert "Authorization" not in unauthenticated_client.headers
    response = unauthenticated_client.post("/auth/login", json={"username": "admin", "password": "senha-admin"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    response = unauthenticated_client.get(
        "/produtos", headers={"Authorization": f"Bearer {data['access_token']}"}
    )
    assert response.status_code == 200

def test_login_funcionario_valido(client, create_test_users):
    response = client.post("/auth/login", json={"username": "func", "password": "senha-func"})
    assert response.status_code == 200

def test_login_username_inexistente(client):
    response = client.post("/auth/login", json={"username": "fantasma", "password": "123"})
    assert response.status_code == 401
    assert response.json()["message"] == "Credenciais inválidas."

def test_login_senha_incorreta(client, create_test_users):
    response = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["message"] == "Credenciais inválidas."

def test_login_campo_extra(client):
    response = client.post("/auth/login", json={"username": "a", "password": "b", "extra": "1"})
    assert response.status_code == 422

def test_decode_token_valido(config_jwt_teste):
    antes = datetime.now(timezone.utc)
    token = create_access_token("teste_sub")
    depois = datetime.now(timezone.utc)
    payload = decode_access_token(token)
    assert set(payload) == {"sub", "exp"}
    assert payload["sub"] == "teste_sub"
    duracao = timedelta(minutes=config_jwt_teste.access_token_expire_minutes)
    assert int((antes + duracao).timestamp()) <= payload["exp"] <= int((depois + duracao).timestamp())


@pytest.mark.parametrize(
    "cenario, erro_esperado",
    [
        pytest.param("sem_exp", jwt.MissingRequiredClaimError, id="sem-exp"),
        pytest.param("sub_vazio", jwt.InvalidTokenError, id="sub-vazio"),
        pytest.param("assinatura_incorreta", jwt.InvalidSignatureError, id="assinatura-incorreta"),
        pytest.param("algoritmo_nao_permitido", jwt.InvalidAlgorithmError, id="algoritmo-nao-permitido"),
        pytest.param("exp_invalido", jwt.DecodeError, id="exp-invalido"),
        pytest.param("sem_assinatura", jwt.InvalidAlgorithmError, id="sem-assinatura"),
    ],
)
def test_decoder_rejeita_token_invalido(config_jwt_teste, cenario, erro_esperado):
    payload = {"sub": "teste_sub", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
    chave = config_jwt_teste.jwt_secret_key
    algoritmo = config_jwt_teste.jwt_algorithm

    if cenario == "sem_exp":
        del payload["exp"]
    elif cenario == "sub_vazio":
        payload["sub"] = ""
    elif cenario == "assinatura_incorreta":
        chave = "outra-chave-ficticia-exclusiva-dos-testes-jwt-0123456789-abcdefghijklmnop"
    elif cenario == "algoritmo_nao_permitido":
        algoritmo = "HS384"
    elif cenario == "exp_invalido":
        payload["exp"] = "expiracao-invalida"
    elif cenario == "sem_assinatura":
        algoritmo = "none"
        chave = ""

    token = jwt.encode(payload, chave, algorithm=algoritmo)
    with pytest.raises(erro_esperado) as excinfo:
        decode_access_token(token)
    if cenario == "sem_exp":
        assert excinfo.value.claim == "exp"

def test_token_nao_contem_campos_sensiveis(client, create_test_users):
    response = client.post("/auth/login", json={"username": "admin", "password": "senha-admin"})
    token = response.json()["access_token"]
    payload = decode_access_token(token)
    assert "role" not in payload
    assert "password" not in payload
    assert "password_hash" not in payload

def test_token_expirado(config_jwt_teste):
    now = datetime.now(timezone.utc)
    expire = now - timedelta(minutes=1)
    payload = {"sub": "admin", "exp": expire}
    token = jwt.encode(payload, config_jwt_teste.jwt_secret_key, algorithm=config_jwt_teste.jwt_algorithm)

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)

    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials
    from app.database import SessionLocal

    with pytest.raises(HTTPException) as excinfo:
        with SessionLocal() as db:
            get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token), db)

    assert excinfo.value.status_code == 401

def test_token_malformado():
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials
    from app.database import SessionLocal

    with pytest.raises(HTTPException) as excinfo:
        with SessionLocal() as db:
            get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad.token.here"), db)

    assert excinfo.value.status_code == 401

def test_token_sem_sub(config_jwt_teste):
    payload = {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
    token = jwt.encode(payload, config_jwt_teste.jwt_secret_key, algorithm=config_jwt_teste.jwt_algorithm)

    with pytest.raises(jwt.MissingRequiredClaimError) as claim_error:
        decode_access_token(token)
    assert claim_error.value.claim == "sub"

    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials
    from app.database import SessionLocal

    with pytest.raises(HTTPException) as excinfo:
        with SessionLocal() as db:
            get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token), db)

    assert excinfo.value.status_code == 401

def test_token_valido_usuario_deletado():
    from app.database import SessionLocal
    with SessionLocal() as db:
        u = Usuario(username="deletado", password_hash="123", role="ADMIN")
        db.add(u)
        db.commit()

    token = create_access_token("deletado")

    with SessionLocal() as db:
        db.execute(Usuario.__table__.delete().where(Usuario.username == "deletado"))
        db.commit()

    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials

    with pytest.raises(HTTPException) as excinfo:
        with SessionLocal() as db:
            get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token), db)

    assert excinfo.value.status_code == 401

def test_token_ausente_gera_401_no_endpoint(unauthenticated_client):
    response = unauthenticated_client.get("/produtos")
    assert response.status_code == 401


def test_token_valido_retorna_usuario_atual(create_test_users):
    app_teste = FastAPI()

    @app_teste.get("/test-auth")
    def test_endpoint(user: Usuario = Depends(get_current_user)):
        return {"user": user.username}

    token = create_access_token("admin")
    with TestClient(app_teste) as client_local:
        response = client_local.get("/test-auth", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["user"] == "admin"


def test_role_atual_no_banco_nao_do_token(client, create_test_users):
    from app.database import SessionLocal
    token = create_access_token("admin")

    from sqlalchemy import select
    with SessionLocal() as db:
        admin = db.scalar(select(Usuario).where(Usuario.username == "admin"))
        assert admin.role == "ADMIN"

        db.execute(Usuario.__table__.update().where(Usuario.username == "admin").values(role="FUNCIONARIO"))
        db.commit()

    from fastapi.security import HTTPAuthorizationCredentials
    with SessionLocal() as db:
        user = get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token), db)
        assert user.role == "FUNCIONARIO"

def test_settings_fails_without_jwt_secret(monkeypatch):
    from pydantic import ValidationError
    from app.config import Settings

    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    with pytest.raises(ValidationError) as excinfo:
        Settings(
            _env_file=None,
            db_host="localhost",
            db_port=5432,
            db_name="test",
            db_user="user",
            db_password="123"
        )
    assert "jwt_secret_key" in str(excinfo.value)

def test_www_authenticate_header_in_401(unauthenticated_client, create_test_users):
    payload_expirado = {
        "sub": "admin",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    token_expirado = jwt.encode(
        payload_expirado, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    # O usuário existe: sem a exigência de exp, este token permitiria acesso.
    token_sem_exp = jwt.encode(
        {"sub": "admin"}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    cenarios = [
        ("ausente", {}),
        ("malformado", {"Authorization": "Bearer bad_token"}),
        ("expirado", {"Authorization": f"Bearer {token_expirado}"}),
        ("sem_exp", {"Authorization": f"Bearer {token_sem_exp}"}),
    ]
    for cenario, headers in cenarios:
        response = unauthenticated_client.get("/produtos", headers=headers)
        assert response.status_code == 401, cenario
        assert response.headers.get("WWW-Authenticate") == "Bearer", cenario
        assert response.json() == {
            "status": 401,
            "error": "unauthorized",
            "message": "Credenciais inválidas.",
            "details": None,
        }, cenario
