import requests


from pathlib import Path
from flask import jsonify, render_template, request, Blueprint, Flask

from ..authentication import require_auth
from ..config import ConfigBase


CONFIG_PATH = str(Path(__file__).parent / "config.json")


class ReverseProxyConfig(ConfigBase):
    site_name: str = ""
    host_name: str = ""
    schema:    str = ""

    def _set_site_name(self, site_name: str):
        if site_name[:4] != "http":
            raise ValueError("`site_name` has to start with either 'http://' or 'https://'.")
        self.site_name = site_name.strip("/")
        self.schema, self.host_name = self.site_name.split("://")


def app_add_reverseproxy_module(app: Flask,
                                config_path: str=CONFIG_PATH):
    config = ReverseProxyConfig(config_path)

    reverse_proxy = Blueprint("reverseproxy", __name__)

    ALL_HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']


    @reverse_proxy.route('/', defaults={'path': ''}, methods=ALL_HTTP_METHODS)
    @reverse_proxy.route("/<path:path>", methods=ALL_HTTP_METHODS)
    def proxy(path):

        url = f"{config.site_name}/{path}"
        request.headers.set("Host", config.host_name)
        request.headers.set("Authority", config.host_name)
        request.headers.set("Schema", config.schema)

        # excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        # headers = {name: value for (name, value) in request.headers if
        #                    name.lower() not in excluded_headers}

        r = requests.request(request.method,
                            url,
                            params=request.values,
                            stream=False,
                            headers=request.headers,
                            allow_redirects=False,
                            data=request.data)

        return r.content, r.status_code, r.headers.items()

    @reverse_proxy.route('/reverseproxy/config', methods=["GET"])
    @require_auth
    def config_page_get():
        return render_template("reverseproxy/config.html", username=(request.user and request.user.username))

    @reverse_proxy.route('/reverseproxy/config.json', methods=["GET"])
    @require_auth
    def config_get():
        return jsonify(config._to_dict())

    @reverse_proxy.route('/reverseproxy/config.json', methods=["POST"])
    @require_auth
    def config_post():
        try:
            config._set_site_name(request.json["site_name"])
            config._save()
            print("saved")
        except ValueError:
            return jsonify(ok=False, msg="site_name has to start with 'http://' or 'https://'")
        except KeyError:
            return jsonify(ok=False, msg="'site_name' key missing from JSON")

        return jsonify(ok=True, site_name=config.site_name)


    app.register_blueprint(reverse_proxy)



