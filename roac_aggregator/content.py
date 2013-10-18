from flask import render_template
from . import app, server
from .models import Node


@app.route('/nodes')
def nodes():
    nodes_col = server.db.nodes
    nodes = nodes_col.find()
    nodes = [Node(node) for node in nodes]
    return render_template('nodes.html', nodes=nodes)


@app.route('/')
def logs():
    return render_template('index.html')
