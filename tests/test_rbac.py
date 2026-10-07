import pytest
from app.models.usuario import Role

def test_sem_token(unauthenticated_client):
    # GET leitura
    response = unauthenticated_client.get("/produtos")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"
    
    # POST escrita
    response = unauthenticated_client.post("/categorias", json={"nome": "Teste 401"})
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"

def test_admin_permissoes(client):
    # ADMIN tem permissão total. client usa admin_headers por padrão
    cat = client.post("/categorias", json={"nome": "Cat Admin"})
    assert cat.status_code == 201
    cat_id = cat.json()["id"]
    
    cat_put = client.put(f"/categorias/{cat_id}", json={"nome": "Cat Admin Atualizada"})
    assert cat_put.status_code == 200
    
    forn = client.post("/fornecedores", json={
        "nome": "Forn Admin", "cnpj": "12345678901235", "telefone": "11999999999", "email": "admin@test.com"
    })
    assert forn.status_code == 201
    forn_id = forn.json()["id"]
    
    prod = client.post("/produtos", json={
        "nome": "Prod Admin", "sku": "SKU-ADMIN-1", "preco_custo": "10.00", "preco_venda": "20.00",
        "estoque_minimo": 5, "categoria_id": cat_id, "fornecedor_id": forn_id
    })
    assert prod.status_code == 201
    prod_id = prod.json()["id"]
    
    mov = client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10})
    assert mov.status_code == 201
    
    cat_del = client.delete(f"/categorias/{cat_id}")
    assert cat_del.status_code in (204, 409) # Pode dar 409 por causa do produto

def test_funcionario_leitura(unauthenticated_client, funcionario_headers):
    unauthenticated_client.headers.update(funcionario_headers)
    
    assert unauthenticated_client.get("/categorias").status_code == 200
    assert unauthenticated_client.get("/fornecedores").status_code == 200
    assert unauthenticated_client.get("/produtos").status_code == 200
    assert unauthenticated_client.get("/produtos/consultas/estoque-minimo").status_code == 200
    assert unauthenticated_client.get("/movimentacoes").status_code == 200

def test_funcionario_movimentacao(client, unauthenticated_client, funcionario_headers):
    # Prepara dados com admin (client)
    cat_id = client.post("/categorias", json={"nome": "Cat Func"}).json()["id"]
    forn_id = client.post("/fornecedores", json={
        "nome": "Forn Func", "cnpj": "12345678901236", "telefone": "11999999999", "email": "func@test.com"
    }).json()["id"]
    prod_id = client.post("/produtos", json={
        "nome": "Prod Func", "sku": "SKU-FUNC-1", "preco_custo": "10.00", "preco_venda": "20.00",
        "estoque_minimo": 5, "categoria_id": cat_id, "fornecedor_id": forn_id
    }).json()["id"]
    
    # Testa movimentação com funcionario
    unauthenticated_client.headers.update(funcionario_headers)
    
    mov = unauthenticated_client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10})
    assert mov.status_code == 201
    
    movs = unauthenticated_client.get("/movimentacoes")
    assert movs.status_code == 200

def test_funcionario_proibido(unauthenticated_client, funcionario_headers):
    unauthenticated_client.headers.update(funcionario_headers)
    
    endpoints_escrita = [
        ("POST", "/categorias", {"nome": "Teste 403"}),
        ("PUT", "/categorias/999", {"nome": "Teste 403"}),
        ("DELETE", "/categorias/999", None),
        ("POST", "/fornecedores", {"nome": "Teste 403", "cnpj": "1", "telefone": "1", "email": "a@b.com"}),
        ("PUT", "/fornecedores/999", {"nome": "Teste 403", "cnpj": "1", "telefone": "1", "email": "a@b.com"}),
        ("DELETE", "/fornecedores/999", None),
        ("POST", "/produtos", {"nome": "Teste 403", "sku": "1", "preco_custo": "1", "preco_venda": "1", "estoque_minimo": 1, "categoria_id": 1, "fornecedor_id": 1}),
        ("PUT", "/produtos/999", {"nome": "Teste 403", "sku": "1", "preco_custo": "1", "preco_venda": "1", "estoque_minimo": 1, "categoria_id": 1, "fornecedor_id": 1}),
        ("DELETE", "/produtos/999", None),
    ]
    
    for metodo, url, json_body in endpoints_escrita:
        response = unauthenticated_client.request(metodo, url, json=json_body)
        assert response.status_code == 403
        assert "WWW-Authenticate" not in response.headers
        data = response.json()
        assert data["status"] == 403
        assert data["error"] == "forbidden"
        assert data["details"] is None

def test_role_alterada_apos_token(unauthenticated_client):
    from app.database import SessionLocal
    from app.models.usuario import Usuario, Role
    from app.security.passwords import hash_password
    from app.security.jwt import create_access_token
    
    with SessionLocal() as db:
        admin = Usuario(username="mutante", password_hash=hash_password("123"), role=Role.ADMIN)
        db.add(admin)
        db.commit()
    
    token = create_access_token("mutante")
    unauthenticated_client.headers.update({"Authorization": f"Bearer {token}"})
    
    # 1. Confirma operação de ADMIN
    response = unauthenticated_client.post("/categorias", json={"nome": "Mutante Cat"})
    assert response.status_code == 201
    
    # 2. Altera role no banco para FUNCIONARIO
    with SessionLocal() as db:
        db.execute(Usuario.__table__.update().where(Usuario.username == "mutante").values(role=Role.FUNCIONARIO.value))
        db.commit()
        
    # 3. Mesmo token deve tomar 403
    response2 = unauthenticated_client.post("/categorias", json={"nome": "Mutante Cat 2"})
    assert response2.status_code == 403

def test_usuario_deletado(unauthenticated_client):
    from app.database import SessionLocal
    from app.models.usuario import Usuario, Role
    from app.security.passwords import hash_password
    from app.security.jwt import create_access_token
    
    with SessionLocal() as db:
        fantasma = Usuario(username="fantasma", password_hash=hash_password("123"), role=Role.ADMIN)
        db.add(fantasma)
        db.commit()
    
    token = create_access_token("fantasma")
    unauthenticated_client.headers.update({"Authorization": f"Bearer {token}"})
    
    with SessionLocal() as db:
        db.execute(Usuario.__table__.delete().where(Usuario.username == "fantasma"))
        db.commit()
        
    response = unauthenticated_client.get("/produtos")
    assert response.status_code == 401
