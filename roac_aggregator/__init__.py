#!/usr/bin/env python
from flask import Flask
from .json import JSONEncoder
from .mongodb import MongoDB


app = Flask(__name__.split('.')[0])

SECRET_KEY = "development key"
DEBUG = True
MONGO_DB = 'roac'

app.config.from_object(__name__)


app.json_encoder = JSONEncoder


server = MongoDB(app)


from . import views
