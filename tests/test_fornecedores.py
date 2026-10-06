def test_fornecedor_post_valid(client):
    payload = {
        "nome": "Fornecedor 1",
        "cnpj": "11111111111111",
        "telefone": "11999999999",
        "email": "contato1@fornecedor.com"
    }
    response = client.post("/fornecedores", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["nome"] == "Fornecedor 1"
    assert "id" in body

def test_fornecedor_get_list(client):
    payload = {
        "nome": "Fornecedor 1",
        "cnpj": "11111111111111",
        "telefone": "11999999999",
        "email": "contato1@fornecedor.com"
    }
    client.post("/fornecedores", json=payload)
    response = client.get("/fornecedores")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_fornecedor_get_by_id(client):
    payload = {
        "nome": "Fornecedor 1",
        "cnpj": "11111111111111",
        "telefone": "11999999999",
        "email": "contato1@fornecedor.com"
    }
    f_id = client.post("/fornecedores", json=payload).json()["id"]
    response = client.get(f"/fornecedores/{f_id}")
    assert response.status_code == 200
    assert response.json()["cnpj"] == "11111111111111"

def test_fornecedor_put_existing(client):
    payload = {
        "nome": "Fornecedor 1",
        "cnpj": "11111111111111",
        "telefone": "11999999999",
        "email": "contato1@fornecedor.com"
    }
    f_id = client.post("/fornecedores", json=payload).json()["id"]
    
    payload["nome"] = "Fornecedor Alterado"
    response = client.put(f"/fornecedores/{f_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["nome"] == "Fornecedor Alterado"

def test_fornecedor_delete_existing(client):
    payload = {
        "nome": "Fornecedor 1",
        "cnpj": "11111111111111",
        "telefone": "11999999999",
        "email": "contato1@fornecedor.com"
    }
    f_id = client.post("/fornecedores", json=payload).json()["id"]
    
    response = client.delete(f"/fornecedores/{f_id}")
    assert response.status_code == 204
    
    res_get = client.get(f"/fornecedores/{f_id}")
    assert res_get.status_code == 404
    assert res_get.json()["error"] == "not_found"

def test_fornecedor_post_duplicate_cnpj(client):
    payload = {
        "nome": "Fornecedor 1",
        "cnpj": "11111111111111",
        "telefone": "11999999999",
        "email": "contato1@fornecedor.com"
    }
    client.post("/fornecedores", json=payload)
    
    payload["email"] = "contato2@fornecedor.com"
    response = client.post("/fornecedores", json=payload)
    assert response.status_code == 409
    assert response.json()["error"] == "conflict"

def test_fornecedor_post_duplicate_email(client):
    payload = {
        "nome": "Fornecedor 1",
        "cnpj": "11111111111111",
        "telefone": "11999999999",
        "email": "contato1@fornecedor.com"
    }
    client.post("/fornecedores", json=payload)
    
    payload["cnpj"] = "22222222222222"
    response = client.post("/fornecedores", json=payload)
    assert response.status_code == 409
    assert response.json()["error"] == "conflict"

def test_fornecedor_put_duplicate_cnpj(client):
    p1 = {
        "nome": "F1", "cnpj": "11111111111111",
        "telefone": "11", "email": "e1@test.com"
    }
    p2 = {
        "nome": "F2", "cnpj": "22222222222222",
        "telefone": "22", "email": "e2@test.com"
    }
    client.post("/fornecedores", json=p1)
    f2_id = client.post("/fornecedores", json=p2).json()["id"]
    
    p2["cnpj"] = "11111111111111"
    response = client.put(f"/fornecedores/{f2_id}", json=p2)
    assert response.status_code == 409
    assert response.json()["error"] == "conflict"

def test_fornecedor_put_duplicate_email(client):
    p1 = {
        "nome": "F1", "cnpj": "11111111111111",
        "telefone": "11", "email": "e1@test.com"
    }
    p2 = {
        "nome": "F2", "cnpj": "22222222222222",
        "telefone": "22", "email": "e2@test.com"
    }
    client.post("/fornecedores", json=p1)
    f2_id = client.post("/fornecedores", json=p2).json()["id"]
    
    p2["email"] = "e1@test.com"
    response = client.put(f"/fornecedores/{f2_id}", json=p2)
    assert response.status_code == 409
    assert response.json()["error"] == "conflict"
