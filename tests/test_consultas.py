import pytest
from datetime import datetime, timezone, timedelta

def criar_categoria(client):
    return client.post("/categorias", json={"nome": "Cat Consultas"}).json()["id"]

def criar_fornecedor(client, nome="Forn Consultas", cnpj="12345678901234", email="c@test.com"):
    return client.post("/fornecedores", json={
        "nome": nome,
        "cnpj": cnpj,
        "telefone": "11999999999",
        "email": email
    }).json()["id"]

def criar_produto(client, cat_id, forn_id, nome="Prod Consultas", sku="SKU-C1", estoque_min=5):
    return client.post("/produtos", json={
        "nome": nome,
        "sku": sku,
        "preco_custo": "10.00",
        "preco_venda": "20.00",
        "estoque_minimo": estoque_min,
        "categoria_id": cat_id,
        "fornecedor_id": forn_id
    }).json()["id"]

def registrar_entrada(client, prod_id, qtd):
    return client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": qtd}).json()

def test_consultas_estoque_minimo(client):
    cat_id = criar_categoria(client)
    forn_id = criar_fornecedor(client)
    
    # A: estoque_minimo=5, saldo=5 (deve retornar)
    prod_A = criar_produto(client, cat_id, forn_id, "A", "SKU-A", 5)
    registrar_entrada(client, prod_A, 5)
    
    # B: estoque_minimo=5, saldo=3 (deve retornar)
    prod_B = criar_produto(client, cat_id, forn_id, "B", "SKU-B", 5)
    registrar_entrada(client, prod_B, 3)
    
    # C: estoque_minimo=5, saldo=6 (nao deve retornar)
    prod_C = criar_produto(client, cat_id, forn_id, "C", "SKU-C", 5)
    registrar_entrada(client, prod_C, 6)
    
    response = client.get("/produtos/consultas/estoque-minimo")
    assert response.status_code == 200
    ids_retornados = [p["id"] for p in response.json()]
    assert prod_A in ids_retornados
    assert prod_B in ids_retornados
    assert prod_C not in ids_retornados

def test_consultas_filtro_data_inicio(client):
    cat_id = criar_categoria(client)
    forn_id = criar_fornecedor(client)
    prod_id = criar_produto(client, cat_id, forn_id, "D", "SKU-D", 5)
    
    m1 = registrar_entrada(client, prod_id, 10)
    
    response = client.get(f"/movimentacoes?data_inicio={m1["data"].replace("+", "%2B")}")
    assert response.status_code == 200
    ids = [m["id"] for m in response.json()]
    assert m1["id"] in ids

def test_consultas_filtro_data_fim(client):
    cat_id = criar_categoria(client)
    forn_id = criar_fornecedor(client)
    prod_id = criar_produto(client, cat_id, forn_id, "E", "SKU-E", 5)
    
    m1 = registrar_entrada(client, prod_id, 10)
    
    response = client.get(f"/movimentacoes?data_fim={m1["data"].replace("+", "%2B")}")
    assert response.status_code == 200
    ids = [m["id"] for m in response.json()]
    assert m1["id"] in ids

def test_consultas_intervalo_completo(client):
    cat_id = criar_categoria(client)
    forn_id = criar_fornecedor(client)
    prod_id = criar_produto(client, cat_id, forn_id, "F", "SKU-F", 5)
    
    m1 = registrar_entrada(client, prod_id, 10)
    
    response = client.get(f"/movimentacoes?data_inicio={m1["data"].replace("+", "%2B")}&data_fim={m1["data"].replace("+", "%2B")}")
    assert response.status_code == 200
    ids = [m["id"] for m in response.json()]
    assert m1["id"] in ids

def test_consultas_timezone(client):
    cat_id = criar_categoria(client)
    forn_id = criar_fornecedor(client)
    prod_id = criar_produto(client, cat_id, forn_id, "G", "SKU-G", 5)
    
    m1 = registrar_entrada(client, prod_id, 10)
    
    dt_utc = datetime.fromisoformat(m1["data"].replace('Z', '+00:00'))
    dt_br = dt_utc.astimezone(timezone(timedelta(hours=-3)))
    
    data_br_str = dt_br.isoformat().replace("+", "%2B")
    
    response = client.get(f"/movimentacoes?data_inicio={data_br_str}&data_fim={data_br_str}")
    assert response.status_code == 200
    ids = [m["id"] for m in response.json()]
    assert m1["id"] in ids

def test_consultas_intervalo_invalido(client):
    inicio = "2026-10-10T10:00:00Z"
    fim = "2026-10-01T10:00:00Z"
    
    response = client.get(f"/movimentacoes?data_inicio={inicio}&data_fim={fim}")
    assert response.status_code == 400
    body = response.json()
    assert body["status"] == 400
    assert body["error"] == "bad_request"
    assert "message" in body

def test_consultas_sem_resultados(client):
    futuro = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat().replace("+", "%2B")
    response = client.get(f"/movimentacoes?data_inicio={futuro}")
    assert response.status_code == 200
    assert response.json() == []

def test_consultas_fornecedor_historico(client):
    cat_id = criar_categoria(client)
    forn_A = criar_fornecedor(client, "A", "11111111111111", "a@test.com")
    forn_B = criar_fornecedor(client, "B", "22222222222222", "b@test.com")
    
    prod_id = criar_produto(client, cat_id, forn_A, "H", "SKU-H", 5)
    m1 = registrar_entrada(client, prod_id, 10)
    
    p = client.get(f"/produtos/{prod_id}").json()
    p_put = {
        "nome": p["nome"],
        "sku": p["sku"],
        "preco_custo": p["preco_custo"],
        "preco_venda": p["preco_venda"],
        "estoque_minimo": p["estoque_minimo"],
        "categoria_id": p["categoria_id"],
        "fornecedor_id": forn_B
    }
    client.put(f"/produtos/{prod_id}", json=p_put)
    
    m2 = registrar_entrada(client, prod_id, 10)
    
    rA = client.get(f"/movimentacoes?fornecedor_id={forn_A}")
    assert rA.status_code == 200
    ids_A = [m["id"] for m in rA.json()]
    assert m1["id"] in ids_A
    assert m2["id"] not in ids_A
    
    rB = client.get(f"/movimentacoes?fornecedor_id={forn_B}")
    assert rB.status_code == 200
    ids_B = [m["id"] for m in rB.json()]
    assert m2["id"] in ids_B
    assert m1["id"] not in ids_B

def test_consultas_fornecedor_inexistente(client):
    response = client.get("/movimentacoes?fornecedor_id=99999")
    assert response.status_code == 404
    body = response.json()
    assert body["status"] == 404
    assert body["error"] == "not_found"

def test_consultas_filtros_combinados(client):
    cat_id = criar_categoria(client)
    forn_id = criar_fornecedor(client, "Comb", "33333333333333", "comb@test.com")
    prod_id = criar_produto(client, cat_id, forn_id, "I", "SKU-I", 5)
    
    m1 = registrar_entrada(client, prod_id, 10)
    
    url = f"/movimentacoes?fornecedor_id={forn_id}&data_inicio={m1["data"].replace("+", "%2B")}&data_fim={m1["data"].replace("+", "%2B")}"
    response = client.get(url)
    assert response.status_code == 200
    ids = [m["id"] for m in response.json()]
    assert m1["id"] in ids

def test_consultas_query_parameter_invalido(client):
    response = client.get("/movimentacoes?fornecedor_id=abc")
    assert response.status_code == 422
    body = response.json()
    assert body["status"] == 422
    assert body["error"] == "validation_error"
    assert "message" in body
    assert isinstance(body.get("details"), list)
    for detail in body["details"]:
        assert "loc" in detail
        assert "msg" in detail
        assert "type" in detail
        assert "input" not in detail
