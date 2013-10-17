from flask import json as flask_json
from bson.objectid import ObjectId
from pymongo.cursor import Cursor


class JSONEncoder(flask_json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, Cursor):
            return [r for r in o]
        return flask_json.JSONEncoder.default(self, o)
