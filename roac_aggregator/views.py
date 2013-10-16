from flask import request
from flask.ext.jsonpify import jsonify
from . import app, server
from .models import Record, Node


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

    nodes = server.db.nodes
    node = nodes.find_one({"name": record.name})
    if node is None:
        node = Node.build(record.name)
    else:
        node = Node(node)
    for result in record.results:
        node.status[result.name] = result.data
    nodes.save(node)

    return jsonify(record)
