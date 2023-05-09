from datetime import datetime
from datetime import timedelta
from datetime import timezone
from traceback import print_exc

from flask import Flask, Request, request, jsonify, Blueprint, make_response, Response

from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, JWTManager, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request
from flask_jwt_extended.jwt_manager import ExpiredSignatureError, CSRFError
from werkzeug.datastructures import Headers



class User:
    def __init__(self, username) -> None:
        self.username = username


class MyRequest(Request):
    user: User = None

    def __init__(self, environ, populate_request: bool = True, shallow: bool = False) -> None:
        super().__init__(environ, populate_request, shallow)
        self._mutable_headers()
    

    def set_user(self, u: User):
        print(type(self))
        self.user = u
    

    def _mutable_headers(self) -> None:
        new_headers = Headers()
        for k, v in self.headers:
            new_headers[k] = v
        self.headers = new_headers


class MyFlask(Flask):
    request_class = MyRequest


def create_app():
    app = MyFlask(__name__)

    # If true this will only allow the cookies that contain your JWTs to be sent
    # over https. In production, this should always be set to True
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this in your code!
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    return app


auth = Blueprint("auth", __name__, url_prefix="/auth")
stuff = Blueprint("stuff", __name__, url_prefix="/stuff")
jwt = JWTManager()

def app_addons(app: Flask):
    app.register_blueprint(auth)
    app.register_blueprint(stuff)
    jwt.init_app(app)




def authenticate(request: MyRequest) -> MyRequest:
    try:
        vjir = verify_jwt_in_request(optional=True)
        if vjir is None:
            return
        username = get_jwt()["sub"]
        request.set_user(User(username))
        return request
    except (RuntimeError, KeyError, ExpiredSignatureError, CSRFError) as e:
        # Case where there is not a valid JWT. Just return the original response
        return request


def require_auth(f):
    def wraped_require_auth(*args, **kwargs):
        if request.user is None:
            return make_response(jsonify({"msg": "you need to be logged in for this endpoint"})), 401
        request.headers.set("username", request.user.username)
        return f(*args, **kwargs)
    return wraped_require_auth


@auth.before_app_request
def before_every_request():
    """
    Every request will be passed all the components.
    """
    print("auth before")
    authenticate(request)



# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring. Change the timedeltas to match the needs of your application.
@auth.after_app_request
def refresh_expiring_jwts(response):
    # Response.headers.remove("")
    try:
        vjir = verify_jwt_in_request(optional=True)
        if vjir is None:
            return response
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError, ExpiredSignatureError, CSRFError) as e:
        # Case where there is not a valid JWT. Just return the original response
        unset_jwt_cookies(response)
        return response


@auth.route("/login", methods=["POST"])
def login():
    response = jsonify({"msg": "login successful"})
    access_token = create_access_token(identity="example_user")
    set_access_cookies(response, access_token)
    return response


@auth.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@auth.route("/protected")
@require_auth
def protected():
    return jsonify(foo="bar", user=request.user.username)



@stuff.before_app_request
def pri():
    print("stuff before")

@stuff.route("/")
@require_auth
def hello():
    print("headers", request.headers.get("username"))
    return jsonify(msg=f"hello {request.user.username}, I am blueprint 'stuff'")


if __name__ == "__main__":
    app = create_app()
    app_addons(app)
    app.run(debug=True)



