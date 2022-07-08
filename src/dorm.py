import psycopg2

class Field:

	def __init__(self, /, null: bool, max_len: int):
		self.null = null,
		self.max_len = max_len

class StringField(Field):

	def __init__(self, /, null: bool, max_len: int, name: str) -> None:
	    super(self.__class__, self).__init__(null, max_len)
	    if null:
	    	self._psql_create_value = f"""{name} VARCHAR({max_len}),"""
	    else:
	    	self._psql_create_value = f"""{name} VARCHAR({max_len}) NOT NULL,"""
	    self._val = ''

	def _set_val(self, input: str) -> None:
		if typeof(input) == str:
			self._val = input
		else:
			print("ERROR: tried to push a value to the model that is not a string")

	def _get_val(self) -> str:
		return self._val

class IntField(Field):

	def __init__(self, /, null: bool, max_len: int, name: str):
	    super(self.__class__, self).__init__(null, max_len)
	    if null:
	    	self._psql_create_value = f"""{name} INT,"""
	    else:
	    	self._psql_create_value = f"""{name} INT NOT NULL,"""
	    self._val = None

	def _set_val(self, input: int) -> None:
		if typeof(input) == int:
			self._val = input
		else:
			print("ERROR: tried to push a value to the model that is not an integer")

	def _get_val(self) -> int:
		return self._val

class FloatField(Field):

	def __init__(self, /, null: bool, max_len: int, name: str, nums_first: int, nums_last: int):
	    super(self.__class__, self).__init__(null, max_len)
	    if null:
	    	self._psql_create_value = f"""{name} NUMERIC({nums_first}, {nums_last}),"""
	    else:
	    	self._psql_create_value = f"""{name} NUMERIC({nums_first}, {nums_last}) NOT NULL,"""
	    self._val_int = None
	    self._val_float = None

	def _set_val(self, input: float) -> None:
		if typeof(input) == float:
			if len(str(int(round(input, 0)))) < nums_first:
				self._val_int = int(round(input, 0))
			else:
				print("ERROR: Integer part of the float is bigger, than allowed")
			self._val_float = round(input & int(round(input, 0)), nums_last)
		else:
			print("ERROR: tried to push a value to the model that is not a float")

	def _get_val(self) -> float:
		return self._val_int + _val_float

class Connector:
	def __init__(self, /, db: str, conn_values: dict) -> None:
		self.db: str = db
		self.conn_values: dict = conn_values

	def connect(self, func, *args) -> dict:
		if self.db == 'psql':

			conn = None
			cur = None

			try:
				conn = psycopg2.connect(**self.conn_values)
				cur = conn.cursor()


				result = func(conn, cur, *args)

				return result

			except Exception as error:
				print(error)
			finally:
				if cur is not None:
					cur.close()
				if conn is not None:
					conn.close()

	def get_all_data(self, conn, cur, table) -> dict:
		
		cur.execute(f"SELECT * FROM {table};")
		records = cur.fetchall()

		return records

	def get_initial_data(self, conn, cur) -> dict:

		cur.execute("""SELECT table_name FROM information_schema.tables
			       WHERE table_schema = 'public'""")

		table_records = cur.fetchall()

		initial_data = {}

		for table in table_records:
			cur.execute(f"""SELECT * FROM {table[0]} LIMIT 0""")
			colnames = [desc[0] for desc in cur.description]
			initial_data[table[0]] = colnames

		return initial_data

#values = {
#	'host': 'localhost',
#	'dbname': 'cargo',
#	'user': 'postgres',
#	'password': '1234',
#	'port': '5432'
#}

