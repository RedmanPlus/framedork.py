from src.preprocessors.HTML import HTMLPreprocessor
from src.preprocessors.Response import ResponseHandler

class BasicHandler:

    def __init__(self, PAGES: list, html: HTMLPreprocessor):
        self.PAGES = PAGES
        self.html = html

    def __call__(self, request, *args, **kwargs):

        page = self.PAGES[request["PATH_INFO"]]
        result = page.handler(request, *args, **kwargs)

        return result

class LocalHandler(BasicHandler):

    def __call__(self, request, *args, **kwargs):
        result = super().__call__(request, *args, **kwargs)

        if result.method == "html":
            response = ResponseHandler(200, result, "html", "local")()
        elif result.method == "json":
            response = ResponseHandler(200, result, "json", "local")()

        return response()

class WSGIHandler(BasicHandler):

    def __call__(self, request, *args, **kwargs):
        result =  super().__call__(request, *args, **kwargs)

        if result.method == "html":
            result.contents = self.html(*result.contents)
            response = ResponseHandler(200, result.contents, "html", "wsgi")
        elif result.method == "json":
            response = ResponseHandler(200, result.contents, "json", "wsgi")

        return response()