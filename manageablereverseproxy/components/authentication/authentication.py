

from enum import Enum

from ...logger import InheritLogger

from .user import User
from .models import UserDB
from ..component_base import ComponentBase
from ...wrapperclass import Request, Response


class HeadersPublic(Enum):
    # Private headers
    USER_ID    = "Mrp-User-Id"
    USER_TOKEN = "Mrp-User-Token"


class HeadersPrivate(Enum):
    # Private headers
    USERNAME  = "Priv-Mrp-Username"
    USER_ID   = "Priv-Mrp-User-Id"
    USER_ROLES = "Priv-Mrp-User-Role"



class Authentication(ComponentBase, InheritLogger):


    def process_request(self, r: Request) -> Response | Request:
        r = self.remove_headers(r, [h.value for h in HeadersPrivate])

        r = self.user_action(r)
        if isinstance(r, Response):
            return r

        r = self.authenticate_request(r)
        r = self.remove_headers(r, [h.value for h in HeadersPublic])
        return r
    
    def remove_headers(self, r: Request, headers: list[str]) -> Request:
        """
        Clear headers that are used internally.
        """
        for h in headers:
            r.headers.remove(h)
        return r

    def user_action(self, r: Request) -> Request | Response:
        """
        Check the method and URL, maybe this request is for the API to register, login or logout.
        """

        self.lgr.debug(f"user_action: {r.path}")

        return r            

    def authenticate_request(self, r: Request) -> Request:
        """
        If the request has headers with 
        """

        user_id = r.headers.get(HeadersPublic.USER_ID.value, None)
        token   = r.headers.get(HeadersPublic.USER_TOKEN.value, None)
        if user_id is None or token is None:
            return r
        
        user: UserDB = UserDB.query.filter_by(user_id=user_id, token=token).first()

        if user is None:
            return r

        r = self.set_headers_for_authenticated(r, user)
        r.user = user
        return r

    
    def set_headers_for_authenticated(self, r: Request, u: UserDB) -> Request:
        r.headers.set(HeadersPrivate.USER_ID, u.user_id)
        r.headers.set(HeadersPrivate.USERNAME, u.username)
        r.headers.set(HeadersPrivate.USER_ROLES, u.roles)
        return r
        




