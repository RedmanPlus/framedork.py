import socket
from typing import Callable, NoReturn

from src.handlers.handlers import LocalHandler

from src.preprocessors.Request import RequestPreprocessor
from src.etc.settings import Settings
from src.preprocessors.HTML import HTMLPreprocessor
from src.preprocessors.Response import ResponseHandler
from src.DORM.dorm import Connector
from src.etc.wsgi import Context, WSGIObject

from src.exceptions.handler_exceptions import MethodError

class Page:

    def __init__(self, handler: Callable[[any], any], methods: list) -> NoReturn:
        self.handler: Callable[[any], any] = handler
        self.methods: list = methods

    def __call__(self, request: dict, *args, **kwargs) -> Callable[[any], any]:
        return self.handler(request, *args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.handler.__name__}, ({' '.join(self.methods)})"


class Framedork:

    def __init__(self, settings: Settings = None) -> NoReturn:

        self.PAGES: dict = {}
        self.WSGI_CONTEXT: Context = Context()
        self.DEBUG: bool = False
        self.SETTINGS: Settings = settings

        self.request_preprocessor = RequestPreprocessor()
        self.html_preprocessor = HTMLPreprocessor()

    def register(self, addr: str, methods: list) -> Callable[[any], any]:
        def _decorator(func: Callable[[any], any]):
            def _wrapper(*args, **kwargs):
                self.PAGES[addr] = Page(
                    handler=func,
                    methods=methods
                )
            return _wrapper
        return _decorator

    def run(self, *args) -> NoReturn:
        for arg in args:
            arg()
        if self.SETTINGS.deploy == "local":
            sock = socket.socket()
            sock.bind((self.SETTINGS.host, self.SETTINGS.port))
            sock.listen(self.SETTINGS.conns)

            conn, addr = sock.accept()
            print("connected: ", addr)

            while True:
                try:
                    data = conn.recv(self.SETTINGS.conn_size).decode()
                    if not data:
                        break

                    request = self.request_preprocessor(data)
                    if self.DEBUG:
                        for key, value in request.items():
                            print(f"{key}: {value}")
                    try:
                        address = self.PAGES[request['ADDR']]
                        if request['METHOD'] not in address.methods:
                            response = ResponseHandler(405, '405.html', "html", "local")()
                            response_code = 405
                        else:
                            result = address(request, **request['PARAMS'])
                            if result.method == "html":
                                result.contents = self.html_preprocessor(*result.contents)
                                response = ResponseHandler(200, result.contents, "html", "local")()
                                response_code = 200
                            if result.method == "json":
                                response = ResponseHandler(200, result.contents, "json", "local")()
                                response_code = 200
                    except KeyError:
                        response = ResponseHandler(404, "404.html", "html", "local")()
                        response_code = 404
                        conn.close()
                        sock.close()
                        break

                    conn.send(response[0].encode())
                    conn.send(response[1].encode())
                    conn.send(b"\r\n")
                    conn.send(response[2].encode())

                    print(addr, request['ADDR'], request['PARAMS'], request['METHOD'], response_code)

                except Exception as e:
                    print(e)
                    conn.close()
                    sock.close()
                    break
        elif self.SETTINGS.deploy == "wsgi":
            
            return WSGIObject(self.PAGES)