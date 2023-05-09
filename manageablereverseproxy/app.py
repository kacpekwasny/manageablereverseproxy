from flask import Flask, session
from flask.scaffold import setupmethod
from flask_sqlalchemy import SQLAlchemy

from . import REPO_DIR
from .wrapperclass import MyFlask


def create_app():
    app = MyFlask(__name__)
    app.config.from_pyfile('secret.py')
    return app



# app.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql://{app.config['DB_USER']}:{app.config['DB_PASSWORD']}"
#                                          f"@{app.config['DB_HOST']}/{app.config['DB_NAME']}")





