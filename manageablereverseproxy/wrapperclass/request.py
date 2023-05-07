from __future__ import annotations

from typing import TYPE_CHECKING
from  flask import Request as flRequest
from requests.structures import CaseInsensitiveDict
from werkzeug.datastructures import Headers

from .inherit_obj import ObjectInherit

if TYPE_CHECKING:
    from ..components.authentication.models import UserDB

class Request(ObjectInherit, flRequest):
    """
    Wrapper for `flask.Request` that adds aditional fields.
    """

    ip_address: str
    "IP address of the client."

    user: UserDB | None = None
    """User associated with this request."""


    def __init__(self, flask_request: flRequest, *args, **kwargs) -> None:
        super().__init__(flask_request, *args, **kwargs)
        self._mutable_headers()
        self._set_ipaddr(flask_request)

    def _set_ipaddr(self, fr: flRequest):
        """
        Set `ip_address` either from `header`, or from `remote_addr`.
        """
        ip_address = fr.environ.get('HTTP_X_FORWARDED_FOR')
        self.ip_address = fr.remote_addr if ip_address is None else ip_address

    def _mutable_headers(self) -> None:
        new_headers = Headers()
        for k, v in self.headers:
            new_headers[k] = v
        self.headers = new_headers





