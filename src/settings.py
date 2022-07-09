from .dorm import Connector

class Settings:

	def __init__(self, /, db: str, db_conn: dict):
		self.db = db
		self.db_conn = db_conn
		self.connector = Connector(db=db, conn_values=db_conn)