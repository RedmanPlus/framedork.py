# FRAMEDORK.PY

An attempt to learn how frameworks like Django or Flask work internally by trying to implement my own version.
***WARNING - this is by no means a production ready code and is not even supposed to be used in production. Changes might be applied to the codebase without any notice, so use cautiously***

## Getting started

To start using framedork.py, simply clone the repository to your local machine with 'git clone https://github.com/RedmanPlus/framedork.py.git'. You can use all of the features by importing main file 'framework.py' into your main Python file like this:
> 'import framework'

## Defining a page

To define a page, write a simple function using a '@register' decorator like this:

> '@framework.register('/', ['GET'])
>
> def index():
>
>   return "index.html"'

At the current stage of a project, a page function returns a name of an html file, that will be then loaded and displayed by the framework. You will need to create one by yourself.
Also notice that method list must be defined but currently **it doesn't do anything**. Support for the different http methods will be added later.

## Running your website

To run your website, you need to call a 'run()' function at the end of the file. Your 'run()' function must accept all of the functions you've written **not called** so they can be registered by the framework. You can do it like so:

> 'framework.run(index)'

Then simply run your file with

> 'python main.py'

or

> 'main.py'

if you're using a !# at the beguining of a file.

The web server will be automatically started on 8080 port, where you can access it.