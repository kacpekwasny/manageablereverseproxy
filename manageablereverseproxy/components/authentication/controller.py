

from datetime import timedelta, datetime, timezone
import json
from pathlib import Path
from flask import Flask, jsonify, render_template, request, Blueprint, send_from_directory, make_response, abort
from flask_jwt_extended import (
    JWTManager, create_access_token,
    get_jwt_identity, set_access_cookies,
    unset_jwt_cookies, verify_jwt_in_request
)
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, JWTManager, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request, unset_access_cookies
from flask_jwt_extended.jwt_manager import ExpiredSignatureError, CSRFError

from .models import db, User
from .authentication import Authentication
from ..config import ConfigBase
from ...wrapperclass import MyRequest
from ... import REPO_DIR
from ...db import db


CONFIG_FILE = str(Path(__file__).parent / "config.json")


class AuthConfig(ConfigBase):
    refresh_delta = 15 * 60   # seconds
    login_delta   = 15 * 60   # seconds



def hash_password(password: str) -> str:
    # TODO
    return password



def authenticate(request: MyRequest) -> MyRequest:
    try:
        print(f"authenticate {request.cookies=}")
        vjir = verify_jwt_in_request(optional=True)
        if vjir is None:
            raise 
        user_id = get_jwt()["sub"]
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            abort(500, "User is defined in cookie, but doesnt exist in database. Have you performed 'drop tables'? Hmmm?.")
        request.set_user(user)
        return request
    except (RuntimeError, KeyError, ExpiredSignatureError, CSRFError) as e:
        # Case where there is not a valid JWT. Just return the original response
        return request


def require_auth(f):
    def wraped_require_auth(*args, **kwargs):
        if request.user is None:
            return render_template("authentication/auth_required.html", request_path=request.path), 401
        return f(*args, **kwargs)
    wraped_require_auth.__name__ = f.__name__
    return wraped_require_auth


def app_add_authentication_module(app: Flask,
                                  url_prefix="/auth",
                                  config_path: str=CONFIG_FILE):
    # NOTE: This is just a basic example of how to enable cookies. This is
    #       vulnerable to CSRF attacks, and should not be used as is. See
    #       csrf_protection_with_cookies.py for a more complete example!

    config = AuthConfig(config_path)
    
    auth = Blueprint("authentication_controller", __name__, url_prefix=url_prefix)

    jwt = JWTManager()
    
    # Configure application to store JWTs in cookies. Whenever you make
    # a request to a protected endpoint, you will need to send in the
    # access or refresh JWT via a cookie.
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']

    # Only allow JWT cookies to be sent over https. In production, this
    # should likely be True
    app.config['JWT_COOKIE_SECURE'] = False


    # Disable CSRF protection for this example. In almost every case,
    # this is a bad idea. See examples/csrf_protection_with_cookies.py
    # for how safely store JWTs in cookies
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False


    @auth.before_app_request
    def before_every_request():
        """
        Every request will be passed all the components.
        """
        authenticate(request)


    # Using an `after_request` callback, we refresh any token that is within 30
    # minutes of expiring. Change the timedeltas to match the needs of your application.
    @auth.after_app_request
    def refresh_expiring_jwts(response):
        try:
            # This is a response for a logout action. Do not refresh cookie.
            if response.logout:
                return response
            
            vjir = verify_jwt_in_request(optional=True)
            if vjir is None:
                return response
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(seconds=config.refresh_delta))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError, ExpiredSignatureError, CSRFError) as e:
            # Case where there is not a valid JWT. Just return the original response
            unset_jwt_cookies(response)
            return response


    # Use the set_access_cookie() and set_refresh_cookie() on a response
    # object to set the JWTs in the response cookies. You can configure
    # the cookie names and other settings via various app.config options
    @auth.route('/login', methods=['POST'])
    def login():
        if isinstance(request.user, User):
            return jsonify(msg="You need to log out first."), 401

        username = request.json.get('username', None)
        password = request.json.get('password', None)
        user = User.query.filter_by(username=username, passhash=hash_password(password)).first()
        if user is None:
            return jsonify({'login': False}), 401

        # Create the tokens we will be sending back to the user
        access_token = create_access_token(identity=user.user_id,
                                        expires_delta=timedelta(seconds=config.login_delta)) # TODO: Configurable option

        # Set the JWT cookies in the response
        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        return resp, 200

    @auth.route('/login', methods=['GET'])
    def login_form():
        return render_template("authentication/login.html", username=(request.user and request.user.username))

    @auth.route('/get-my-info', methods=['GET'])
    def get_info():
        if isinstance(request.user, User):
            return make_response(jsonify(authenticated=True,
                                         username=request.user.username,
                                         user_id=request.user.user_id),
                                200)
        
        return make_response(jsonify(authenticated=False),
                             401)

    # Because the JWTs are stored in an httponly cookie now, we cannot
    # log the user out by simply deleting the cookie in the frontend.
    # We need the backend to send us a response to delete the cookies
    # in order to logout. unset_jwt_cookies is a helper function to
    # do just that.
    @auth.route('/logout', methods=['GET'])
    @require_auth
    def logout():
        resp = make_response(render_template("authentication/logout.html"), 200)
        unset_jwt_cookies(resp)
        resp.logout_flag()
        return resp

    @auth.route('/register', methods=['GET'])
    def register_form():
        return render_template("authentication/register.html", username=(request.user and request.user.username))

    @auth.route('/register', methods=['POST'])
    def register_request():
        """
        Inbound request for user Register (account doesnt exist).
        """
        json = request.json
        username = json["username"]
        if not User.query.filter_by(username=username).first() is None:
            return jsonify({"registered": True, "msg": "User with such username exists."}), 409 # HTTP Conflict

        if len(username) < 1:
            return jsonify({"registered": False, "msg": "You realy could have given that single charachter for 'username' :/"}), 422 # Unprocessable Content

        password = json["password"]
        if len(password) < 1:
            return jsonify({"registered": False, "msg": "You realy could have given that single charachter for 'password' :/"}), 422 # Unprocessable Content


        passhash = hash_password(password)
        user = User(username=username, passhash=passhash)
        db.session.add(user)
        db.session.commit()
        return jsonify({"registered": True}), 200


    # We do not need to make any changes to our protected endpoints. They
    # will all still function the exact same as they do when sending the
    # JWT in via a header instead of a cookie
    @auth.route('/api/example', methods=['GET'])
    @require_auth
    def protected():
        user_id = get_jwt_identity()
        return jsonify({'hello': f'{user_id=}, {request.user.username=}'}), 200

    app.register_blueprint(auth)
    jwt.init_app(app)



