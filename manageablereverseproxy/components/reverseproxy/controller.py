import requests

from flask import request, Blueprint, Flask



def app_add_reverseproxy_module(app: Flask, site_name: str):
    if site_name[:4] != "http":
        raise ValueError("`site_name` has to start with either 'http://' or 'https://'.")

    reverse_proxy = Blueprint("reverseproxy", __name__)

    ALL_HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']


    @reverse_proxy.route('/', defaults={'path': ''}, methods=ALL_HTTP_METHODS)
    @reverse_proxy.route("/<path:path>", methods=ALL_HTTP_METHODS)
    def proxy(path):

        r = requests.request(request.method,
                            f"{site_name}{path}",
                            params=request.values,
                            stream=False,
                            headers=request.headers,
                            allow_redirects=False,
                            data=request.data)

        # excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        # headers = [(name, value) for (name, value) in r.raw.headers.items() if
        #                    name.lower() not in excluded_headers]


        return r.content, r.status_code, r.headers.items()

    app.register_blueprint(reverse_proxy)



