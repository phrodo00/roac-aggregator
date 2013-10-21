from flask import render_template
from . import app


@app.route('/nodes')
def nodes():
    return render_template('nodes.html')


@app.route('/')
def logs():
    return render_template('index.html')