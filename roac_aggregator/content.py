from __future__ import absolute_import
from flask import render_template, redirect, url_for
from . import app


@app.route('/')
def nodes():
    return render_template('nodes.html')


@app.route('/nodes')
def redirect_to_index():
    return redirect(url_for(nodes.__name__))


@app.route('/log')
def logs():
    return render_template('log.html')


@app.route('/alarms')
def list_alarms():
    return render_template('alarms.html')
