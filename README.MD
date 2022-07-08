# FRAMEDORK.PY

An attempt to learn how frameworks like Django or Flask work internally by trying to implement my own version.
***WARNING - this is by no means a production ready code and is not even supposed to be used in production. Changes might be applied to the codebase without any notice, so use cautiously***

## Getting started

To start using framedork.py, simply clone the repository to your local machine with  `git clone https://github.com/RedmanPlus/framedork.py.git`. You can use all of the features by importing main file `framedork.py` into your main Python file like this:

> `import framedork`

## Defining a page

To define a page, write a simple function using a `@register` decorator like this:

```Python
@framedork.register('/', ['GET'])
def index(request):
	return "index.html", {}
```

Page function accepts a request from a browser (a dictionary of all possible parameters from a request), and returns a name of html file of the page and a dictionary of values, that need to be inserted into the page. You can inspect a note on tempating later. 
You will need to specify all allowed methods for the page. If a page is called by a method, that is not declarated in a `register` decorator, **framedork** will send a '405 Method not allowed' error.

## Accessing URL parameters

To access URL parameters, add the variable that will hold the value of a parameter to the function input like so:

```Python
def index(request, id=1):
```

We recomend to set some default values to the parameter, so your program won't crash if a parameter is not present. You can use the value of your URL parameters in an inner logic of your page function.

## Accessing POST body

If you wish to use a POST-requests with your page, you can access all of the POST-body parameters with `request["BODY"]`.
`request["BODY"]` is a dictionary, containing all of the parameters, sent by a POST-request, alteady parsed and splitted by **framedork**. If you know in advance, what parameters are being sent, then you can simply access all the values by

```Python
param_value = request["BODY"]["name_of_param"]
```

or if you wish to make code cleaner:

```Python
body = request["BODY"]
param_value = body["name_of_param"]
```

A `request["BODY"]` field is present in all request by default, even in cases if the GET requests was sent. By default it is set to an empty list, so before accessing all of the POST values you need to check if the body is empty. 
POST-request parameters can be used in inner logic of your program. Currently **framedork** has no implementation of a database connection, so you can use a POST-request body as a list of conditions in case you wish to obstain from url parameters.

## Templating

**Framedork** uses custom html preprocessor akin to Jinja2, but at the current moment has much less functionality, so it is more like abridged Jinja2.

### Inserting values into the page

To insert a value into a page, construct your html file like so:

```HTML
<h1>{value}</h1>
```

Now, in your page function, add a dictionary, where keys have the same name as the labels you put in your html file. For example, if you're using URL parameters in your page, you can write a function like this:

```Python
def index(request, id=1):  # id is a hypothetic parameter from http://127.0.0.1:8080/?id=1
	return 'test.html', {'value': str(id)}
```

The value of the dictionary will then replace a label in your html page.
Similarly you can use values sent in a POST request, you'll just need to wrap them in a dictionary with names, that will correspond with the ones in your html.

Please also note that the amount of labels and passed values must be exactly the same at best (or not less than the labels in your html file at worst), to avoid errors and crashes.

### Extending templates

To extend your html file by a template, create a template file like 'base.html'. Base file must contain an extendable block like so:

```HTML
{% block content %}
```

Similarly, the file that you will pass from your function should look something like so:

```HTML
{% extends 'base.html' %}
{% block content %}
{% endblock %}
```

Now all of the html content placed between opening and ending of the block will be inserted into a template, and this template will be shipped to the browser.

Please note that the base template filename is a path relaive to the extendable file, and preferably they both should be located in the same folder.

## Running your website

To run your website, you need to call a `run()` function at the end of the file. Your `run()` function must accept all of the functions you've written **not called** so they can be registered by the framework. You can do it like so:

```Python
framedork.run(index)
```
Then simply run your file with

```console
python main.py
```
or

```console
main.py
```

if you're using a !# at the beguining of a file.

The web server will be automatically started on 8080 port, where you can access it.

**Please note that** currently you cannot shutdown your server from inside the program or terminal. You can try to use Ctrl-C, but it takes to much time and don't really work. We recomend currently to stop the python process from your machine's controll panell.
