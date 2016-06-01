from wsgiref import simple_server
from . import app

httpd = simple_server.make_server('127.0.0.1', 8000, app.setup())
httpd.serve_forever()