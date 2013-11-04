from __future__ import absolute_import
from pymongo import MongoClient, ASCENDING, DESCENDING
from collections import MutableMapping, MutableSequence


def prepare_object_keys(obj, repl_str='_'):
    """ Recursively replaces dots in mapping keys by underscores to save them
    to mongodb. Other objects are left alone. (Mappings must be of the
    muttable quality).
    Use only on incoming data. Using it on repetedly on saved data results in
    ever increasing repl_str repetitions."""
    if isinstance(obj, basestring):
        return obj  # Short-circuit on strings, since they are sequences too.
    if isinstance(obj, MutableMapping):
        new_obj = obj.__class__()
        for key in obj:
            #Replace . by repl_str, replace repl_str by it 2 times.
            new_key = key.replace(
                repl_str, repl_str * 2).replace('.', repl_str)
            new_obj[new_key] = prepare_object_keys(obj[key])
        return new_obj
    if isinstance(obj, MutableSequence):
        new_obj = obj.__class__()
        for i, x in enumerate(obj):
            new_obj.insert(i, prepare_object_keys(x))
        return new_obj
    return obj
