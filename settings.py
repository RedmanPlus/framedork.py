from src.etc.settings import Settings

DB_CONNECTION = {
    "host": "localhost"
}

settings = Settings(
    port=8000,
    db="postgres",
    db_conn=DB_CONNECTION,
    deploy="wsgi"
)