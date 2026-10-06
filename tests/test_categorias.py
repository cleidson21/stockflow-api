def test_categoria_post_valid(client):
    response = client.post("/categorias", json={"nome": "Eletrônicos"})
    assert response.status_code == 201
    body = response.json()
    assert body["nome"] == "Eletrônicos"
    assert "id" in body

def test_categoria_get_list(client):
    client.post("/categorias", json={"nome": "C1"})
    response = client.get("/categorias")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["nome"] == "C1"

def test_categoria_get_by_id(client):
    cat_id = client.post("/categorias", json={"nome": "C1"}).json()["id"]
    response = client.get(f"/categorias/{cat_id}")
    assert response.status_code == 200
    assert response.json()["nome"] == "C1"

def test_categoria_put_existing(client):
    cat_id = client.post("/categorias", json={"nome": "C1"}).json()["id"]
    response = client.put(f"/categorias/{cat_id}", json={"nome": "C2"})
    assert response.status_code == 200
    assert response.json()["nome"] == "C2"

def test_categoria_delete_existing(client):
    cat_id = client.post("/categorias", json={"nome": "C1"}).json()["id"]
    response = client.delete(f"/categorias/{cat_id}")
    assert response.status_code == 204
    
    res_get = client.get(f"/categorias/{cat_id}")
    assert res_get.status_code == 404
    assert res_get.json()["error"] == "not_found"

def test_categoria_post_duplicate_name(client):
    client.post("/categorias", json={"nome": "C1"})
    response = client.post("/categorias", json={"nome": "C1"})
    assert response.status_code == 409
    assert response.json()["error"] == "conflict"

def test_categoria_put_duplicate_name(client):
    client.post("/categorias", json={"nome": "C1"})
    cat_id = client.post("/categorias", json={"nome": "C2"}).json()["id"]
    response = client.put(f"/categorias/{cat_id}", json={"nome": "C1"})
    assert response.status_code == 409
    assert response.json()["error"] == "conflict"
