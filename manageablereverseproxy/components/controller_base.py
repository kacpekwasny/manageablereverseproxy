from .component_base import ComponentBase



class ControllerBase:
    """
    Base class for controlers of components.

    `FirewallIP` will have `FirewallIPController` that will be responsible for giving the Managment options by access from the web.
    """


    def register_component(self, component: ComponentBase):
        """
        The usecase I am predicting for now is allowing controller to get reference to the shared object.
        """