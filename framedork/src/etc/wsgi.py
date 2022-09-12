import sys
import logging

from src.handlers.handlers import WSGIHandler
from src.preprocessors.Response import ResponseHandler
from src.preprocessors.HTML import HTMLPreprocessor

class Context:
    def __init__(self):
        self.pages = {}

    def set_context(self, context):
        self.pages = context

class WSGIObject:

    def __init__(self, pages):
        self.pages = pages
        self.html_preprocessor = HTMLPreprocessor()
        self.handler = WSGIHandler(self.pages, self.html_preprocessor)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    def __call__(self, environ, start_response):
        self.logger.info(environ['PATH_INFO'])
        try:
            page = self.pages[environ['PATH_INFO']]

            if environ['REQUEST_METHOD'] not in page.methods:
                response = ResponseHandler(405, '405.html', "html", "wsgi")
                response_data = response()
                start_response(response_data[0], response_data[1])

                return iter([response_data[2].encode()])

            data = {}
            if environ['QUERY_STRING'] != "":
                params = environ['QUERY_STRING'].split("&")

                for param in params:
                    param = param.split("=")
                    data[param[0]] = param[1]

            response_data = self.handler(environ, **data)

            start_response(response_data[0], response_data[1])
            return iter([response_data[2].encode()])
        except KeyError:
            response_data = ResponseHandler(404, "404.html", "html", "wsgi")()

            start_response(response_data[0], response_data[1])

            return iter([response_data[2].encode()])