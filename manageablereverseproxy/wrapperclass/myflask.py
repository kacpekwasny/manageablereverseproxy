from flask import Flask

from .myrequest import MyRequest
from .myresponse import MyResponse


class MyFlask(Flask):
    request_class = MyRequest
    response_class = MyResponse
