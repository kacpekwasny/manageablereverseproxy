from flask import Flask, send_from_directory, request

from manageablereverseproxy import REPO_DIR
from manageablereverseproxy.wrapperclass import HeadersPrivate


app = Flask(__name__)


def require_auth(func):
    def wraped(*args, **kwargs):
        print(HeadersPrivate.USER_ID.value.__repr__(), "X-Priv-Mrp-User-Id")
        print(HeadersPrivate.USER_ID.value == "X-Priv-Mrp-User-Id")
        print(request.headers.get("X-Priv-Mrp-User-Id"))

        if request.headers.get(HeadersPrivate.USER_ID.value, None) is None:
            return "You are not logged in!", 401
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
            username: {request.headers.get(HeadersPrivate.USERNAME.value)}
            <br>
            user_id: {request.headers.get(HeadersPrivate.USER_ID.value)}
            """

if __name__ == "__main__":
    app.run(port=8001, debug=True)