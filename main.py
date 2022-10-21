from framedork.framedork import Framedork
from framedork.src.preprocessors.Response import Response
from settings import settings
from middlewares import URLParamsFilter, URLParamsContext

app = Framedork(settings=settings)

app.add_filter(URLParamsFilter(URLParamsContext()))

@app.register("/", ["GET"])
def index(request, name):
    return Response(["templates/index.html", {"name": name}])

wsgi = app.run(index)