#!/usr/bin/env python
from flask import Flask
from .json import JSONEncoder
from .mongodb import MongoDB
from flask.ext.mail import Mail


app = Flask(__name__.split('.')[0], instance_relative_config=True)

app.config.from_object('roac_aggregator.defaults')
app.config.from_pyfile('roacagg.cfg', silent=True)
app.config.from_envvar('ROACAGG_SETTINGS', silent=True)


app.json_encoder = JSONEncoder


server = MongoDB(app)
mail = Mail(app)


from . import api, content
