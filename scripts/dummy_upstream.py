from flask import Flask, send_from_directory, request

from manageablereverseproxy import REPO_DIR
from manageablereverseproxy.headers import HeadersPrivate


app = Flask(__name__)


def require_auth(func):
    def wraped(*args, **kwargs):
        if request.headers.get(HeadersPrivate.USERNAME, None) is None:
            return "You are not logged in!", 404
        return func(*args, **kwargs)
    return wraped

@app.route('/', defaults={'u_path': ''})
@app.route("/<path:u_path>", methods=["GET"])
def index(u_path: str):
    return "<h1> dupa, powtarzam! uwaga, dupa! " + u_path + "</h1>"


@app.route("/favicon.ico")
def dummy():
    return send_from_directory(str(REPO_DIR / "assets"), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/logged")
@require_auth
def logged():
    return f"""
            username: {request.headers.get(HeadersPrivate.USERNAME)}
            <br>
            roles: {request.headers.get(HeadersPrivate.USER_ROLES)}
            """

if __name__ == "__main__":
    app.run(port=8001)