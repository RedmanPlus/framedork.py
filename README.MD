# FRAMEDORK.PY

An attempt to learn how frameworks like Django or Flask work internally by trying to implement my own version.
***WARNING - this is by no means a production ready code and is not even supposed to be used in production. Changes might be applied to the codebase without any notice, so use cautiously***

## Getting started

To start using framedork.py, simply clone the repository to your local machine with  `git clone https://github.com/RedmanPlus/framedork.py.git`. You can use all of the features by importing main file `framedork.py` into your main Python file like this:

> `import framedork`

## Defining a page

To define a page, write a simple function using a `@register` decorator like this:

> `@framedork.register('/', ['GET'])
>
> def index(request):
>
>   return "index.html"`

At the current stage of a project, a page function accepts a request from a browser and returns a name of an html file, that will be then loaded and displayed by the framework. You will need to create one by yourself.
You will need to specify all allowed methods for the page. If a page is called by a method, that is not declarated in a `register` decorator, **framedork** will send a '405 Method not allowed' error.

## Accessing URL parameters

To access URL parameters, add the variable that will hold the value of a parameter to the function input like so:

> `def index(request, id=1):`

We recomend to set some default values to the parameter, so your program won't crash if a parameter is not present. You can use the value of your URL parameters in an inner logic of your page function.

## Accessing POST body

If you wish to use a POST-requests with your page, you can access all of the POST-body parameters with `request["BODY"]`.
`request["BODY"]` is a dictionary, containing all of the parameters, sent by a POST-request, alteady parsed and splitted by **framedork**. If you know in advance, what parameters are being sent, then you can simply access all the values by

> `param_value = request["BODY"]["name_of_param"]`

or if you wish to make code cleaner:

> `body = request["BODY"]`
>
> `param_value = body["name_of_param"]`

A `request["BODY"]` field is present in all request by default, even in cases if the GET requests was sent. By default it is set to an empty list, so before accessing all of the POST values you need to check if the body is empty. 
POST-request parameters can be used in inner logic of your program. Currently **framedork** has no implementation of a database connection, so you can use a POST-request body as a list of conditions in case you wish to obstain from url parameters.

## Running your website

To run your website, you need to call a `run()` function at the end of the file. Your `run()` function must accept all of the functions you've written **not called** so they can be registered by the framework. You can do it like so:

> `framedork.run(index)`

Then simply run your file with

> `python main.py`

or

> `main.py`

if you're using a !# at the beguining of a file.

The web server will be automatically started on 8080 port, where you can access it.
