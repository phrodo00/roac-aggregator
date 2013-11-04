from __future__ import absolute_import
from collections import Mapping, Sequence, deque
from numbers import Number
from . import server, app
from .models import Alarm
from .alarm_handlers import handle_alarm


# Don't want to put too much stuff in the alarm class, so it'll all be handled
# here, C style.

# This would REALLY benefit from unit testing (can anyone say technical debt?)


def run_alarms(node):
    collection = server.db.alarms
    alarms = collection.find()
    for alarm in alarms:
        alarm = Alarm.load(alarm)
        if evaluate_alarm(alarm, node):
            app.logger.debug('Alarm match! %r', alarm)
            handle_alarm(alarm, node)


def evaluate_alarm(alarm, node):
    results = [evaluate_criterium(criterium, node) for criterium in
               alarm.criteria]
    return any(results) and (len(results) > 0)


def evaluate_criterium(crit, node):
    values = path_values(crit.path, node)
    results = []
    for i in values:
        # If the value at path is a number try to conver the value to
        # number.
        value = crit.value
        if isinstance(i, Number):
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass  # oh well...

        if isinstance(i, bool):
            value = value.lower in ['true', 't']

        if isinstance(i, Number) and isinstance(value, Number):
            # If both i and value are numbers we can use number comparisson
            if crit.operator == "lte":
                results.append(i <= value)
                continue
            elif crit.operator == "lt":
                results.append(i < value)
                continue
            elif crit.operator == "gte":
                results.append(i >= value)
                continue
            elif crit.operator == "gt":
                results.append(i > value)
                continue
        if crit.operator == "==":
            results.append(i == value)
        elif crit.operator == "ne":
            results.append(i != value)

    if len(results) == 0:
        return False
    return any(results)


def path_values(path, obj):
    values = []
    traverse_path(path, obj, lambda x: values.append(x))
    return values


def traverse_path(path, obj, fn):
    """calls fn on the objects that are at the end of path.
    path is a string or list representing keys in dictionaries.
    For every dictionary in the obj hierarchy, if there's a match with the
    first element in the path, enter the dictionary and remove the component
    from the path.
    """

    if isinstance(path, basestring):
        path = path.split('.')
    if not isinstance(path, deque):
        path = deque(path)

    if len(path) == 0:
        return fn(obj)

    # Shortcircuit on strings since they are sequences too.
    if isinstance(obj, basestring):
        return None
    if isinstance(obj, Mapping):
        comp = path.popleft()
        if comp in obj:
            return traverse_path(deque(path), obj[comp], fn)
        else:
            return None
    if isinstance(obj, Sequence):
        return [traverse_path(deque(path), o, fn) for o in obj]
    return None
