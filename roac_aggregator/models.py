import dateutil.parser
from datetime import datetime
from jsonschema import validate as validate_schema
from collections import Sequence, Mapping
from . import alarms
from bson.objectid import ObjectId


class AttrToItem(object):
    """Descriptor that binds to an object's Items"""
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


class SeqAttrToItem(AttrToItem):
    """Validates that set values are Sequences"""
    def __set__(self, obj, value):
        if not isinstance(value, Sequence):
            raise TypeError("value should be a sequence")
        AttrToItem.__set__(self, obj, value)


class MapAttrToItem(AttrToItem):
    """Validates that set values are Mappings"""
    def __set__(self, obj, value):
        if not isinstance(value, Mapping):
            raise TypeError("value should be a mapping")
        AttrToItem.__set__(self, obj, value)


class Result(dict):
    name = AttrToItem('name')
    path = AttrToItem('path')
    data = AttrToItem('data')

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))


class JsonSchema(object):
    """Provides a validate_model that check an object hierarchy against the
    json-schema defined in the schema class variable"""
    schema = None

    @classmethod
    def validate_model(cls, s):
        validate_schema(s, cls.schema)


class Record(dict, JsonSchema):

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
    results = SeqAttrToItem('results')

    @classmethod
    def load(cls, data):
        record = cls(data)
        if not isinstance(record.created_at, datetime):
            record.created_at = dateutil.parser.parse(record.created_at)
        record.results = [Result(result) for result in record.results]
        return record

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))


class Node(dict):
    name = AttrToItem('name')
    status = MapAttrToItem('status')

    @classmethod
    def build(cls, name):
        node = cls()
        node.name = name
        node.status = {}
        return node

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))


class Alarm(dict, JsonSchema):
    schema = {
        'title': 'Alarm criteria',
        'type': 'object',
        'properties': {
            'criteria': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'path': {'type': 'string'},
                        'operator': {'type': 'string'},
                        'value': {'type': ['string', 'number']}
                    },
                    'required': ['path', 'operator', 'value']
                }
            },
            'action': {
                'type': 'object',
                'properties': {
                    'type': {'type': 'string'},
                    'parameters': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                },
                'required': ['type', 'parameters']
            }
        },
        'required': ['criteria', 'action']
    }

    criteria = SeqAttrToItem('criteria')
    action = AttrToItem('action')

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))

    @classmethod
    def load(cls, data):
        alarm = cls(data)
        if '_id' in alarm:
            alarm['_id'] = ObjectId(alarm['_id'])
        alarm.criteria = [Criteria(x) for x in alarm.criteria]
        alarm.action = Action(alarm.action)
        return alarm

    def valid(self):
        valid_criteria = reduce(lambda x, y: x and y, [criterium.valid() for
                                criterium in self.criteria])
        return valid_criteria and self.action.valid()


class Criteria(dict):
    operators = ['gt', 'lt', 'gte', 'lte', '==', 'ne']

    path = AttrToItem('path')
    operator = AttrToItem('operator')
    value = AttrToItem('value')

    def valid(self):
        """Operator has to be one of the strings in operators, and if value is
        a string, it can only be '=='
        """
        if self.operator not in self.operators:
            return False
        if isinstance(self.value, basestring) and self.operator != '==':
            return False
        return True


class Action(dict):
    type_ = AttrToItem('type')
    parameters = SeqAttrToItem('parameters')

    def valid(self):
        if self.type_ not in alarms.available_actions:
            return False
        else:
            return True
