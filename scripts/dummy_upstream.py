from flask import Flask, redirect, send_from_directory, request

from manageablereverseproxy import REPO_DIR
from manageablereverseproxy.wrapperclass import HeadersPrivate


app = Flask(__name__)


def require_auth(func):
    def wraped(*args, **kwargs):
        if request.headers.get(HeadersPrivate.USER_ID.value, None) is None:
            return redirect("/auth/login"), 302
        return func(*args, **kwargs)
    return wraped

@app.route('/', defaults={'u_path': ''})
@app.route("/<path:u_path>", methods=["GET"])
def index(u_path: str):
    return f"""
    <h1> I am an upstream server!</h1>
    <br>
    <h3> You have requested pathadwawdawdw: {repr(u_path)} </h3>
    """

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