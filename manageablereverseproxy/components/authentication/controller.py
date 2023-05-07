
from flask import Blueprint

from .authentication import Authentication

AUTHENTICATION = Authentication()

AUTHENTICATION_CONTROLLER = Blueprint("authentication_controller", __name__, url_prefix='/authentication-controller')



