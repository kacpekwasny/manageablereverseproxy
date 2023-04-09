from .controller_base import ControllerBase
from ..wrapperclass import Request, Response

class ComponentBase:

    def process_request(self, r: Request) -> Response | Request:
        """
        Component has to overwrite this method.

        Example:
            comp1 -> comp2 -> comp3
            if copm1.process_request() returns Response it will not be passed to 
        """
        raise NotImplementedError("This function has to be implemented by child class.")

    def register_controller(self, controller: ControllerBase):
        """
        The usecase I am predicting for now is allowing controller to get reference to the shared object.
        """