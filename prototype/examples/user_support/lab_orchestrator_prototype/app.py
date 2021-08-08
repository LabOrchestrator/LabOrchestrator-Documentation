from typing import Optional

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class CC:
    _obj: Optional['ControllerCollection'] = None

    @staticmethod
    def get() -> 'ControllerCollection':
        if CC._obj is None:
            raise KeyError()
        return CC._obj

    @staticmethod
    def set(obj: 'ControllerColction'):
        CC._obj = obj
