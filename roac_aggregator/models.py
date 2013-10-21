import dateutil.parser
from datetime import datetime
from jsonschema import validate as validate_schema


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

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))


class Record(dict):

    schema = {
        'title': 'Log record schema',
        'type': 'object',
        'properties': {
            'created_at': {
                'description': 'Timestamp of log, formatted in ISO8601',
                'format': 'date-time',
                'type': 'string'
            },
            'name': {
                'description': 'Name of node',
                'format': 'host-name',
                'type': 'string'
            },
            'results': {
                'items': {
                    'properties': {
                        'name': {'type': 'string'},
                        'path': {'type': 'string'},
                        'data': {}
                    },
                    'required': ['name', 'data']
                },
                'type': 'array'
            }
        },
        'required': ['created_at', 'name', 'results']
    }

    created_at = AttrToItem('created_at')
    name = AttrToItem('name')
    results = AttrToItem('results')

    def __init__(self, mapping={}):
        dict.__init__(self, mapping)
        if not isinstance(self.created_at, datetime):
            self.created_at = dateutil.parser.parse(self.created_at)
        self.results = [Result(result) for result in self.results]

    @classmethod
    def validate_model(cls, s):
        validate_schema(s, cls.schema)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))


class Node(dict):
    name = AttrToItem('name')
    status = AttrToItem('status')

    @classmethod
    def build(cls, name):
        node = cls()
        node.name = name
        node.status = {}
        return node

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))
