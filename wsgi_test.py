import framedork

@framedork.register('html', "/", ['GET'])
def index(request):
	return "test.html", {}

runner = framedork.set_wsgi(index)