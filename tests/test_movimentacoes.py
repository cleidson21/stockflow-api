import pytest

def criar_categoria(client):
    return client.post("/categorias", json={"nome": "Categoria Movimentacao"}).json()["id"]

def criar_fornecedor(client, nome="Fornecedor Movimentacao", cnpj="12345678901234", email="contato@movimentacao.com"):
    return client.post("/fornecedores", json={
        "nome": nome,
        "cnpj": cnpj,
        "telefone": "11999999999",
        "email": email
    }).json()["id"]

def criar_produto(client, cat_id, forn_id, nome="Produto Movimentacao", sku="SKU-MOV-001"):
    return client.post("/produtos", json={
        "nome": nome,
        "sku": sku,
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }).json()["id"]

def setup_base(client):
    cat_id = criar_categoria(client)
    forn_id = criar_fornecedor(client)
    prod_id = criar_produto(client, cat_id, forn_id)
    return cat_id, forn_id, prod_id

def test_movimentacao_entrada_valid(client):
    _, forn_id, prod_id = setup_base(client)
    
    # Produto inicialmente tem estoque 0
    res_prod = client.get(f"/produtos/{prod_id}")
    assert res_prod.json()["quantidade_em_estoque"] == 0

    payload = {
        "produto_id": prod_id,
        "tipo": "ENTRADA",
        "quantidade": 10
    }
    response = client.post("/movimentacoes", json=payload)
    assert response.status_code == 201
    
    body = response.json()
    assert "id" in body
    assert body["tipo"] == "ENTRADA"
    assert body["quantidade"] == 10
    assert body["produto_id"] == prod_id
    assert body["fornecedor_id"] == forn_id
    assert "data" in body

    # Confirma quantidade atualizada
    res_prod2 = client.get(f"/produtos/{prod_id}")
    assert res_prod2.json()["quantidade_em_estoque"] == 10

def test_movimentacao_entradas_sucessivas(client):
    _, _, prod_id = setup_base(client)
    
    client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10})
    client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 5})
    
    res_prod = client.get(f"/produtos/{prod_id}")
    assert res_prod.json()["quantidade_em_estoque"] == 15
    
    res_movs = client.get("/movimentacoes")
    assert len(res_movs.json()) == 2

def test_movimentacao_saida_valida(client):
    _, _, prod_id = setup_base(client)
    client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10})
    
    response = client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "SAIDA", "quantidade": 4})
    assert response.status_code == 201
    
    body = response.json()
    assert body["tipo"] == "SAIDA"
    assert body["quantidade"] == 4
    
    res_prod = client.get(f"/produtos/{prod_id}")
    assert res_prod.json()["quantidade_em_estoque"] == 6

def test_movimentacao_saida_exata(client):
    _, _, prod_id = setup_base(client)
    client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10})
    
    response = client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "SAIDA", "quantidade": 10})
    assert response.status_code == 201
    
    res_prod = client.get(f"/produtos/{prod_id}")
    assert res_prod.json()["quantidade_em_estoque"] == 0

def test_movimentacao_estoque_insuficiente(client):
    _, _, prod_id = setup_base(client)
    client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10})
    
    res_movs_antes = client.get("/movimentacoes")
    qtd_movs_antes = len(res_movs_antes.json())
    
    response = client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "SAIDA", "quantidade": 11})
    assert response.status_code == 409
    
    body = response.json()
    assert body["status"] == 409
    assert body["error"] == "conflict"
    
    res_prod = client.get(f"/produtos/{prod_id}")
    assert res_prod.json()["quantidade_em_estoque"] == 10
    
    res_movs_depois = client.get("/movimentacoes")
    assert len(res_movs_depois.json()) == qtd_movs_antes

def test_movimentacao_produto_inexistente(client):
    payload = {
        "produto_id": 99999,
        "tipo": "ENTRADA",
        "quantidade": 10
    }
    response = client.post("/movimentacoes", json=payload)
    assert response.status_code == 404
    
    body = response.json()
    assert body["error"] == "not_found"

@pytest.mark.parametrize("quantidade", [0, -1])
def test_movimentacao_quantidade_invalida(client, quantidade):
    _, _, prod_id = setup_base(client)
    payload = {
        "produto_id": prod_id,
        "tipo": "ENTRADA",
        "quantidade": quantidade
    }
    response = client.post("/movimentacoes", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"

def test_movimentacao_tipo_invalido(client):
    _, _, prod_id = setup_base(client)
    payload = {
        "produto_id": prod_id,
        "tipo": "TRANSFERENCIA",
        "quantidade": 10
    }
    response = client.post("/movimentacoes", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"

@pytest.mark.parametrize("campo_invalido", [
    {"id": 999},
    {"data": "2026-01-01T00:00:00Z"},
    {"fornecedor_id": 1}
])
def test_movimentacao_campos_controlados_servidor(client, campo_invalido):
    _, _, prod_id = setup_base(client)
    payload = {
        "produto_id": prod_id,
        "tipo": "ENTRADA",
        "quantidade": 10
    }
    payload.update(campo_invalido)
    response = client.post("/movimentacoes", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"

def test_movimentacao_get_lista(client):
    _, _, prod_id = setup_base(client)
    client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10})
    client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 20})
    
    response = client.get("/movimentacoes")
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_movimentacao_get_por_id(client):
    _, _, prod_id = setup_base(client)
    mov = client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10}).json()
    mov_id = mov["id"]
    
    response = client.get(f"/movimentacoes/{mov_id}")
    assert response.status_code == 200
    assert response.json()["id"] == mov_id
    
    res_invalid = client.get("/movimentacoes/99999")
    assert res_invalid.status_code == 404
    assert res_invalid.json()["error"] == "not_found"

def test_movimentacao_imutabilidade_http_method_not_allowed(client):
    _, _, prod_id = setup_base(client)
    mov_id = client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10}).json()["id"]
    
    res_put = client.put(f"/movimentacoes/{mov_id}", json={})
    assert res_put.status_code == 405
    
    res_patch = client.patch(f"/movimentacoes/{mov_id}", json={})
    assert res_patch.status_code == 405
    
    res_delete = client.delete(f"/movimentacoes/{mov_id}")
    assert res_delete.status_code == 405
    
    res_get = client.get(f"/movimentacoes/{mov_id}")
    assert res_get.status_code == 200

def test_openapi_imutabilidade(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    
    path_item = openapi["paths"].get("/movimentacoes/{movimentacao_id}", {})
    
    assert "get" in path_item
    assert "put" not in path_item
    assert "patch" not in path_item
    assert "delete" not in path_item

def test_movimentacao_fornecedor_historico(client):
    cat_id = criar_categoria(client)
    forn_A_id = criar_fornecedor(client, nome="Fornecedor A", cnpj="11111111111111", email="a@test.com")
    forn_B_id = criar_fornecedor(client, nome="Fornecedor B", cnpj="22222222222222", email="b@test.com")
    
    prod_id = criar_produto(client, cat_id, forn_A_id)
    
    mov_1 = client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10}).json()
    assert mov_1["fornecedor_id"] == forn_A_id
    
    prod_data = client.get(f"/produtos/{prod_id}").json()
    prod_data["fornecedor_id"] = forn_B_id
    res_put = client.put(f"/produtos/{prod_id}", json={
        "nome": prod_data["nome"],
        "sku": prod_data["sku"],
        "preco_custo": prod_data["preco_custo"],
        "preco_venda": prod_data["preco_venda"],
        "estoque_minimo": prod_data["estoque_minimo"],
        "categoria_id": prod_data["categoria_id"],
        "fornecedor_id": forn_B_id
    })
    assert res_put.status_code == 200
    
    mov_2 = client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "SAIDA", "quantidade": 1}).json()
    assert mov_2["fornecedor_id"] == forn_B_id
    
    mov_1_reconsultada = client.get(f"/movimentacoes/{mov_1['id']}").json()
    assert mov_1_reconsultada["fornecedor_id"] == forn_A_id

def test_delete_produto_com_historico(client):
    _, _, prod_id = setup_base(client)
    client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10})
    
    response = client.delete(f"/produtos/{prod_id}")
    assert response.status_code == 409
    
    res_prod = client.get(f"/produtos/{prod_id}")
    assert res_prod.status_code == 200
    
    res_movs = client.get("/movimentacoes")
    assert len(res_movs.json()) >= 1

def test_delete_fornecedor_com_historico(client):
    _, forn_id, prod_id = setup_base(client)
    client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10})
    
    response = client.delete(f"/fornecedores/{forn_id}")
    assert response.status_code == 409
    
    res_forn = client.get(f"/fornecedores/{forn_id}")
    assert res_forn.status_code == 200
