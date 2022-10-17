from typing import Dict

from framedork.src.etc.utils import Page, RegisterMixin
from framedork.src.middleware.filters import BaseFilter

class BaseMiddleware(RegisterMixin):

    def __init__(self):

        self.PAGES:  Dict[str, Page]  = {}
        self.filter: BaseFilter = None

    def add_filter(self, filter: BaseFilter):
        self.filter = filter

    def add_pages(self, *args):
        for arg in args:
            arg()

    def __call__(self, request: dict) -> any:
        valid, _ = self.filter(request)
        if valid:
            return self.PAGES.get(request['PATH_INFO'])

        return None