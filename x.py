from time import perf_counter
from flask import Flask, request, redirect, Response
import requests

app = Flask(__name__)
SITE_NAME = "http://127.0.0.1:8080/"


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
