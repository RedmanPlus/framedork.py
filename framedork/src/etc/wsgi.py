import sys
import logging
from framedork.src.etc.utils import Page

from framedork.src.handlers.handlers import WSGIHandler
from framedork.src.middleware.filters import BaseFilter
from framedork.src.middleware.middleware import BaseMiddleware
from framedork.src.preprocessors.Response import ResponseHandler
from framedork.src.preprocessors.HTML import HTMLPreprocessor

class Context:
    def __init__(self):
        self.pages = {}

    def set_context(self, context):
        self.pages = context

class WSGIObject:

    def __init__(self, pages: list, filter: BaseFilter, middleware: BaseMiddleware):
        self.pages = pages
        self.html_preprocessor = HTMLPreprocessor()
        self.handler = WSGIHandler(self.pages, self.html_preprocessor)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler(stream=sys.stdout))

        self.filter = filter
        self.middlewares = middleware

    def evaluate_middlewares(self, request: dict) -> Page:
        if self.middlewares is None:
            return self.handler(request)

        for middleware in self.middlewares:
            page = middleware(request)
            if page is not None:
                return page

        return self.handler(request)

    def __call__(self, environ, start_response):
        self.logger.info(environ['PATH_INFO'])
        valid, reason = self.filter(environ)

        if not valid:
            response_data = ResponseHandler(reason(), f"{reason()}.html", "html", "wsgi")()
            start_response(response_data[0], response_data[1])
            return iter([response_data[2].encode()])


        page = self.evaluate_middlewares(environ)

        data = {}
        if environ['QUERY_STRING'] != "":
            params = environ['QUERY_STRING'].split("&")

            for param in params:
                param = param.split("=")
                data[param[0]] = param[1]

        response_data = self.handler(page, environ, **data)

        start_response(response_data[0], response_data[1])
        return iter([response_data[2].encode()])
