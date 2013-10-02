#!/usr/bin/env python

from __future__ import print_function
from flask import Flask, request

app = Flask(__name__)
app.debug = True

@app.route('/log/<string:node>', methods=['POST'])
def new_log(node):
    app.logger.info(request.get_json())
    return node

if __name__ == '__main__':
    app.run()
