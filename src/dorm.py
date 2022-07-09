from datetime import datetime
from math import floor
import psycopg2

class Field:

	def __init__(self, /, null: bool, max_len: int):
		self.null = null,
		self.max_len = max_len

class StringField(Field):

	def __init__(self, /, null: bool = True, max_len: int = 1000, name: str = '') -> None:
		super(self.__class__, self).__init__(null, max_len)
		self.name = name
		if null:
			self._psql_create_value = f"""{name} VARCHAR({max_len}),"""
		else:
			self._psql_create_value = f"""{name} VARCHAR({max_len}) NOT NULL,"""
		self._val = ''

	def _set_val(self, input: str) -> None:
		if type(input) == str:
			self._val = input
		else:
			print("ERROR: tried to push a value to the model that is not a string")

	def _get_val(self) -> str:
		return self._val

class IntField(Field):

	def __init__(self, /, null: bool = True, max_len: int = 1000, name: str = '') -> None:
		super(self.__class__, self).__init__(null, max_len)
		self.name = name
		if null:
			self._psql_create_value = f"""{name} INT,"""
		else:
			self._psql_create_value = f"""{name} INT NOT NULL,"""
		self._val = None

	def _set_val(self, input: int) -> None:
		if type(input) == int:
			self._val = input
		else:
			print("ERROR: tried to push a value to the model that is not an integer")

	def _get_val(self) -> int:
		return self._val

class FloatField(Field):

	def __init__(self, /, null: bool = True, max_len: int = 1000, name: str = '', nums_first: int = 0, nums_last: int = 0) -> None:
		super(self.__class__, self).__init__(null, max_len)
		self.name = name
		if null:
			self._psql_create_value = f"""{name} NUMERIC({nums_first}, {nums_last}),"""
		else:
			self._psql_create_value = f"""{name} NUMERIC({nums_first}, {nums_last}) NOT NULL,"""
		self.nums_first = nums_first
		self.nums_last = nums_last
		self._val_int = None
		self._val_float = None

	def _set_val(self, input: float) -> None:
		if type(input) == float:
			if len(str(int(floor(input)))) <= self.nums_first:
				self._val_int = int(floor(input))
			else:
				print("ERROR: Integer part of the float is bigger, than allowed")
			self._val_float = round(input % int(floor(input)), self.nums_last)
		else:
			print("ERROR: tried to push a value to the model that is not a float")

	def _get_val(self) -> float:
		return self._val_int + self._val_float

class DateField(Field):

	def __init__(self, /, null: bool = True, max_len: int = 1000, name: str = '', default_current_date: bool = False) -> None:
		super(self.__class__, self).__init__(null, max_len)
		self.name = name
		if null:
			if default_current_date:
				self._psql_create_value = f"""{name} DATE DEFAULT CURRENT_DATE,"""
			else:
				self._psql_create_value = f"""{name} DATE,"""
		else:
			if default_current_date:
				self._psql_create_value = f"""{name} DATE NOT NULL DEFAULT CURRENT_DATE,"""
			else:
				self._psql_create_value = f"""{name} DATE NOT NULL,"""
		self._val = None

	def _set_val(self, input) -> None:
		self._val = input

	def _get_val(self) -> datetime.date:
		return self._val

class Model:
	def __init__(self, /, table: str, fields: list) -> None:
		self.table = table
		self.fields = fields
		self.connector = None

	# Inner methods for working within the class or from the framework

	def _register(self, connector):
		self.connector = connector

		_ = self.connector.connect(self._connect)

	def _create(self, conn, cur) -> int:

		create_list = [field._psql_create_value for field in self.fields]

		script = f"CREATE TABLE {self.table} (\n"

		for i, line in enumerate(create_list):
			if i == len(create_list) -1:
				script += '\t' + line[:-1] + '\n'
			else:
				script += '\t' + line + '\n'
		else:
			script += ');'

		cur.execute(script)
		conn.commit()

		return {}

	def _connect(self, conn, cur) -> int:

		cur.execute("""SELECT table_name FROM information_schema.tables
				   WHERE table_schema = 'public'""")

		if (f'{self.table}',) not in cur.fetchall():
			result = self._create(conn, cur)

			return result

		return {}

	def _add_vals(self, values: dict) -> None:
		for field in self.fields:
			field._set_val(values[field.name])
			print(field._get_val())

	def _write_row(self, conn, cur) -> int:

		name_list = [field.name for field in self.fields]
		value_list = [field._get_val() for field in self.fields]

		script = f"INSERT INTO {self.table} ("
		for i, name in enumerate(name_list):
			if i == len(name_list) - 1:
				script += name
			else:
				script += name + ', '
		else:
			script += ')\n'

		script += 'VALUES ('

		for i, value in enumerate(value_list):
			if i == len(value_list) - 1:
				if type(value) == str or (type(value) != int and type(value) != float):
					script += "'" + value + "'"
				else:
					script += str(value)
			else:
				if type(value) == str or (type(value) != int and type(value) != float):
					script += "'" + str(value) + "'" + ', '
				else:
					script += str(value) + ', '
		else:
			script += ');'

		cur.execute(script)
		conn.commit()

		return 1

	def _get_all_rows(self, conn, cur) -> list:

		script = f"""SELECT * FROM {self.table}"""

		cur.execute(script)

		result = cur.fetchall()

		queryset = []

		for one in result:
			query = {}
			for i, entry in enumerate(one):
				query[self.fields[i].name] = entry

			queryset.append(query)

		return queryset

	def _get_row_by_params(self, conn, cur, params: dict) -> list:

		script = f"""SELECT * FROM {self.table}"""

		if params != {}:
			script += "\nWHERE"
			for i, field in enumerate(self.fields):
				try:
					if type(params[field.name]) == int or type(params[field.name]) == float:
						script += f' {field.name} = {params[field.name]} AND'
					else:
						script += f" {field.name} = '{params[field.name]}' AND"
				except KeyError:
					continue
			else:
				script = script[:-4]
				script += ';'

		cur.execute(script)
		result = cur.fetchall()

		queryset = []
		for one in result:
			query = {}
			for i, entry in enumerate(one):
				query[self.fields[i].name] = entry
			queryset.append(query)

		return queryset

	# Methods for high-level handling inside the web program.

	def get(self) -> list:

		result = self.connector.connect(self._get_all_rows)

		return result

	def filter(self, params: dict) -> list:

		result = self.connector.connect(self._get_row_by_params, params)

		return result

	def add(self, vals: dict) -> None:

		self._add_vals(vals)

	def save(self) -> None:

		result = self.connector.connect(self._write_row)

class Connector:
	def __init__(self, /, db: str, conn_values: dict) -> None:
		self.db: str = db
		self.conn_values: dict = conn_values

	def connect(self, func, *args) -> any:
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

		for table in table_records:
			cur.execute(f"""SELECT * FROM {table[0]} LIMIT 0""")
			colnames = [desc[0] for desc in cur.description]
			initial_data[table[0]] = colnames

		return initial_data

# Testing

#values = {
#	'host': 'localhost',
#	'dbname': 'orm_test',
#	'user': 'postgres',
#	'password': '1234',
#	'port': '5432'
#}

#c = Connector(db='psql', conn_values=values)

#result = c.connect(m.get_row_by_params, params)

#print(result)

#animal = Model(table='animal', fields=[
#		StringField(null=False, max_len=20, name='name'),
#		StringField(null=False, max_len=30, name='species'),
#		IntField(name='life_expectancy')
#	])

#animal._register(c)

#vals1 = {'name': 'Hyena', 'species': 'Hyaenidae', 'life_expectancy': 30}
#vals2 = {'name': 'Elephant', 'species': 'Cool', 'life_expectancy': 60}
#vals3 = {'name': 'Human', 'species': 'Homo', 'life_expectancy': 80}
#vals4 = {'name': 'Dog', 'species': 'Cute', 'life_expectancy': 15}
#vals5 = {'name': 'Mouse', 'species': 'Snich', 'life_expectancy': 3}
#vals6 = {'name': 'Cat', 'species': 'Cute', 'life_expectancy': 15}

#animal.add(vals1)
#animal.save()

#animal.add(vals2)
#animal.save()

#animal.add(vals3)
#animal.save()

#animal.add(vals4)
#animal.save()

#animal.add(vals5)
#animal.save()

#animal.add(vals6)
#animal.save()

#result = animal.filter({'name': 'Dog'})

#print(result)