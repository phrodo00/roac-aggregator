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


def prepare_record(record):
    record['created_at'] = dateutil.parser.parse(record['created_at'])


@app.route('/api/v1/log', methods=['POST'])
def new_log():
    """
    {
        "title": "Log Schema",
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
    record = request.get_json()
    prepare_record(record)
    log = mongoDB.db.log
    data_id = log.insert(record)
    return jsonify(record)

if __name__ == '__main__':
    app.run()
