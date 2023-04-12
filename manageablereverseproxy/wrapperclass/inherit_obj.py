"""
Create object that inherits from a class that I do not create an instance of.

fr = flask.Request()

class Request(flask.Request):
    "How to create `Request` that will be a child of `flask.Request` ?"

"""

import typing as T


class ObjectInherit:

    def __init__(self, parent_class_instance) -> None:
        self._parent = parent_class_instance
    
    def __getattr__(self, __name: str) -> T.Any:
        return getattr(self._parent, __name)

