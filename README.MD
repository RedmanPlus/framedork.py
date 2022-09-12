# FRAMEDORK.PY

An attempt to learn how frameworks like Django or Flask work internally by trying to implement my own version.
***WARNING - this is by no means a production ready code and is not even supposed to be used in production. Changes might be applied to the codebase without any notice, so use cautiously***

>**New in 0.2.0: we've refactored all of our code into the OOP, so the code created for the earlier version of the framedork will not work. Please refactor your application according to the new documentation**
## Getting started

To start using framedork.py, simply clone the repository to your local machine with  `git clone https://github.com/RedmanPlus/framedork.py.git`. You can use all of the features by importing main file `framedork.py` into your main Python file like this:

```Python
from src.framedork import Framedork
from src.preprocessors.response import Response

app = Framedork()
```

Here you create an instance of a framedork, that will handle all of the routing and connections from now on

## Defining a page

To define a page, write a simple function using a `@app.register` decorator like this:

```Python
@app.register('/', ['GET'])
def index(request):
	return Response(["index.html", {}])
```

Page function accepts a request from a browser (a dictionary of all possible parameters from a request), and returns a Response object that accepts a relative adress of a template file and a dictionary with parameters that need to be added to the page. You can inspect a note on tempating later. 
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
POST-request parameters can be used in inner logic of your program or for getting values into the database.

## POST, PUT and DELETE methods

All three methods generate a `request['BODY']` dictionary, that you can accept. To differenciate between the methods inside your **framedork** function, we recomend to use `match request['METHOD']:` structure, or if you're using an older version of Python - `if request['METHOD'] == 'GET'` structure.

It looks something like this:

```Python
@app.register('/foo/', ['GET', 'POST', 'PUT', 'DELETE'])
def foo(request, id=1):
	match request['METHOD']:
		case 'GET':		# A simple GET request, just returns
			return Response(['test2.html', {'value': str(id)}])	# a page with values from parameters
		case 'POST':									
			values = request['BODY']	# POST takes values from the request
			animal.add(values)			# and uses them to create a new record
			animal.save()				# in the database
			return Response(['test2.html', {'value': str(id)}])
		case 'PUT':									
			values = request['BODY']	# PUT request at first gets an entry
			check = animal.filter({'id': id})# that needs to be checked, then
			print(check)				# updates it with the data from a 
			for key, value in values.items(): # PUT requet and updates the data
				try:
					check[0][key] = value
				except KeyError:
					continue
			animal.add(check[0])
			animal.save()
			return Response(['test2.html', {'value': str(id)}])
		case 'DELETE':		# DELETE takes data from your request
			values = request['BODY']	# and deletes all entries that satisfy
			animal.delete(values)		# the condition
			return Response(['test2.html', {'value': str(id)}])
```

All of the methods can be used to create a more interractive backend or to make an API.

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

## DORM (or dorkORM)

**DORM** is a custom ORM integrated into **framedork**. It can be used for connecting your web app with external database, so you can use this data in your web pages. DORM is currently *work-in-progress*, so any changes may apply.

**DORM** only supports *PostgreSQL* connections for now

### Creating and registering models

First of all, import **DORM** into your main file like so:

```Python
from src.dorm import Model, StringField, IntField, FloatField, DateField
```

Now create a model of your SQL table:

```Python
animal = Model(table='animal', fields=[
		StringField(null=False, max_len=20, name='name'),
		StringField(null=False, max_len=30, name='species'),
		IntField(name='life_expectancy')
	])
```

Model accepts two parameters - a name of a relative SQL table and a list of fields it will contain. Please note that your model can reflect an existing SQL table in your database - it will not fail and will just use this table and all it's data, but your model **must** reflect all of the columns 100% or it will crash. So on current stage of development we recomend to use **DORM** models with existing tables only in case these tables have only already implemented fields.

Currently **DORM** can only create 4 field types - String, Integer, Float and date. All of these fields have a `null` parameter, that will define on initiation, if a field can be nullable. By default it is set to `True`, and you don't have to add it into the definition.

To register a model, call a `register_model()` function:

```Python
framedork.register_model([animal])
```

`register_model` accepts a list of all models registered by you. It will check, if accociated tables exist in a database, and if not created - will create ones.

### Using **DORM** models in your code

To use **DORM** models in your **framedork** functions, add `global` instruction in a beguining of the file like so:

```Python
@app.register('/animal/', ['GET'])
def animal_page(request, name='Hyena'):
	global animal
```

Currently you can only get values from a database and create new entries.

#### Getting values

To get values from a database, use `get()` and `filter()` methods. A `get()` methods returns all entries into a database in a list of dictionaries, where every dictionary is a separate entry, and every field in a dictionary represents a value with a key of the column name. `filter()` does the same, but it accepts a dictionary of search parameters. Every key in a dictionary must reflect a name of a column in your SQL table.

Now you can use your fetched data in your inner logic or simply send it to the browser with templating.

#### Setting values

To set values for your database, first of all use `add()` method of your model. `add()` method accepts a dictionary of all values, that you wish to write. Note that keys of the dictionary must reflect your SQL table column names, and all NOT NULL fields must be filled.

Then you can use `save()` method and it will authomatically save your data in a database.

It looks something like so:

```Python
vals = {'name': 'Hyena', 'species': 'Hyaenidae', 'life_expectancy': 30}
animal.add(vals1)
animal.save()
```

#### Updating values

To update values in your database, you can also use `add()` and `save()` combination. `save()` method checks if the entry by this id already exists in your database and either updates it or creates a new one.

For example, you fetch some information from your database. Then you apply some transformation to this data. Now you can `add()` it back to the model and then `save()` it. It looks like so:

```Python
animals = animal.get()
one = animals[0]

one['name'] = 'Qute Hyena'

animal.add(one)
animal.save()
```

We recomend to apply any changes directly to the data you fetched to avoid any errors.

#### Deleting values

To delete a value from your database, use `delete()` method. It accepts a dictionary, where every key represents a name of the field. The value represents a value of this particular column in the database, that will be deleted.

It looks like this:

```Python
animal.delete({'name': 'Hyena'})
```
Note that `delete()` method may delete multiple entries in your database if your dictionary is not very specific or there is multiple entries that contain the value you specified to be deleted.

## Adding settings

Settings in your **framedork** application are used for specifiing what host and port to connect to, and what are the database credentials. You can set your settings in definition of a `Settings` class entity, that you'll then pass to the `Framedork` entity upon it's initialising. It looks like this:

```Python
settings = Settings(
    port=8000,
    db="postgres",
    db_conn=DB_CONNECTION,
    deploy="wsgi"
)

app = Framedork(settings)
```

All of the arguments to the `Settings` class are optional and `Settings` are optional for the `Framedork` instanse themselves, but you can define these fields:
- host: an IP adress from which the server will send the data.
- port: the port that will be used for connection.
- conns: the amount of consequent connections that are avaliable simultaneously.
- conn_size: the amount of bytes allowed to be recieved once at a time by the server from the client.
- db: a database you will use. Currently accepts only 'psql' as a parameter.
- db_conn: All of the necessary credential information to connect with the database. Please make sure that all of the credentials are correct.
- deploy: will define if your app is ran locally or by a WSGI web server.


## Using framedork for creating API-s

You can specify what kind of response will the function send to the browser. To make your function send a json string, specify the content type in your `@register` decorator:

```Python
@app.register('/api/', ['GET', 'POST'])
def api(request):
	return Response([{'hi': 'you\'re qute'}])
```

Here your function returns a `Response` object that accepts only the list with a dictionary in it. Now **framedork** will send it to the browser or to any endpoint that will call your website at this address. 

Also, since **DORM** `get()` and `filter()` methods return a list of dictionaries with entries to the database, you can simply fetch all the data you need and straight up send the response to the client like so:

```Python
@app.register('/api/', ['GET', 'POST'])
def api(request, id=1):
	response = animal.filter({'id': id})
	if response == []:
		return {'error': 'nothing found'}
	return Response([response[0]])
```

This way you can create a series of different endpoints that will communicate with the database, resulting in a full **framedork** backend.

## Filters

You can manage what requests are being passed to your function with filters. They check if the request falls into several constraints that you define and either passes it to the controller functions (if everything is ok) or sends an error to the client if some constraints are violated.

**Framedork** uses build-in `URLMethodFilter` class as a default, but you can create your own filter.

```Python
from framedork.src.middleware.filters import BaseFilter

class CustomFilter(BaseFilter):
	CONSTRAINTS = [
		...
	]
```

All filters are derived from a `BaseFilter` parent class and have a list of constraints. A constraint is a function or callable that accepts a request (a simple dictionary), a context object and returns a boolean and a reason object. 

```Python
def is_allowed_url_parameters(request: dict, context: BaseContext) -> bool, reasons.Reason:
	...
```

A context is a class that has all of the information about the state of the **framedork** that might be needed during evaluating. It can accept any given amount of arguments that then can be accessed during evaluation. For ease of use defining custom context classes with specific `@property` methods is advised.

```Python
class CuspomContext(BaseContext):

	@property
	def allowed_parameters(self):
		return [param_name for param_name in self.objects.parameters_field]

```

Every context object has an inner `objects` attribute. It's a dataclass that holds all of the data passed upon the initializing the instance. For example:

```Python

parameters = {"x": "int", "y": "string"}

context = CustomContext(parameters)

```

will create an internal dataclass like so:

```Python

@dataclass
class CustomContextData:
	parameters_field: dict

```

And will return an instance of it populated with the data that was passed to it upon initializing. You now can use this fields in your `@property` methods. For example, expanding on the earlier case:

```Python
def is_allowed_url_parameters(request: dict, context: BaseContext) -> bool, reasons.Reason:
	for param in request['QUERY_PARAMS']:
		if param not in context.allowed_parameters:
			return False, reasons.ForbittenReason
	
	return True, None
```

will check if an incomming url-parameters are allowed to be passed to the **framedork** and in case of not, will send to a user a `403 Forbitten` HTTP response code.

Now you simply add your function to the constraints of a filter:

```Python
class CustomFilter(BaseFilter):
	CONSTRAINTS = [
		is_allowed_url_parameter
	]
```

and add use this filter as a primary filter for a **framedork** with `add_filter` method:

```Python
app.add_filter(CustomFilter(context=CustomContext(parameters)))
```

> *Note:* Please notice that this filter will not check for allowed methods or registered urls. You can add this by adding `is_allowed_method` and `is_registered_url` functions that can also be imported from a filter module. We recommend to add them to every filter that you write 

## Running your website

To run your website, you need to call a `run()` method of your `framedork` instance at the end of the file. Your `run()` method must accept all of the functions you've written **not called** so they can be registered by the framework. You can do it like so:

```Python
app.run(index)
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

**Please note that** currently you cannot shutdown your server from inside the program or terminal. You can try to use Ctrl-C, but it can result with sockets being left open. We recomend currently to stop the python process from your machine's controll panell.

## Running framedork.py with Gunicorn

To run **framedork.py** with a web server, you'll need to change your file a little. Change your settings' `local` paramether to the `wsgi`. Now change your `app.run()` method at the end of the file to:

```Python
wsgi = app.run(index)
```

Register all of your functions in a `run()` method. It will return an object, that we will then call with a Gunicorn.

Now upload all of your work onto the server with Gunicorn installed on it and in a project directory call:

```commandline
gunicorn --workers=2 main:app
```

where
- `main` is a name of your file
- `wsgi` is the name of the object returned by your `run()` function

Now your app will be hosted on a 127.0.0.1:8000, but you can specify the IP address.
