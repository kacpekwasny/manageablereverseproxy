from flask import Flask, session
from flask.scaffold import setupmethod
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

from . import REPO_DIR

app = Flask(__name__)

# Configure application to store JWTs in cookies. Whenever you make
# a request to a protected endpoint, you will need to send in the
# access or refresh JWT via a cookie.
app.config['JWT_TOKEN_LOCATION'] = ['cookies']

# Only allow JWT cookies to be sent over https. In production, this
# should likely be True
app.config['JWT_COOKIE_SECURE'] = False


# Disable CSRF protection for this example. In almost every case,
# this is a bad idea. See examples/csrf_protection_with_cookies.py
# for how safely store JWTs in cookies
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config.from_pyfile('secret.py')


jwt = JWTManager(app)
app.debug = True

# app.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql://{app.config['DB_USER']}:{app.config['DB_PASSWORD']}"
#                                          f"@{app.config['DB_HOST']}/{app.config['DB_NAME']}")

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{str(REPO_DIR / 'assets/test.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app, session_options=dict(expire_on_commit=False))


def add_commit(*args):
    with app.app_context():
        for a in args:
            db.session.add(a)
        db.session.commit()

# load the reverse proxy
from . import reverseproxy



