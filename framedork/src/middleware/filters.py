import inspect
from typing import List, Callable, NoReturn
from dataclasses import make_dataclass

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


class URLContext(BaseContext):

    @property
    def registered_urls(self):
        pages = self.objects.PAGES_field
        registered = [page for page in pages]

        return registered

class BaseFilter:

    CONSTRAINTS: List[Callable[[dict, BaseContext], bool]] = []

    def __init__(self, context: BaseContext) -> NoReturn:
        self.context = context

    def __call__(self, request: dict) -> bool:
        for constraint in self.CONSTRAINTS:
            if not constraint(request, self.context):
                return False
        
        return True

def is_registered_url(request: dict, context: BaseContext) -> bool:
    if request["PATH_INFO"] not in context.registered_urls:
        return False
    return True

class URLFilter(BaseFilter):

    CONSTRAINTS: List[Callable[[dict, BaseContext], bool]] = [
        is_registered_url
    ]