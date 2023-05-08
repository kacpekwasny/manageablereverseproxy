from pathlib import Path
from flask import Flask, jsonify, request, Blueprint, send_from_directory
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

from .authentication import Authentication
from .models import UserDB
from ...app import add_commit

FRONTEND_DIR = str(Path(__file__).parent / "frontend")

AUTHENTICATION = Authentication()

AUTHENTICATION_BP = Blueprint("authentication_controller", __name__, url_prefix='/auth')

def hash_password(password: str) -> str:
    # TODO
    return password





# NOTE: This is just a basic example of how to enable cookies. This is
#       vulnerable to CSRF attacks, and should not be used as is. See
#       csrf_protection_with_cookies.py for a more complete example!


# Use the set_access_cookie() and set_refresh_cookie() on a response
# object to set the JWTs in the response cookies. You can configure
# the cookie names and other settings via various app.config options
@AUTHENTICATION_BP.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = UserDB.query.filter_by(username=username, passhash=hash_password(password)).first()
    if user is None:
        return jsonify({'login': False}), 401

    # Create the tokens we will be sending back to the user
    access_token = create_access_token(identity=user.user_id)
    refresh_token = create_refresh_token(identity=user.user_id)

    # Set the JWT cookies in the response
    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    print(f"{resp.cookies}")
    return resp, 200

@AUTHENTICATION_BP.route('/login', methods=['GET'])
def login_form():
    return send_from_directory(FRONTEND_DIR, "login.html")

# Same thing as login here, except we are only setting a new cookie
# for the access token.
@AUTHENTICATION_BP.route('/refresh', methods=['POST'])
@jwt_required()
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


# Because the JWTs are stored in an httponly cookie now, we cannot
# log the user out by simply deleting the cookie in the frontend.
# We need the backend to send us a response to delete the cookies
# in order to logout. unset_jwt_cookies is a helper function to
# do just that.
@AUTHENTICATION_BP.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200

@AUTHENTICATION_BP.route('/register', methods=['POST'])
def register_request():
    """
    Inbound request for user Register (account doesnt exist).
    """
    json = request.json
    username = json["username"]
    if not UserDB.query.filter_by(username=username).first() is None:
        return jsonify({"registered": True, "msg": "User with such username exists."}), 409 # HTTP Conflict

    password = json["password"]
    if len(password) < 1:
        return jsonify({"registered": True, "msg": "You realy could have given that single charachter :/"}), 422 # Unprocessable Content


    passhash = hash_password(password)
    user = UserDB(username=username, passhash=passhash)
    add_commit(user)
    return jsonify({"registered": True}), 200


# We do not need to make any changes to our protected endpoints. They
# will all still function the exact same as they do when sending the
# JWT in via a header instead of a cookie
@AUTHENTICATION_BP.route('/api/example', methods=['GET'])
@jwt_required()
def protected():
    username = get_jwt_identity()
    return jsonify({'hello': 'from {}'.format(username)}), 200

