from typing import Callable, NoReturn

class RegisterMixin:

    def register(self, addr: str, methods: list) -> Callable[[any], any]:
        def _decorator(func: Callable[[any], any]):
            def _wrapper(*args, **kwargs):
                self.PAGES[addr] = Page(
                    handler=func,
                    methods=methods
                )
            return _wrapper
        return _decorator

class Page:

    def __init__(self, handler: Callable[[any], any], methods: list) -> NoReturn:
        self.handler: Callable[[any], any] = handler
        self.methods: list = methods

    def __call__(self, request: dict, *args, **kwargs) -> Callable[[any], any]:
        return self.handler(request, *args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.handler.__name__}, ({' '.join(self.methods)})"

