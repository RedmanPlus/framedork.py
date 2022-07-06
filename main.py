import framework

@framework.register('/', ['GET'])
def index():
	return 'test.html'

@framework.register('/two/', ['GET'])
def other(id=1):
	if id == 1:
		return 'test2.html'
	elif id == 2:
		return 'test22.html'

framework.run(index, other)