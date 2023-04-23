from time import perf_counter

import requests
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, Response


class ManageableReverseProxy(Flask):
    """
    """
    db = SQLAlchemy()
    lol = "test"

    def after_init(self):
        with self.app_context():
            print("dupa")
            self.db.create_all()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, import_name=__name__)
        self.config.from_pyfile('config.py')
        self.debug = True
        self.app_context()
        self.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql://{self.config['DB_USER']}:{self.config['DB_PASSWORD']}"
                                                  f"@{self.config['DB_HOST']}/{self.config['DB_NAME']}")
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.db.init_app(self)



mrp = ManageableReverseProxy()

from .models import Firewall

mrp.after_init()
SITE_NAME = "http://localhost:8080/"


@mrp.route('/', defaults={'path': ''})
@mrp.route("/<path:path>", methods=["GET", "POST", "DELETE"])
def proxy(path):
    start = perf_counter()

    if mrp.db.session.execute(mrp.db.select(Firewall).filter_by(ip_address=request.remote_addr)).scalar() is not None:
        return Response("Access Denied", 401)

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
    mrp.run(debug=True, port=8000)
