#!/usr/bin/env python
from __future__ import print_function
from flask import Flask, request
from flask.ext.jsonpify import jsonify
from pymongo import MongoClient

from flask import json as flask_json
from bson.objectid import ObjectId

app = Flask(__name__)

SECRET_KEY = "development key"
DEBUG = True
MONGO_DB = 'roac'

app.config.from_object(__name__)


class JSONEncoder(flask_json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return flask_json.JSONEncoder.default(self, o)


app.json_encoder = JSONEncoder


class MongoDB(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.client = MongoClient(
            app.config.setdefault('MONGO_HOST', 'localhost',))
        self.db = self.client[app.config['MONGO_DB']]


mongoDB = MongoDB(app)


@app.route('/log/<string:node>', methods=['POST'])
def new_log(node):
    data = request.get_json()
    log = mongoDB.db.log
    data_id = log.insert(data)
    return jsonify(data)

if __name__ == '__main__':
    app.run()
