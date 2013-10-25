#!/usr/bin/env python
from roac_aggregator import app

app.debug = True

if __name__ == '__main__':
    app.run(host='0.0.0.0')
