import threading
from fastapi.testclient import TestClient
from app.main import app

def test_concorrencia_saida_simultanea(client):
    cat_id = client.post("/categorias", json={"nome": "Cat Concorrencia"}).json()["id"]
    forn_id = client.post("/fornecedores", json={
        "nome": "Forn Concorrencia", "cnpj": "12345678901234", "telefone": "11999999999", "email": "conc@test.com"
    }).json()["id"]
    prod_id = client.post("/produtos", json={
        "nome": "Prod Conc", "sku": "SKU-CONC-1", "preco_custo": "10.00", "preco_venda": "20.00",
        "estoque_minimo": 5, "categoria_id": cat_id, "fornecedor_id": forn_id
    }).json()["id"]
    
    res_in = client.post("/movimentacoes", json={"produto_id": prod_id, "tipo": "ENTRADA", "quantidade": 10})
    assert res_in.status_code == 201

    barrier = threading.Barrier(2)
    results = []
    # Lock for thread-safe append to results list
    list_lock = threading.Lock()

    def worker():
        local_client = TestClient(app, raise_server_exceptions=False)
        try:
            barrier.wait(timeout=5)
        except threading.BrokenBarrierError:
            pass
            
        response = local_client.post("/movimentacoes", json={
            "produto_id": prod_id,
            "tipo": "SAIDA",
            "quantidade": 8
        })
        with list_lock:
            results.append(response.status_code)

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)

    t1.start()
    t2.start()

    t1.join(timeout=10)
    t2.join(timeout=10)

    assert sorted(results) == [201, 409], f"Resultados das threads inconsistentes: {results}"

    res_prod = client.get(f"/produtos/{prod_id}")
    estoque_final = res_prod.json()["quantidade_em_estoque"]
    assert estoque_final == 2
    assert estoque_final >= 0

    res_movs = client.get("/movimentacoes")
    movs_do_produto = [m for m in res_movs.json() if m["produto_id"] == prod_id]
    
    assert len(movs_do_produto) == 2
    entradas = [m for m in movs_do_produto if m["tipo"] == "ENTRADA"]
    saidas = [m for m in movs_do_produto if m["tipo"] == "SAIDA"]
    
    assert len(entradas) == 1
    assert entradas[0]["quantidade"] == 10
    assert len(saidas) == 1
    assert saidas[0]["quantidade"] == 8
