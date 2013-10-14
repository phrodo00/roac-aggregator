from flask import json as flask_json
from bson.objectid import ObjectId


class JSONEncoder(flask_json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return flask_json.JSONEncoder.default(self, o)
