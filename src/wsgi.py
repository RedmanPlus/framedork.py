
def get_wsgi_data():
	pass

def app(environ, start_response):
	data = b'Hey'
	status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(data)))
    ]
    print(environ)
    print(start_response)
    start_response(status, response_headers)
    return iter([data])