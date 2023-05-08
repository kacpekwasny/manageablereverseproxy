from datetime import datetime
from datetime import timedelta
from datetime import timezone
from traceback import print_exc

from flask import Flask, Request, request, jsonify, Blueprint, make_response

from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, JWTManager, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request
from flask_jwt_extended.jwt_manager import ExpiredSignatureError, CSRFError



class User:
    def __init__(self, username) -> None:
        self.username = username


class MyRequest(Request):
    user: User = None

    def set_user(self, u: User):
        print(type(self))
        self.user = u

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
jwt = JWTManager()

def app_addons(app: Flask):
    app.register_blueprint(auth)
    jwt.init_app(app)




def authenticate(request: MyRequest) -> MyRequest:
    print("authenticate")
    try:
        verify_jwt_in_request(optional=True)
        username = get_jwt()["sub"]
        request.set_user(User(username))
        print(request.user)
        return request
    except (RuntimeError, KeyError, ExpiredSignatureError, CSRFError) as e:
        # Case where there is not a valid JWT. Just return the original response
        print("unauth:", e)
        return request


def require_auth(f):
    def wraped_require_auth(*args, **kwargs):
        print(request.user)
        if request.user is None:
            return make_response(jsonify({"msg": "you need to be logged in for this endpoint"})), 401
        return f(*args, **kwargs)
    return wraped_require_auth


@auth.before_app_request
def before_every_request():
    """
    Every request will be passed all the components.
    """
    print(f"{request.cookies=}")
    authenticate(request)
    print(request.user)
    print("before:")


# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring. Change the timedeltas to match the needs of your application.
@auth.after_app_request
def refresh_expiring_jwts(response):
    try:
        verify_jwt_in_request(optional=True)
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError, ExpiredSignatureError, CSRFError) as e:
        # Case where there is not a valid JWT. Just return the original response
        print("after:", e)
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
    return jsonify(foo="bar")


if __name__ == "__main__":
    app = create_app()
    app_addons(app)
    app.run(debug=True)