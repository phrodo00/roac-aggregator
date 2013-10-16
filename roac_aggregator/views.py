from flask import request
from flask.ext.jsonpify import jsonify
from . import app, server
from .models import Record, Node
import socket


class InvalidUsage(Exception):
    status_code = 422

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/api/v1/log', methods=['POST'])
def new_log():
    """
    Gets an update from a node in the following schema:

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

    # Compare the node name with the IP's name and discard results that don't
    # match.
    client_ip = request.remote_addr
    client_name = socket.gethostbyaddr(client_ip)[0]
    app.logger.debug("node_ip: %s, client_name: %s, name: %s",
                     client_ip, client_name, record.name)
    if record.name != client_name:
        raise InvalidUsage(
            'Info about nodes should be posted by the same node', 403)

    # Save the log record.
    log = server.db.log
    log.insert(record)

    # Merge data into node.
    nodes = server.db.nodes
    node = nodes.find_one({"name": record.name})
    if node is None:
        node = Node.build(record.name)
    else:
        node = Node(node)
    for result in record.results:
        node.status[Node.status_key(result.name)] = result.data
    nodes.save(node)

    return jsonify(record)
