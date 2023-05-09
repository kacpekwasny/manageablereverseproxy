from ..wrapperclass import MyRequest, MyResponse

class ComponentBase:

    def process_request(self, r: MyRequest) -> MyResponse | MyRequest:
        """
        Component has to overwrite this method.

        Example:
            comp1 -> comp2 -> comp3
            if copm1.process_request() returns Response it will not be passed to 
        """
        raise NotImplementedError("This function has to be implemented by child class.")

