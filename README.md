# Bird API

This is an implementation of a simple toy REST API for storing and
retrieving birds. To learn, for fun and glory.

# Python environment

This was only tested with Python 3. You can find list of python packages
required in requirements.txt, coming straight from development
virtualenv. To replicate python environment:

1. Make sure you are using Python 3.
2. (recommended) Prepare and activate virtual environment.
3. pip install -r requirements.txt

# Does it run?

You can run a test instance of the application using reference
implementation of a WSGI server by just running the birds package. It
requires a default, test, unauthorised MongoDB instance running.

1. Make sure you are in the repository top-level directory.
2. Run: python -m birds
3. The server, it is running! Look, I'm making requests!

# Show me your tests

This uses standard unittest module for testing. Testing storage requires
local, runnin, unauthorised instance of MongoDB.

1. Make sure you are in the repository top-level directory.
2. Run: python -m unittest discover

You can test just the web resources, which does not require the
database, by running unittest module on just the birds.test_resources
module:

python -m unittest birds.test_resources

Add a -v argument to python invocations here to see the list of tests
being run. Because it's fun, that's why.
