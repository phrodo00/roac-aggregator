from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING


class MongoDB(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    @property
    def client(self):
        if not hasattr(self, '_client'):
            self._client = MongoClient(
                self.app.config.setdefault('MONGO_HOST', 'localhost'))
        return self._client

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = self.client[self.app.config['MONGO_DB']]
        return self._db
