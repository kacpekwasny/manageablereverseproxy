from pathlib import Path
from flask import Flask, Blueprint, jsonify, render_template, request, send_from_directory, make_response

from .models import db, ClientIPAddress
from .firewallip import FirewallIP, FirewallIPConfig
from ..authentication import require_auth
from ... import REPO_DIR
from ...wrapperclass import MyResponse

CONFIG_FILE = str(Path(__file__).parent / "config.json")



def app_add_firewall_ip_module(app: Flask,
                               url_prefix: str="/firewallip",
                               config_path: str=CONFIG_FILE):

    firewallip_bp = Blueprint("firewall_ip_controller", __name__, url_prefix=url_prefix)

    config = FirewallIPConfig(config_path)
    firewallip = FirewallIP(config)
    firewallip.set_lgr_level(-1)

    @firewallip_bp.before_request
    @require_auth
    def require_user_auth():
        return


    @firewallip_bp.before_app_request
    def firewall():
        r = firewallip.process_request(request)
        if isinstance(r, MyResponse):
            return r

    @firewallip_bp.route("/", methods=["GET"])
    def index():
        return render_template("firewall_ip/index.html")


    @firewallip_bp.route("/clients.json", methods=["GET"])
    def get_clients():
        return jsonify({ client.ip_address: client.to_dict() for client in ClientIPAddress.query.all() })

    @firewallip_bp.route("/config.json", methods=["GET"])
    def get_config():
        return config._to_dict()

    @firewallip_bp.route("/config.json", methods=["POST"])
    def set_config():
        json = request.json

        firewallip.set_time_window(json["time_window"])
        firewallip.set_max_requests_in_time_window(json["max_requests_in_time_window"])
        firewallip.disable(json["disabled"])
        config._save()

        return get_config()

    @firewallip_bp.route("/ipaddr/<ip_addr>", methods=["GET"])
    def get_ipaddr(ip_addr: str):
        cip = ClientIPAddress.query.filter_by(ip_address=ip_addr).first()
        if cip is None:
            return jsonify({"ok": False, "msg": "IP address not in database."}), 404

        return jsonify(cip.to_dict() | {"ok": True}), 200

    @firewallip_bp.route("/ipaddr/<ip_addr>", methods=["POST"])
    def post_ipaddr(ip_addr: str):
        cip = ClientIPAddress.query.filter_by(ip_address=ip_addr).first()
        if cip is None:
            return jsonify({"ok": False, "msg": "IP address not in database."}), 404

        print(1)
        json = request.json
        if "whitelisted" in json:
            cip.whitelisted = json["whitelisted"]
        if "blacklisted" in json:
            cip.blacklisted = json["blacklisted"]
        print(2)
        
        db.session.commit()

        return jsonify(cip.to_dict() | {"ok": True}), 200


    app.register_blueprint(firewallip_bp)








