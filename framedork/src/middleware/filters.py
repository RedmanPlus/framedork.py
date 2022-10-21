import inspect
from typing import List, Callable, NoReturn
from dataclasses import make_dataclass

from . import reasons

class BaseContext:

    def __init__(self, *args):

        fields = []
        frame = inspect.currentframe().f_back
        tmp1 = dict(frame.f_globals.items())
        tmp2 = dict(frame.f_locals.items())
        tmp = dict(tmp1, **tmp2)

        for arg in args:
            for k, var in tmp.items():
                if isinstance(var, arg.__class__):
                    if arg == var:
                        field = (f"{k}_field", type(arg))
                        fields.append(field)

        data_class = make_dataclass(f"{type(self).__name__}Data", fields)
        self.objects = data_class(*args)


    def __call__(self, *args):
        super().__init__(*args,)


class URLContext(BaseContext):

    @property
    def registered_urls(self):
        pages = self.objects.PAGES_field
        registered = [page for page in pages]

        return registered

class MethodContext(BaseContext):

    @property
    def page_methods(self):
        pages = self.objects.PAGES_field
        methods = {k: v.methods for k, v in pages.items()}

        return methods

class URLMethodContext(URLContext, MethodContext):
    pass

class BaseFilter:

    CONSTRAINTS: List[Callable[[dict, BaseContext], bool]] = []

    def __init__(self, context: BaseContext) -> NoReturn:
        self.context = context

    def __call__(self, request: dict) -> bool:
        for constraint in self.CONSTRAINTS:
            valid, reason = constraint(request, self.context)
            if not valid:
                return False, reason
        
        return True, None

def is_registered_url(request: dict, context: BaseContext) -> bool:
    if request["PATH_INFO"] not in context.registered_urls:
        return False, reasons.NotFoundReason()
    return True, None

def is_allowed_method(request: dict, context: BaseContext) -> bool:
    if request['REQUEST_METHOD'] not in context.page_methods[request['PATH_INFO']]:
        return False, reasons.NotAllowedReason()
    return True, None

class URLFilter(BaseFilter):

    CONSTRAINTS: List[Callable[[dict, BaseContext], bool]] = [
        is_registered_url
    ]

class URLMethodFilter(BaseFilter):

    CONSTRAINTS: List[Callable[[dict, BaseContext], bool]] = [
        is_registered_url,
        is_allowed_method
    ]