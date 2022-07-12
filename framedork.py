import socket
import json
from src.settings import Settings
from src.preprocessor import insert_values_into_html
from src.dorm import Connector, Model, StringField, IntField, FloatField, DateField

RESPONSE_CODES = {
	200: "HTTP/1.1 200 OK\r\n",
	400: "HTTP/1.1 400 BAD_REQUEST\r\n",
	404: "HTTP/1.1 404 NOT_FOUND\r\n",
	405: "HTTP/1.1 405 Method not allowed\r\n",
	500: "HTTP/1.1 500 Internal server error\r\n"
}

PAGES = {}
DEBUG = False
SETTINGS = None

def set_debug(debug: bool) -> None:
	global DEBUG
	DEBUG = debug

def set_settings(host: str = '', port: int = 8080, conns: int = 1, conn_size: int = 1024, db: str = '', db_conn: dict = {}) -> None:
	global SETTINGS
	SETTINGS = Settings(host=host, port=port, conns=conns, conn_size=conn_size, db=db, db_conn=db_conn)

def register_model(models: list) -> None:
	connector = Connector(db=SETTINGS.db, conn_values=SETTINGS.db_conn)
	for model in models:
		model._register(connector)

def register(content: str, addr: str, methods: list):
	def decorator(func):
		def wrapper(*args, **kwargs):
			PAGES[addr] = [methods, func, content]

		return wrapper
	return decorator

def get_url_params(addr: str) -> tuple:
	if '?' in addr:
		params_dict = {}
		addr = addr.split('?')
		params, addr = addr[1].split('&'), addr[0]
		for param in params:
			param = param.split('=')
			head, body = param[0], param[1]
			try:
				params_dict[head] = int(body)
			except ValueError:
				if body == 'true':
					params_dict[head] = True
				elif body == 'false':
					params_dict[head] = False
				else:
					params_dict[head] = body.replace('%20', ' ')

		return (addr, params_dict)
	
	return (addr, {})

def parse_post_body(request: dict):
	if request['CONTENT-TYPE'] == 'application/x-www-form-urlencoded':
		request['BODY'] = '?' + request['BODY'][0][0]
		_, body = get_url_params(request['BODY'])
		request['BODY'] = body
	elif request['CONTENT-TYPE'] == 'application/json':
		body = {}
		for line in request['BODY']:
			if line[0] == '{' or line[0] == '}':
				continue
			else:
				line[0] = line[0].lstrip().replace('"', '')
				line[1] = line[1].replace('"', '').replace(',', '')
				try:
					if '.' in line[1]:
						body[line[0]] = float(line[1])
					else:
						body[line[0]] = int(line[1])
				except ValueError:
					body[line[0]] = line[1]

		request['BODY'] = body

def request_parse(request: bytes) -> dict:
	return_dict = {}
	request = request.split('\r\n')
	empty_line_count = 0
	for line in request:
		if DEBUG:
			print(line)
		line = line.split(': ')
		if len(line) == 1 and line[0] != '' :
			if empty_line_count == 0:			
				line = line[0].split(' ')
				method, addr, protocol = line[0], line[1], line[2]
				addr = get_url_params(addr)
				return_dict['METHOD'] = method
				return_dict['ADDR'] = addr[0]
				return_dict['PROTOCOL'] = protocol
				return_dict['PARAMS'] = addr[1]
			else:
				return_dict['BODY'].append(line)
		elif line[0] == '':
			if empty_line_count == 0:
				return_dict['BODY'] = []

			empty_line_count += 1
		else:
			if empty_line_count < 1:
				head, body = line[0], line[1]
				return_dict[head.upper()] = body
			else:
				return_dict['BODY'].append(line)

	if return_dict['METHOD'] != 'GET':
		parse_post_body(return_dict)

	return return_dict

def construct_response(conn, code: int, page: str, content: str = 'html'):
	if content == 'html':
		headers = {
			'Server': 'MyFramework',
			'Content-Type': 'text/html; encoding=utf8',
			'Content-Length': str(len(page)),
			'Connection': 'keep-alive'
		}

		headers_raw = ''.join('%s: %s\r\n' % (k, v) for k, v in headers.items())

		conn.send(RESPONSE_CODES[code].encode())
		conn.send(headers_raw.encode())
		conn.send(b'\r\n')
		conn.send(page.encode())
	elif content == 'json':

		page = json.dumps(page)

		headers = {
			'Server': 'MyFramework',
			'Content-Type': 'application/json; encoding=utf8',
			'Content-Length': str(len(page)),
			'Connection': 'keep-alive'
		}

		headers_raw = ''.join('%s: %s\r\n' % (k, v) for k, v in headers.items())

		conn.send(RESPONSE_CODES[code].encode())
		conn.send(headers_raw.encode())
		conn.send(b'\r\n')
		conn.send(page.encode())

def run(*args):
	if SETTINGS.deploy == 'Local'
		for function in args:
			result = function()

		sock = socket.socket()
		sock.bind((SETTINGS.host, SETTINGS.port))
		sock.listen(SETTINGS.conns)

		conn, addr = sock.accept()
		print("connected: ", addr)

		while True:
			try:
				data = conn.recv(SETTINGS.conn_size).decode()
				if not data:
					break

				request = request_parse(data)
				if DEBUG:
					for key, value in request.items():
						print(f"{key}: {value}")
				try:
					address = PAGES[request['ADDR']]
					if address[2] == 'html':
						if request['METHOD'] not in PAGES[request['ADDR']][0]:
							construct_response(conn, 405, '405.html')
							response_code = 405
						else:
							if request['PARAMS'] != {}:
								page, values = address[1](request, **request['PARAMS'])
								result = insert_values_into_html(page, values)
								construct_response(conn, 200, result)
								response_code = 200
							else:
								page, values = address[1](request)
								result = insert_values_into_html(page, values)
								construct_response(conn, 200, result)
								response_code = 200
					elif address[2] == 'json':
						if request['METHOD'] not in PAGES[request['ADDR']][0]:
							construct_response(conn, 405, '405.html')
							response_code = 405
						else:
							if request['PARAMS'] != {}:
								response = address[1](request, **request['PARAMS'])
								construct_response(conn, 200, response, 'json')
								response_code = 200
							else:
								response = address[1](request)
								construct_response(conn, 200, response, 'json')
								response_code = 200
				except KeyError:
					construct_response(conn, 404, "error.html")
					response_code = 404

				print(addr, request['ADDR'], request['PARAMS'], request['METHOD'], RESPONSE_CODES[response_code])

			except KeyboardInterrupt:
				conn.close()

		conn.close()
	elif SETTINGS.deploy == 'WGSI':
		pass