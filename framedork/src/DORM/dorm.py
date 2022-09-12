from datetime import datetime
from math import floor
import psycopg2


class Field:

    def __init__(self, /, null: bool, max_len: int):
        self.null = null,
        self.max_len = max_len


class IDField(Field):

    def __init__(self, /, null: bool = False, max_len: int = 1000):
        super(self.__class__, self).__init__(null, max_len)
        self.name = 'id'
        self._psql_create_value = """id INT GENERATED ALWAYS AS IDENTITY,"""
        self._val = None

    def _set_val(self, input: int) -> None:
        if type(input) == int:
            self._val = input
        else:
            print("ERROR: tried to push a value to the model that is not an integer")

    def _get_val(self) -> int:
        return self._val


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

    def __init__(self, /, null: bool = True, max_len: int = 1000, name: str = '', nums_first: int = 0,
                 nums_last: int = 0) -> None:
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

    def __init__(self, /, null: bool = True, max_len: int = 1000, name: str = '',
                 default_current_date: bool = False) -> None:
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
        self.fields = [IDField(), *fields]
        self.connector = None

    # Inner methods for working within the class or from the framework

    def _register(self, connector):
        self.connector = connector

        _ = self.connector.connect(self._connect)

    def _create(self, conn, cur) -> int:

        create_list = [field._psql_create_value for field in self.fields]

        script = f"""CREATE TABLE {self.table} (\n"""

        for i, line in enumerate(create_list):
            if i == len(create_list) - 1:
                script += '\t' + line[:-1] + '\n'
            else:
                script += '\t' + line + '\n'
        else:
            script += ');'

        cur.execute(script)
        conn.commit()

        self.fields.append(IntField())

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
            try:
                field._set_val(values[field.name])
            except KeyError:
                continue

    def _write_row(self, conn, cur) -> int:

        name_list = [field.name for field in self.fields]
        value_list = [field._get_val() for field in self.fields]

        script = f"INSERT INTO {self.table} ("
        for i, name in enumerate(name_list[1:]):
            if i == len(name_list[1:]) - 1:
                script += name
            else:
                script += name + ', '
        else:
            script += ')\n'

        script += 'VALUES ('

        for i, value in enumerate(value_list[1:]):
            if i == len(value_list[1:]) - 1:
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

    def _update_row(self, conn, cur) -> int:

        value_list = [field._get_val() for field in self.fields[1:]]

        script = f"""UPDATE {self.table} SET ("""

        for field in self.fields[1:]:
            script += field.name + ', '
        else:
            script = script[:-2]
            script += ') = ('

        for value in value_list:
            if type(value) == str or (type(value) != int and type(value) != float):
                script += "'" + str(value) + "'" + ", "
            else:
                script += str(value) + ', '
        else:
            script = script[:-2]
            script += ")\n"

        script += f'WHERE id = {self.fields[0]._get_val()};'

        print(script)

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

    def _delete_by_param(self, conn, cur, params: dict) -> int:
        script = f"""DELETE FROM {self.table}\nWHERE"""

        for field in self.fields:
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
        conn.commit()

        return 1

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
        check = self.connector.connect(self._get_all_rows)
        print(check)

        for one in check:
            if one['id'] == self.fields[0]._val:
                result = self.connector.connect(self._update_row)
                break
        else:
            result = self.connector.connect(self._write_row)

    def delete(self, params: dict) -> None:

        result = self.connector.connect(self._delete_by_param, params)


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
