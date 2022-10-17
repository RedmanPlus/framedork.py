from framedork.src.preprocessors.HTML import HTMLPreprocessor
from framedork.src.preprocessors.Response import ResponseHandler

class BasicHandler:

    def __init__(self, PAGES: list, html: HTMLPreprocessor):
        self.html = html

    def __call__(self, page, request, *args, **kwargs):

        result = page(request, *args, **kwargs)

        return result

class LocalHandler(BasicHandler):

    def __call__(self, page, request, *args, **kwargs):
        result = super().__call__(page, request, *args, **kwargs)

        if result.method == "html":
            response = ResponseHandler(200, result, "html", "local")
        elif result.method == "json":
            response = ResponseHandler(200, result, "json", "local")

        return response()

class WSGIHandler(BasicHandler):

    def __call__(self, page, request, *args, **kwargs):
        result =  super().__call__(page, request, *args, **kwargs)

        if result.method == "html":
            result.contents = self.html(*result.contents)
            response = ResponseHandler(200, result.contents, "html", "wsgi")
        elif result.method == "json":
            response = ResponseHandler(200, result.contents, "json", "wsgi")

        return response()