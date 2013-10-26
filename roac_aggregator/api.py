from flask import request
from flask.ext.jsonpify import jsonify

import socket
from bson.objectid import ObjectId

from . import app, server, mongodb
from .models import Record, Node, Alarm
from .mongodb import prepare_object_keys
from .alarms import run_alarms


class InvalidUsage(Exception):
    """Exception to throw when a custom HTTP code and json message is wanted"""
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


def validate_ip(ip, name):
    """Compare the node name with the IP's name and discard results that don't
    match.
    """
    ip_name = socket.gethostbyaddr(ip)[0]
    ip_name = ip_name.split('.')[0]
    # Raises exception if ip_name and name don't coincide, unless ip starts
    # with 127, meaning "The connecton is from inside the house".
    if not ip.startswith('127.') and ip_name != name:
        raise InvalidUsage(
            'Info about nodes should be posted by the same node', 403)


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
    try:
        Record.validate_model(request.get_json())
        record = Record.load(request.get_json())
        record = prepare_object_keys(record)

    except Exception as e:
        app.logger.exception(e)
        raise InvalidUsage("Couldn't parse data", 422)

    validate_ip(request.remote_addr, record.name)

    if '_id' in record:
        del record['_id']

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
    new_status = prepare_object_keys(
        dict((result.name, result.data) for result in record.results))
    node.status.update(new_status)
    nodes.save(node)

    #check alarms on node
    run_alarms(node)

    response = jsonify(record)
    response.status = "201 CREATED"
    return response


@app.route('/api/v1/logs/')
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
        else:
            page = 1
    except ValueError as e:
        app.logger.exception(e)
        raise InvalidUsage("Couldn't understand parameters")

    if page < 1:
        raise InvalidUsage("Page has to be at least 1")

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
    if node is None:
        raise InvalidUsage('Node not found', 404)
    return jsonify(node)


@app.route('/api/v1/alarms/')
def get_alarms():
    collection = server.db.alarms
    alarms = collection.find()
    return jsonify(alarms)


@app.route('/api/v1/alarms/', methods=['POST'])
def post_alarms():
    try:
        alarms = []
        for alarm in request.get_json():
            alarms.append(Alarm.load(alarm))
    except Exception as e:
        app.logger.exception(e)
        raise InvalidUsage("Couldn't parse data", 422)

    delete_alarms = [alarm for alarm in alarms if
                     '_destroy' in alarm and alarm['_destroy']]

    save_alarms = [alarm for alarm in alarms if '_destroy' not in alarm and
                   alarm.valid()]  # TODO: Inform of invalid stuff.

    collection = server.db.alarms
    for alarm in save_alarms:
        collection.save(alarm)

    for alarm in delete_alarms:
        if '_id' in alarm:  # No _id means it wasn't in the DB anyways.
            collection.remove(alarm['_id'])

    return jsonify(save_alarms)


@app.route('/api/v1/alarms/<id>', methods=['DELETE'])
def delete_alarm(id):
    id = ObjectId(id)
    alarms = server.db.alarms
    alarm = alarms.find_one({'_id': id})
    if alarm is None:
        raise InvalidUsage('Alarm not found', 404)
    alarms.remove(id)
    return jsonify({'message': 'done'})
