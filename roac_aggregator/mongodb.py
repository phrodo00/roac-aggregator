from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING


class MongoDB(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.client = MongoClient(
            app.config.setdefault('MONGO_HOST', 'localhost',))
        self.db = self.client[app.config['MONGO_DB']]
