from flask import Flask, send_from_directory

from manageablereverseproxy import REPO_DIR


app = Flask(__name__)

@app.route('/', defaults={'u_path': ''})
@app.route("/<path:u_path>", methods=["GET"])
def index(u_path: str):
    return "<h1> dupa, powtarzam! uwaga, dupa! " + u_path + "</h1>"


@app.route("/favicon.ico")
def dummy():
    return send_from_directory(str(REPO_DIR / "assets"), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    app.run(port=8001)