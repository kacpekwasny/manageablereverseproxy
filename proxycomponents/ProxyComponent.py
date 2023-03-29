import typing as T
from flask import Request, Response

class ProxyComponent:
    """
    Parent class for all classes that will be chained into the proxy.
    """

    def process(self, r: Request) -> Response | str | T.Any:
        """
        Base class that processes the incoming request, and passes it further.
        """

