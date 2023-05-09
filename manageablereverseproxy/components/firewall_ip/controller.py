from pathlib import Path
from flask import Flask, Blueprint, jsonify, request, send_from_directory, make_response

from .models import db, ClientIPAddress
from .firewallip import FirewallIP
from ..authentication import require_auth
from ... import REPO_DIR
from ...wrapperclass import MyResponse

FRONTEND_DIR = str(Path(__file__).parent / "frontend")


def app_add_firewall_ip_module(app: Flask, url_prefix: str="/firewallip"):

    firewallip_bp = Blueprint("firewall_ip_controller", __name__, url_prefix=url_prefix)

    firewallip = FirewallIP().set_time_window(5).set_max_requests_in_time_window(4)
    firewallip.set_lgr_level(-1)

    @firewallip_bp.before_request
    def require_user_auth():
        print(f"firewallip {request.user}")
        if request.user is None:
            return make_response(jsonify({"msg": "you need to be logged in for this endpoint"}), 401)


    @firewallip_bp.before_app_request
    def firewall():
        r = firewallip.process_request(request)
        if isinstance(r, MyResponse):
            return r

    @firewallip_bp.route('/', defaults={'path': ''})
    @firewallip_bp.route("/<path:path>", methods=["GET"])
    def index(path):
        print(request.user)
        if path == "":
            return send_from_directory(FRONTEND_DIR, "index.html")
        return send_from_directory(FRONTEND_DIR, path)


    @firewallip_bp.route("/clients.json", methods=["GET"])
    def get_clients():
        return [ client.to_dict() for client in ClientIPAddress.query.all() ]

    @firewallip_bp.route("/config.json", methods=["GET"])
    def get_config():
        return {
            "time_window": firewallip.time_window,
            "max_requests": firewallip.max_requests_in_time_window,
            "disabled": firewallip.disabled,
        }

    @firewallip_bp.route("/config.json", methods=["POST"])
    def set_config():
        json = request.json

        firewallip.set_time_window(json["time_window"])
        firewallip.set_max_requests_in_time_window(json["max_requests"])
        firewallip.disable(json["disabled"])

        return get_config()

    @firewallip_bp.route("/ipaddr/<ip_addr>", methods=["GET"])
    def get_ipaddr(ip_addr: str):
        cip = ClientIPAddress.query.filter_by(ip_address=ip_addr).first()
        if cip is None:
            return jsonify({"ok": False, "msg": "IP address not in database."}), 404

        return jsonify(cip.to_dict() | {"ok": True}), 200

    @firewallip_bp.route("/ipaddr/<ip_addr>", methods=["POST"])
    @require_auth
    def post_ipaddr(ip_addr: str):
        cip = ClientIPAddress.query.filter_by(ip_address=ip_addr).first()
        if cip is None:
            return jsonify({"ok": False, "msg": "IP address not in database."}), 404

        json = request.json
        if "whitelisted" in json:
            cip.whitelisted = json["whitelisted"]
        if "blacklisted" in json:
            cip.blacklisted = json["blacklisted"]
        
        db.session.commit()

        return jsonify(cip.to_dict() | {"ok": True}), 200


    app.register_blueprint(firewallip_bp)








