from __future__ import absolute_import
from flask.ext.mail import Message
from . import mail, app
from textwrap import dedent
import json


def handle_alarm(alarm, node):
    if alarm.action.type_ in available_actions:
        try:
            available_actions[alarm.action.type_](alarm, node)
        except Exception as e:
            app.logger.exception("Error handling error with %s: %s",
                                 alarm.action.type_, e)
    else:
        app.logger.warning("Alarm with unknown action type, type: %r",
                           alarm.action.type_)


def send_mail(alarm, node):
    msg = Message("Roac alarm: %s" % node.name,
                  recipients=alarm.action.parameters)
    app.logger.debug("Sending email")

    alarm_str, node_str = [json.dumps(x, sort_keys=True, indent=4, separators=(
        ', ', ': '), cls=app.json_encoder) for x in (alarm, node)]
    body = dedent("""
        Node matched an alarm condition.

        Node: {name}

        Alarm: {alarm}

        Details {node}""").format(name=node.name, alarm=alarm_str,
                                  node=node_str)
    msg.body = body
    mail.send(msg)


available_actions = {'mail': send_mail}
