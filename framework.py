import socket

RESPONSE_CODES = {
	200: "HTTP/1.1 200 OK\r\n",
	400: "HTTP/1.1 400 BAD_REQUEST\r\n",
	404: "HTTP/1.1 404 NOT_FOUND\r\n"
}

PAGES = {}

def register(addr: str, methods: list):
	def decorator(func):
		def wrapper(*args, **kwargs):
			PAGES[addr] = [methods, func]

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
					params_dict[head] = body

		return (addr, params_dict)
	
	return (addr, {})

def request_parse(request: bytes) -> dict:
	return_dict = {}
	request = request.decode().split('\r\n')
	for line in request:
		line = line.split(': ')
		if len(line) == 1 and line[0] != '' :
			line = line[0].split(' ')
			method, addr, protocol = line[0], line[1], line[2]
			addr = get_url_params(addr)
			return_dict['METHOD'] = method
			return_dict['ADDR'] = addr[0]
			return_dict['PROTOCOL'] = protocol
			return_dict['PARAMS'] = addr[1]
		elif line[0] == '':
			continue
		else:
			head, body = line[0], line[1]
			return_dict[head.upper()] = body

	return return_dict

def construct_response(conn, code: int, filename: str):

	with open(filename, 'r') as f:
		body = f.read()
		body = body.replace("\t", "")
		body = body.replace("\n", "\r\n")

	headers = {
		'Server': 'MyFramework',
		'Content-Type': 'text/html; encoding=utf8',
		'Content-Length': str(len(body)),
		'Connection': 'Closed'
	}

	headers_raw = ''.join('%s: %s\r\n' % (k, v) for k, v in headers.items())

	conn.send(RESPONSE_CODES[code].encode())
	conn.send(headers_raw.encode())
	conn.send(b'\r\n')
	conn.send(body.encode())

def run(*args):

	for function in args:
		result = function()
		print(result)

	print(PAGES)

	sock = socket.socket()
	sock.bind(('', 8080))
	sock.listen(1)

	conn, addr = sock.accept()
	print("connected: ", addr)

	while True:
		try:
			data = conn.recv(1024)
			if not data:
				break
			request = request_parse(data)
			print(request)
			print(PAGES)
			try:
				addr = PAGES[request['ADDR']]
				print(addr)
				if request['PARAMS'] != {}:
					result = addr[1](**request['PARAMS'])
					construct_response(conn, 200, result)
				else:
					result = addr[1]()
					construct_response(conn, 200, result)
			except KeyError:
				construct_response(conn, 404, "error.html")

		except KeyboardInterrupt:
			conn.close()

	conn.close()