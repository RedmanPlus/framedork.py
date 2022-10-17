'''Basic Framedork app

Here is the example of a 'Hello World' app
'''

from framedork.framedork import Framedork
from framedork.src.etc.settings import Settings
from framedork.src.preprocessors.Response import Response

'''
Framedork class is a main workhorse of the app, it will register
all functions and execute your business logic

Settings class provides a context for an app. By default all of its
fields have a pre-determined value, so you don't need to tweek anything
at first. However, as your project complexity rizes, and more
complex things are needed to be done (Such as a database access or
an addition of the middleware), Settings class is the one to be used

A Response class handles the way your app responds to a cliend.
'''

app = Framedork(Settings())

@app.register("/", ["GET"])
def index(request):
    '''
    You add pages to your app with functions. A Framedork function accepts
    a request (a standart dictionary) and returns a response object. It is also must
    be decorated by a @register decorator, which accepts a URL and a list of  allowed
    method
    '''
    return Response(['index.html', {}])


'''
To run your app, call run() method at the end of the file. It must accept all
of the functions that you've created as arguments
'''
app.run(index)