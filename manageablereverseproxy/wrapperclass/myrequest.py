from __future__ import annotations

from enum import Enum
from flask import Request
from werkzeug.datastructures import Headers


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..components.authentication.models import User


class HeadersPrivate(Enum):
    # Private headers
    USERNAME  = "X-Priv-Mrp-Username"
    USER_ID   = "X-Priv-Mrp-User-Id"


class MyRequest(Request):
    
    user: User = None
    ip_address: str = ""

    def __init__(self, environ, populate_request: bool = True, shallow: bool = False) -> None:
        super().__init__(environ, populate_request, shallow)
        self._mutable_headers()
        self._render_ipaddress()
    
    def set_user(self, u: User):
        self.user = u
        self.headers.add_header(HeadersPrivate.USER_ID.value, u.user_id)
        self.headers.add_header(HeadersPrivate.USERNAME.value, u.username)
    
    def _mutable_headers(self) -> None:
        """
        Convert headers into mutable type.
        Sanitize headers.
        """
        new_headers = Headers()
        for k, v in self.headers:
            try:
                HeadersPrivate(k)
                # no error -> k is a private header
            except ValueError:
                # error -> k is not a private header, and as such will be kept
                new_headers[k] = v
        self.headers = new_headers

    def _render_ipaddress(self) -> None:
        self.ip_address = self.headers.get("X-Real-IP", self.remote_addr)

