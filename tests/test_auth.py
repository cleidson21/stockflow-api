import pytest
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends
from app.models.usuario import Usuario, Role
from app.security.passwords import hash_password
from app.security.jwt import create_access_token, decode_access_token
from app.security.auth import get_current_user
from app.config import settings

@pytest.fixture
def create_test_users(client, verify_test_database):
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

def test_login_admin_valido(client, create_test_users):
    response = client.post("/auth/login", json={"username": "admin", "password": "senha-admin"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

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

def test_decode_token_valido():
    token = create_access_token("teste_sub")
    payload = decode_access_token(token)
    assert payload["sub"] == "teste_sub"

def test_token_nao_contem_campos_sensiveis(client, create_test_users):
    response = client.post("/auth/login", json={"username": "admin", "password": "senha-admin"})
    token = response.json()["access_token"]
    payload = decode_access_token(token)
    assert "role" not in payload
    assert "password" not in payload
    assert "password_hash" not in payload

def test_token_expirado():
    now = datetime.now(timezone.utc)
    expire = now - timedelta(minutes=1)
    payload = {"sub": "admin", "exp": expire}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials
    from app.database import SessionLocal
    
    with pytest.raises(HTTPException) as excinfo:
        with SessionLocal() as db:
            get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token), db)
    
    assert excinfo.value.status_code == 401

def test_token_adulterado():
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials
    from app.database import SessionLocal
    
    with pytest.raises(HTTPException) as excinfo:
        with SessionLocal() as db:
            get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad.token.here"), db)
            
    assert excinfo.value.status_code == 401

def test_token_sem_sub():
    payload = {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
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
    from fastapi import APIRouter
    from app.main import app
    
    router = APIRouter()
    @router.get("/test-auth")
    def test_endpoint(user = Depends(get_current_user)):
        return {"user": user.username}
        
    app.include_router(router)
    
    response = unauthenticated_client.get("/test-auth")
    assert response.status_code == 401

def test_token_valido_retorna_usuario_atual(client, create_test_users):
    from fastapi import APIRouter
    from app.main import app
    
    router = APIRouter()
    @router.get("/test-auth-2")
    def test_endpoint(user = Depends(get_current_user)):
        return {"user": user.username}
        
    app.include_router(router)
    
    token = create_access_token("admin")
    response = client.get("/test-auth-2", headers={"Authorization": f"Bearer {token}"})
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
    
    # Removendo a variável de ambiente para forçar o erro
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    
    with pytest.raises(ValidationError) as excinfo:
        Settings(
            db_host="localhost",
            db_port=5432,
            db_name="test",
            db_user="user",
            db_password="123"
        )
    assert "jwt_secret_key" in str(excinfo.value)

def test_www_authenticate_header_in_401(unauthenticated_client):
    from fastapi import APIRouter
    from app.main import app
    
    router = APIRouter()
    @router.get("/test-auth-header")
    def test_endpoint(user = Depends(get_current_user)):
        return {"user": user.username}
        
    app.include_router(router)
    
    # Ausente
    response = unauthenticated_client.get("/test-auth-header")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"
    
    # Invalido
    response = unauthenticated_client.get("/test-auth-header", headers={"Authorization": "Bearer bad_token"})
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"
    
    # Expirado
    now = datetime.now(timezone.utc)
    expire = now - timedelta(minutes=1)
    payload = {"sub": "admin", "exp": expire}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    response = unauthenticated_client.get("/test-auth-header", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"
