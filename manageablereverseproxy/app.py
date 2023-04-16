from flask import Flask
from flask.scaffold import setupmethod
from flask_sqlalchemy import SQLAlchemy

from . import REPO_DIR

app = Flask(__name__)
app.debug = True


app.config.from_pyfile('config.py')

# app.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql://{app.config['DB_USER']}:{app.config['DB_PASSWORD']}"
#                                          f"@{app.config['DB_HOST']}/{app.config['DB_NAME']}")

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{str(REPO_DIR / 'test.db')}"


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def add_commit(*args):
    with app.app_context():
        for a in args:
            db.session.add(a)
            db.session.commit()
