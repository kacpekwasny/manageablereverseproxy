
from flask import Response as flResponse, make_response, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, verify_jwt_in_request
from flask_jwt_extended.jwt_manager import ExpiredSignatureError

from .models import UserDB
from ...headers import HeadersPrivate, HeadersPublic
from ..component_base import ComponentBase
from ...app import add_commit, db, jwt
from ...logger import InheritLogger
from ...wrapperclass import Request, Response


SimpleHTTPResponse = tuple[str, int]


class Authentication(ComponentBase, InheritLogger):


    def process_request(self, r: Request) -> Response | Request:
        r = self.remove_headers(r, [h.value for h in HeadersPrivate])
        r = self.authenticate_request(r)
        return r
    
    def remove_headers(self, r: Request, headers: list[str]) -> Request:
        """
        Clear headers that are used internally.
        """
        for h in headers:
            r.headers.remove(h)
        return r

    def authenticate_request(self, r: Request) -> Request:
        """
        If the request has cookies with token 
        """
        try:
            verify_jwt_in_request(optional=True)
        except ExpiredSignatureError:
            print("not auth")
            return r
        
        user_id = get_jwt_identity()
        print(f"{user_id=}")
        if user_id is None:
            return r
        
        user: UserDB = UserDB.query.filter_by(user_id=user_id).first()
        print("found user:", user)

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



