import requests
from flask import Flask, request, redirect, Response
from flask.scaffold import setupmethod
from flask_sqlalchemy import SQLAlchemy
from time import perf_counter

db = SQLAlchemy()

app = Flask(__name__, )

# Load config from file config.py
app.config.from_pyfile('config.py')

app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql://{app.config['DB_USER']}:{app.config['DB_PASSWORD']}"
                                         f"@{app.config['DB_HOST']}/{app.config['DB_NAME']}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Create test user and 50 blog entries if do not exist
@setupmethod
def create_user():
    db.create_all()
    db.session.commit()

    return app


@app.route('/', defaults={'path': ''})
@app.route("/<path:path>", methods=["GET", "POST", "DELETE"])
def proxy(path):
    start = perf_counter()
    try:
        global SITE_NAME
        if request.method == "GET":
            resp = requests.get(f"{SITE_NAME}{path}", headers=request.headers, cookies=request.cookies,
                                allow_redirects=False)
            excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
            headers = [(name, value) for (name, value) in resp.raw.headers.items() if
                       name.lower() not in excluded_headers]
            response = Response(resp.content, resp.status_code, headers)
            return response

        elif request.method == "POST":
            print(request.headers)
            content_type = request.headers["Content-Type"]
            resp = None
            if content_type == "application/x-www-form-urlencoded":
                # all data is in the url
                resp = requests.post(f"{SITE_NAME}{path}", headers=request.headers, cookies=request.cookies,
                                     allow_redirects=False)

            elif content_type == "application/json":
                resp = requests.post(f"{SITE_NAME}{path}", headers=request.headers, cookies=request.cookies,
                                     json=request.get_json(), allow_redirects=False)

            excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
            headers = [(name, value) for (name, value) in resp.raw.headers.items() if
                       name.lower() not in excluded_headers]
            response = Response(resp.content, resp.status_code, headers)
            return response

        elif request.method == "DELETE":
            resp = requests.delete(f"{SITE_NAME}{path}", allow_redirects=False)
            excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
            headers = [(name, value) for (name, value) in resp.raw.headers.items() if
                       name.lower() not in excluded_headers]
            response = Response(resp.content, resp.status_code, headers)
            return response
    except Exception as e:
        print(e)
        return "awd"
    finally:
        print(f"{perf_counter()-start=}")


if __name__ == "__main__":
    app.run(debug=True, port=8000)
