import dateutil.parser


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


class Record(dict):
    created_at = AttrToItem('created_at')
    name = AttrToItem('name')
    results = AttrToItem('results')

    def __init__(self, mapping):
        dict.__init__(self, mapping)
        self['created_at'] = dateutil.parser.parse(mapping['created_at'])
        self.results = [Result(result) for result in self.results]
