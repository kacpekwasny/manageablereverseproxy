from  flask import Request as flRequest

from .inherit_obj import ObjectInherit


class Request(ObjectInherit, flRequest):
    """
    Wrapper for `flask.Request` that adds aditional fields.
    """

    ip_address: str
    "IP address of the client."

    def __init__(self, flask_request: flRequest, *args, **kwargs) -> None:
        super().__init__(flask_request, *args, **kwargs)

        self._set_ipaddr(flask_request)

    def _set_ipaddr(self, fr: flRequest):
        """
        Set `ip_address` either from `header`, or from `remote_addr`.
        """
        ip_address = fr.environ.get('HTTP_X_FORWARDED_FOR')
        self.ip_address = fr.remote_addr if ip_address is None else ip_address




