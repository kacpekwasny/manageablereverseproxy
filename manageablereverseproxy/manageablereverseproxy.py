from time import perf_counter

import requests

from flask import Flask, request, Response


class ManageableReverseProxy(Flask):
    """
    """
    SITE_NAME = "http://localhost:5000"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, import_name=__name__)


mrp = ManageableReverseProxy()


@mrp.route('/', defaults={'path': ''},  methods=["GET", "POST"])
@mrp.route("/<path:path>",  methods=["GET", "POST"])
def proxy(path):

    SITE_NAME = "http://localhost:8080/"

    print(request.values)
    r = requests.request(request.method, f"{SITE_NAME}{path}", params=request.values, stream=True, headers=request.headers, allow_redirects=False, data=None)

    excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
    headers = [(name, value) for (name, value) in r.raw.headers.items() if
                       name.lower() not in excluded_headers]

    return Response(r.content, r.status_code, headers)

if __name__ == "__main__":
    mrp.run(debug=True, port=8000)
