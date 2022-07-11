from .dorm import Connector

class Settings:

	def __init__(self, /, host: str, port: int, conns: int, conn_size: int, db: str, db_conn: dict):
		self.host = host
		self.port = port
		self.conns = conns
		self.conn_size = conn_size
		self.db = db
		self.db_conn = db_conn
		self.connector = Connector(db=db, conn_values=db_conn)