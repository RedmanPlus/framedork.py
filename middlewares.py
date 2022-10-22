from framedork.src.middleware.filters import BaseFilter, URLMethodContext, is_registered_url, is_allowed_method
from framedork.src.middleware import reasons

class URLParamsContext(URLMethodContext):

    @property
    def url_params(self):
        return self.objects.request_field["QUERY_PARAMS"]


def has_url_params(request: dict, context: URLParamsContext) -> bool:
    PAGES = context.objects.PAGES_field
    context = context(request, PAGES)

    if context.url_params is not None:
        return True, None

    return False, reasons.ForbittenReason()


class URLParamsFilter(BaseFilter):

    CONSTRAINTS = [
        is_registered_url,
        is_allowed_method,
        has_url_params
    ]