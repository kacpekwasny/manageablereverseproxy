import flask

from .inherit_obj import ObjectInherit


class Response(ObjectInherit, flask.Response):
    """
    Wrapper for `flask.Response` that adds aditional fields.
    """


