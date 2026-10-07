import argparse
import getpass
import sys
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.usuario import Usuario, Role
from app.security.passwords import hash_password

def main():
    parser = argparse.ArgumentParser(description="Criar um novo usuario")
    parser.add_argument("--username", required=True, help="Nome de usuario")
    parser.add_argument("--role", required=True, choices=["ADMIN", "FUNCIONARIO"], help="Role do usuario")
    
    args = parser.parse_args()
    
    with SessionLocal() as db:
        stmt = select(Usuario).where(Usuario.username == args.username)
        existente = db.execute(stmt).scalar_one_or_none()
        
        if existente:
            print(f"Erro: Usuario '{args.username}' ja existe.")
            sys.exit(1)
            
        senha = getpass.getpass("Senha: ")
        senha_confirma = getpass.getpass("Confirme a senha: ")
        
        if senha != senha_confirma:
            print("Erro: As senhas nao coincidem.")
            sys.exit(1)
            
        if not senha:
            print("Erro: A senha nao pode ser vazia.")
            sys.exit(1)
            
        novo_usuario = Usuario(
            username=args.username,
            password_hash=hash_password(senha),
            role=args.role
        )
        
        db.add(novo_usuario)
        try:
            db.commit()
            print(f"Usuario '{args.username}' criado com sucesso com role '{args.role}'.")
        except IntegrityError as e:
            db.rollback()
            if hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
                print(f"Erro: O username '{args.username}' ja esta em uso.")
                sys.exit(1)
            else:
                print("Erro inesperado no banco de dados.")
                sys.exit(1)

if __name__ == "__main__":
    main()
