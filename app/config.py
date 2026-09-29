from pydantic_settings import BaseSettings, SettingsConfigDict
import urllib.parse

class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        safe_password = urllib.parse.quote(self.db_password, safe="")
        safe_user = urllib.parse.quote(self.db_user, safe="")
        # Utiliza apenas "postgresql" conceitualmente pois o driver final (ex: psycopg/asyncpg) ainda não foi escolhido
        return f"postgresql://{safe_user}:{safe_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()
