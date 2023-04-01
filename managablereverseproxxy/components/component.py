from ..wrapperclass.request import Request
from ..wrapperclass.response import Response

class ComponentBase:

    def process_request(self, r: Request) -> Response | Request:
        """
        Component has to overwrite this method.

        Example:
            comp1 -> comp2 -> comp3
            if copm1.process_request() returns Response it will not be passed to 

        """

