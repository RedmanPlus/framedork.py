import socket
from typing import Callable, NoReturn
from framedork.src.etc.utils import Page, RegisterMixin
from framedork.src.middleware.filters import BaseFilter, URLMethodContext, URLMethodFilter

from .src.handlers.handlers import LocalHandler

from .src.preprocessors.Request import RequestPreprocessor
from .src.etc.settings import Settings
from .src.preprocessors.HTML import HTMLPreprocessor
from .src.preprocessors.Response import ResponseHandler
from .src.DORM.dorm import Connector
from .src.etc.wsgi import Context, WSGIObject

from .src.exceptions.handler_exceptions import MethodError

class Framedork(RegisterMixin):

    def __init__(self, settings: Settings = None) -> NoReturn:

        self.PAGES: dict = {}
        self.WSGI_CONTEXT: Context = Context()
        self.DEBUG: bool = False
        self.SETTINGS: Settings = settings

        self.request_preprocessor = RequestPreprocessor()
        self.html_preprocessor = HTMLPreprocessor()

        self.filter: BaseFilter = None
        self.preffered_filter: BaseFilter = None

        self.middlwares = None

    def add_filter(self, filter: BaseFilter) -> NoReturn:
        self.preffered_filter = filter

    def set_filter(self) -> NoReturn:
        PAGES = self.PAGES
        if self.preffered_filter is None:
            self.filter = URLMethodFilter(context=URLMethodContext(PAGES))

    def add_middlewares(self, *args) -> NoReturn:
        if self.middlwares is None:
            self.middlwares = list(args)
        else:
            self.middlwares.append(*args)

    def evaluate_middlewares(self, request: dict) -> Page:
        if self.middlwares is None:
            return self.PAGES[request["ADDR"]]

        for middleware in self.middlwares:
            page = middleware(request)
            if page is not None:
                return page

        return self.PAGES[request["ADDR"]]

    def run(self, *args) -> NoReturn:
        for arg in args:
            arg()

        if self.middlewares is not None:
            for middleware in self.middlwares:
                self.PAGES = dict(self.PAGES, **middleware.PAGES)

        self.set_filter()

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

                    valid, reason = self.filter(request)

                    if not valid:
                        response = ResponseHandler(reason(), f"{reason()}.html", "html", "local")()
                        response_code = reason()
                    else:
                        address = self.evaluate_middlewares(request)
                        result = address(request, **request['PARAMS'])
                        if result.method == "html":
                            result.contents = self.html_preprocessor(*result.contents)
                            response = ResponseHandler(200, result.contents, "html", "local")()
                            response_code = 200
                        if result.method == "json":
                            response = ResponseHandler(200, result.contents, "json", "local")()
                            response_code = 200

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
            
            return WSGIObject(self.PAGES, self.filter, self.middlwares)