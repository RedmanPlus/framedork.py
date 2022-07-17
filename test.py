class WSGI:

    def __init__(self) -> None:
        self._data = None
        self._status = None
        self._response_headers = None

    def __call__(self, environ, start_response) -> any:
        start_response(self._status, self._response_headers)

        return iter([self._data])

    def _set_data(self, new_data: bytes) -> None:
        self._data = new_data

    def _set_status(self, new_status: str) -> None:
        self._status = new_status

    def _set_headers(self, headers: list) -> None:
        self._response_headers = headers 

    def set(self, response: dict) -> None:
        self._set_data(response['data'])
        self._set_status(response['status'])
        self._set_headers(response['headers'])

test = WSGI()

test.set({
        'data': b'Hi mom',
        'status': '200 OK',
        'headers': [
            ('Content-type', 'text/plain'),
            ('Content-Length', '6')
    ]})

