import json

class Response:

    def __init__(self, contents: list):
        self.contents = contents
        if len(self.contents) > 1:
            self.method = "html"
        else:
            self.method = "json"

class ResponseHandler:

    base_headers: list = [
        ('Server', 'Framedork.py'),
        ('Connection', 'keep-alive')
    ]

    html_headers: str = 'text/html; encoding=utf8'
    json_headers: str = 'application/json; encoding=utf8'

    RESPONSE_CODES = {
        200: "HTTP/1.1 200 OK\r\n",
        400: "HTTP/1.1 400 BAD_REQUEST\r\n",
        404: "HTTP/1.1 404 NOT_FOUND\r\n",
        405: "HTTP/1.1 405 Method not allowed\r\n",
        500: "HTTP/1.1 500 Internal server error\r\n"
    }

    RESPONSE_CODES_WSGI = {
        200: "200 OK",
        400: "400 BAD REQUEST",
        404: "404 NOT FOUND",
        405: "405 Method not allowed",
        500: "500 Internal server error"
    }

    def __init__(self, code: int, page: str, content: str, mode: str):
        self.code = code
        self.page = page
        self.content = content
        self.mode = mode

    def _construct_response(self):

        page_raw = self.page
        
        if self.content == "json":
            page_raw = json.dumps(self.page[0])

        headers_raw = [f"{i[0]}: {i[1]}" for i in self.base_headers]
        headers_raw = "\r\n".join(headers_raw) + f"\r\nContent-Length: {len(page_raw)}\r\n" 
        headers_raw = headers_raw + 'Content-Type: ' + self.html_headers + "\r\n" if self.content == "html" else headers_raw + 'Content-Type: ' + self.json_headers + "\r\n"

        return (self.RESPONSE_CODES[self.code], headers_raw, page_raw)

    def _construct_wsgi_response(self):

        page_raw = self.page

        if self.content == "json":
            page_raw = json.dumps(self.page)

        headers = self.base_headers.copy()
        headers.append(("Content-Length", str(len(page_raw))))
        headers.append(('Content-Type', self.html_headers) if self.content == "html" else ('Content-Type', self.json_headers))
        
        return (self.RESPONSE_CODES_WSGI[self.code], headers, page_raw)

    def __call__(self):
        if self.mode == "local":
            return self._construct_response()
        elif self.mode == "wsgi":
            return self._construct_wsgi_response()