from app.security.passwords import hash_password, verify_password

def test_hash_nao_deve_ser_texto_plano():
    senha = "senha-teste"
    hash_senha = hash_password(senha)
    
    assert hash_senha != senha
    assert "senha-teste" not in hash_senha

def test_verify_password_correta_retorna_true():
    senha = "senha-secreta"
    hash_senha = hash_password(senha)
    
    assert verify_password(senha, hash_senha) is True

def test_verify_password_incorreta_retorna_false():
    senha = "senha-secreta"
    hash_senha = hash_password(senha)
    
    assert verify_password("outra-senha", hash_senha) is False
