#!/usr/bin/env python
from __future__ import print_function
from flask import Flask, request
from flask.ext.jsonpify import jsonify
from pymongo import MongoClient

import dateutil.parser

from flask import json as flask_json
from bson.objectid import ObjectId

app = Flask(__name__)

SECRET_KEY = "development key"
DEBUG = True
MONGO_DB = 'roac'

app.config.from_object(__name__.split('.')[0])


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


class AttrToItem(object):
    def __init__(self, item_name):
        self.__name__ = item_name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj[self.__name__]

    def __set__(self, obj, value):
        obj[self.__name__] = value

    def __delete__(self, obj):
        del obj[self.__name__]


class Result(dict):
    name = AttrToItem('name')
    path = AttrToItem('path')
    data = AttrToItem('data')


class Record(dict):
    created_at = AttrToItem('created_at')
    name = AttrToItem('name')
    results = AttrToItem('results')

    def __init__(self, mapping):
        dict.__init__(self, mapping)
        self['created_at'] = dateutil.parser.parse(mapping['created_at'])
        self.results = [Result(result) for result in self.results]


@app.route('/api/v1/log', methods=['POST'])
def new_log():
    """
    {
        "title": "Log record schema",
        "type": "object",
        "properties": {
            "created_at": {
                "type": "string",
                "description": "Timestamp of log, formatted in ISO8601",
                "format": "date-time"
            },
            "name": {
                "type": "string",
                "description": "Name of node",
                "format": "host-name"
            },
            "results": {
                "type": "array",
                "items": {
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "path": {
                            "type": "string"
                        },
                        "data": {
                        }
                    },
                    "required": ["name", "data"]
                }
            }
        },
        "required": ["created_at", "name", "results"]
    }
    """
    record = Record(request.get_json())
    log = mongoDB.db.log
    data_id = log.insert(record)
    return jsonify(record)

if __name__ == '__main__':
    app.run()
