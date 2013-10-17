from flask import request
from flask.ext.jsonpify import jsonify
from . import app, server, mongodb
from .models import Record, Node
import socket


class InvalidUsage(Exception):
    status_code = 400

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


@app.route('/api/v1/log/', methods=['POST'])
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
    try:
        record = Record(request.get_json())
    except Exception:
        raise InvalidUsage("Couldn't parse data", 422)

    # Compare the node name with the IP's name and discard results that don't
    # match.
    client_ip = request.remote_addr
    client_name = socket.gethostbyaddr(client_ip)[0]
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


@app.route('/api/v1/logs')
def get_logs():
    try:
        count = request.args.get('count')
        if count:
            count = int(count)
        else:
            count = 20
        page = request.args.get('page')
        if page:
            page = int(page)
    except ValueError:
        raise InvalidUsage("Couldn't understand parameters")

    if page < 1:
        raise InvalidUsage("Page has to be at least 1")

    app.logger.debug('count: %s', count)
    log = server.db.log
    records = log.find().sort('created_at', mongodb.DESCENDING).limit(count)
    if page:
        page = page - 1
        skip = page * count
    records.skip(skip)
    return jsonify(records)


@app.route('/api/v1/nodes/')
def get_nodes():
    nodes_col = server.db.nodes
    nodes = nodes_col.find(fields={"name": True})
    nodes = [n["name"] for n in nodes]
    return jsonify(nodes)


@app.route('/api/v1/nodes/<name>')
def get_node(name):
    nodes = server.db.nodes
    node = nodes.find_one({"name": name})
    return jsonify(node)
