from flask import request
from flask.ext.jsonpify import jsonify
from . import app, server
from .models import Record


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
    log = server.db.log
    log.insert(record)
    return jsonify(record)
