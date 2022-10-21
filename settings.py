from framedork.src.etc.settings import Settings

settings = Settings(
    host="0.0.0.0",
    port=8000,
    db="postgres",
    db_conn={"some_conn": "some_param"},
    deploy="wsgi"
)