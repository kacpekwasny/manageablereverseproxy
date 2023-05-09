
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.jwt_manager import ExpiredSignatureError

from .models import User
from ..component_base import ComponentBase
from ...logger import InheritLogger
from ...wrapperclass import MyRequest, MyResponse, HeadersPrivate

SimpleHTTPResponse = tuple[str, int]


class Authentication(ComponentBase, InheritLogger):


    def process_request(self, r: MyRequest) -> MyResponse | MyRequest:
        r = self.remove_headers(r, [h.value for h in HeadersPrivate])
        r = self.authenticate_request(r)
        return r
    
    def remove_headers(self, r: MyRequest, headers: list[str]) -> MyRequest:
        """
        Clear headers that are used internally.
        """
        for h in headers:
            r.headers.remove(h)
        return r

    def authenticate_request(self, r: MyRequest) -> MyRequest:
        """
        If the request has cookies with token 
        """
        try:
            verify_jwt_in_request(optional=True)
        except ExpiredSignatureError:
            return r
        
        user_id = get_jwt_identity()
        print(f"{user_id=}")
        if user_id is None:
            return r
        
        user: User = User.query.filter_by(user_id=user_id).first()
        print("found user:", user)

        if user is None:
            return r

        r = self.set_headers_for_authenticated(r, user)
        r.user = user
        return r

    def set_headers_for_authenticated(self, r: MyRequest, u: User) -> MyRequest:
        r.headers.set(HeadersPrivate.USER_ID, u.user_id)
        r.headers.set(HeadersPrivate.USERNAME, u.username)
        r.headers.set(HeadersPrivate.USER_ROLES, u.roles)
        return r



