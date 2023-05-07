
from flask import Response as flResponse


from .models import UserDB, token_generator
from ...headers import HeadersPrivate, HeadersPublic
from ..component_base import ComponentBase
from ...app import add_commit, db
from ...logger import InheritLogger
from ...wrapperclass import Request, Response


SimpleHTTPResponse = tuple[str, int]


class Authentication(ComponentBase, InheritLogger):


    def process_request(self, r: Request) -> Response | Request:
        r = self.remove_headers(r, [h.value for h in HeadersPrivate])

        r = self.authenticate_request(r)

        r = self.user_action(r)
        if not isinstance(r, Request):
            return r

        r = self.remove_headers(r, [h.value for h in HeadersPublic])
        return r
    
    def remove_headers(self, r: Request, headers: list[str]) -> Request:
        """
        Clear headers that are used internally.
        """
        for h in headers:
            r.headers.remove(h)
        return r

    def user_action(self, r: Request) -> Request | SimpleHTTPResponse:
        """
        Check the method and URL, maybe this request is for the API to register, login or logout.
        """
        if r.path == "/register":
            return self.register_request(r)
        if r.path == "/login":
            return self.login_request(r)
        if r.path == "/logout":
            return self.logout_request(r)
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

    def register_request(self, r: Request) -> SimpleHTTPResponse:
        """
        Inbound request for user Register (account doesnt exist).
        """
        json = r.json
        username = json["username"]
        if not UserDB.query.filter_by(username=username).first() is None:
            return "User with such username exists.", 409 # Conflict

        password = json["password"]
        if len(password) < 1:
            return "You realy could have given that single charachter :/", 422 # Unprocessable Content


        passhash = self.hash_password(password)
        user = UserDB(username=username, passhash=passhash)
        add_commit(user)
        return "git", 200
    
    def login_request(self, r: Request) -> SimpleHTTPResponse:
        """
        Inbound request for user Login (account exists).
        """
        json = r.json
        username = json["username"]
        password = json["password"]
        passhash = self.hash_password(password)
        user = UserDB.query.filter_by(username=username, passhash=passhash).first()

        if user is None:
            return "Either 'username' or 'password' is incorrect.", 401

        new_token = token_generator()
        user.token = new_token
        db.session.commit()

        Response

        return new_token, 200
    
    def logout_request(self, r: Request) -> SimpleHTTPResponse:
        if r.user is None:
            return "Well, you should be very much logged in, in order to log out.", 401
        r.user.token = token_generator()
        db.session.commit()
        return "Successfuly logged out", 200

    def hash_password(self, password: str) -> str:
        # TODO
        return password





