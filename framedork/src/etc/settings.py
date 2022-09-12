from ..DORM.dorm import Connector


class Settings:

    def __init__(self, /, host: str = "127.0.0.1", port: int = 8000, conns: int = 10, 
                    conn_size: int = 1024, db: str = None, db_conn: dict = None,
                    deploy: str = 'Local'):
        self.host = host
        self.port = port
        self.conns = conns
        self.conn_size = conn_size
        self.db = db
        self.db_conn = db_conn
        self.connector = Connector(db=db, conn_values=db_conn)
        self.deploy = deploy
