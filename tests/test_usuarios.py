from sqlalchemy import select
from app.models.usuario import Usuario, Role
from app.security.passwords import hash_password
from app.database import SessionLocal

def test_criar_usuario_no_banco():
    # Cria o hash
    senha_plana = "minha-senha"
    senha_hasheada = hash_password(senha_plana)
    
    # Cria o modelo
    usuario = Usuario(
        username="admin_teste",
        password_hash=senha_hasheada,
        role=Role.ADMIN
    )
    
    with SessionLocal() as db_session:
        db_session.add(usuario)
        db_session.commit()
        
        # Valida persistencia
        usuario_db = db_session.scalar(select(Usuario).where(Usuario.username == "admin_teste"))
        
        assert usuario_db is not None
        assert usuario_db.id > 0
        assert usuario_db.username == "admin_teste"
        assert usuario_db.role == "ADMIN"
        assert usuario_db.password_hash == senha_hasheada
        assert usuario_db.password_hash != senha_plana
