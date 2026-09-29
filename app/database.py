from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Engine é a infraestrutura central que gerencia o pool de conexões com o banco.
engine = create_engine(
    settings.database_url.render_as_string(hide_password=False)
)

# SessionLocal é uma fábrica de instâncias da unidade de trabalho (Session).
SessionLocal = sessionmaker(
    bind=engine
)
