def setup_dependencies(client):
    cat_id = client.post("/categorias", json={"nome": "Cat Produto"}).json()["id"]
    forn_id = client.post("/fornecedores", json={
        "nome": "Forn Produto",
        "cnpj": "12345678901234",
        "telefone": "11",
        "email": "fp@test.com"
    }).json()["id"]
    return cat_id, forn_id

def test_produto_post_valid(client):
    cat_id, forn_id = setup_dependencies(client)
    payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    response = client.post("/produtos", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["quantidade_em_estoque"] == 0
    assert "data_cadastro" in body
    assert body["sku"] == "SKU-001"

def test_produto_get_list(client):
    cat_id, forn_id = setup_dependencies(client)
    payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    client.post("/produtos", json=payload)
    
    response = client.get("/produtos")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_produto_get_by_id(client):
    cat_id, forn_id = setup_dependencies(client)
    payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    p_id = client.post("/produtos", json=payload).json()["id"]
    
    response = client.get(f"/produtos/{p_id}")
    assert response.status_code == 200
    assert response.json()["sku"] == "SKU-001"

def test_produto_put_existing(client):
    cat_id, forn_id = setup_dependencies(client)
    payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    body_post = client.post("/produtos", json=payload).json()
    p_id = body_post["id"]
    data_cadastro = body_post["data_cadastro"]
    
    payload["nome"] = "Produto 2"
    payload["preco_venda"] = "30.00"
    payload["estoque_minimo"] = 10
    
    response = client.put(f"/produtos/{p_id}", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["nome"] == "Produto 2"
    assert body["preco_venda"] == "30.00"
    assert body["estoque_minimo"] == 10
    assert body["quantidade_em_estoque"] == 0
    assert body["data_cadastro"] == data_cadastro

def test_produto_delete_existing(client):
    cat_id, forn_id = setup_dependencies(client)
    payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    p_id = client.post("/produtos", json=payload).json()["id"]
    
    response = client.delete(f"/produtos/{p_id}")
    assert response.status_code == 204
    
    res_get = client.get(f"/produtos/{p_id}")
    assert res_get.status_code == 404

def test_produto_post_duplicate_sku(client):
    cat_id, forn_id = setup_dependencies(client)
    payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    client.post("/produtos", json=payload)
    
    payload["nome"] = "Produto Diferente"
    response = client.post("/produtos", json=payload)
    assert response.status_code == 409
    assert response.json()["error"] == "conflict"

def test_produto_put_duplicate_sku(client):
    cat_id, forn_id = setup_dependencies(client)
    p1 = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    p2 = {
        "nome": "Produto 2",
        "sku": "SKU-002",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    client.post("/produtos", json=p1)
    p2_id = client.post("/produtos", json=p2).json()["id"]
    
    p2["sku"] = "SKU-001"
    response = client.put(f"/produtos/{p2_id}", json=p2)
    assert response.status_code == 409
    assert response.json()["error"] == "conflict"

def test_produto_post_invalid_categoria(client):
    cat_id, forn_id = setup_dependencies(client)
    payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": 99999,
        "fornecedor_id": forn_id
    }
    response = client.post("/produtos", json=payload)
    assert response.status_code == 404

def test_produto_post_invalid_fornecedor(client):
    cat_id, forn_id = setup_dependencies(client)
    payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": 99999
    }
    response = client.post("/produtos", json=payload)
    assert response.status_code == 404

def test_produto_put_invalid_categoria(client):
    cat_id, forn_id = setup_dependencies(client)
    payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    p_id = client.post("/produtos", json=payload).json()["id"]
    payload["categoria_id"] = 99999
    response = client.put(f"/produtos/{p_id}", json=payload)
    assert response.status_code == 404

def test_produto_put_invalid_fornecedor(client):
    cat_id, forn_id = setup_dependencies(client)
    payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    p_id = client.post("/produtos", json=payload).json()["id"]
    payload["fornecedor_id"] = 99999
    response = client.put(f"/produtos/{p_id}", json=payload)
    assert response.status_code == 404

def test_produto_post_protected_fields(client):
    cat_id, forn_id = setup_dependencies(client)
    base_payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    
    # Extra field: quantidade_em_estoque
    p1 = base_payload.copy()
    p1["quantidade_em_estoque"] = 10
    assert client.post("/produtos", json=p1).status_code == 422
    
    # Extra field: data_cadastro
    p2 = base_payload.copy()
    p2["data_cadastro"] = "2026-01-01T00:00:00Z"
    assert client.post("/produtos", json=p2).status_code == 422
    
    # Extra field: id
    p3 = base_payload.copy()
    p3["id"] = 999
    assert client.post("/produtos", json=p3).status_code == 422

def test_produto_put_protected_fields(client):
    cat_id, forn_id = setup_dependencies(client)
    payload = {
        "nome": "Produto 1",
        "sku": "SKU-001",
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": 5,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }
    p_id = client.post("/produtos", json=payload).json()["id"]
    
    payload["quantidade_em_estoque"] = 10
    assert client.put(f"/produtos/{p_id}", json=payload).status_code == 422
