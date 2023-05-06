from flask import Flask, send_from_directory

from manageablereverseproxy import REPO_DIR


app = Flask(__name__)

@app.route("/*")
def index(path: str):
    return "dupa" + path


@app.route("/favicon.ico")
def dummy():
    return send_from_directory(str(REPO_DIR), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    app.run(port="8001")