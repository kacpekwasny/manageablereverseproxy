from pathlib import Path
from flask import Blueprint, render_template, request, send_file, send_from_directory

from .firewallip import FirewallIP
from .client_ip_addr import ClientIPAddress

FRONTEND_DIR = str(Path(__file__).parent / "frontend")

FIREWALL_IP_CONTROLLER = Blueprint("firewall_ip_controller", __name__, url_prefix='/firewall-ip-controller')

FIREWALL_IP = FirewallIP().set_time_window(5).set_max_requests_in_time_window(4)
FIREWALL_IP.set_lgr_level(-1)

@FIREWALL_IP_CONTROLLER.route('/', defaults={'path': ''})
@FIREWALL_IP_CONTROLLER.route("/<path:path>", methods=["GET"])
def index(path):
    if path == "":
        return send_from_directory(FRONTEND_DIR, "index.html")
    return send_from_directory(FRONTEND_DIR, path)


@FIREWALL_IP_CONTROLLER.route("/clients.json", methods=["GET"])
def get_clients():
    return [ client.to_dict() for client in ClientIPAddress._client_cache.values() ]

@FIREWALL_IP_CONTROLLER.route("/config.json", methods=["GET"])
def get_config():
    return {
        "time_window": FIREWALL_IP.time_window,
        "max_requests": FIREWALL_IP.max_requests_in_time_window,
        "disabled": FIREWALL_IP.disabled,
    }

@FIREWALL_IP_CONTROLLER.route("/config.json", methods=["POST"])
def set_config():
    json = request.json

    FIREWALL_IP.set_time_window(json["time_window"])
    FIREWALL_IP.set_max_requests_in_time_window(json["max_requests"])
    FIREWALL_IP.disable(json["disabled"])

    return get_config()


@FIREWALL_IP_CONTROLLER.route("/whitelist/<add>/<ip_addr>", methods=["POST"])
def whitelist(add: str, ip_addr: str):

    add_to_whitelist = {
        "true": True,
        "false": False,
    }.get(add.lower(), None)

    if add_to_whitelist is None:
        return "`add` may be 'True' or 'False' string only.", 400
    
    FIREWALL_IP.whitelist_clientipaddr(ip_addr, add_to_whitelist)
    return get_clients(), 200

@FIREWALL_IP_CONTROLLER.route("/blacklist/<add>/<ip_addr>", methods=["POST"])
def blacklist(add: str, ip_addr: str):

    add_to_blacklist = {
        "true": True,
        "false": False,
    }.get(add.lower(), None)

    if add_to_blacklist is None:
        return "`add` may be 'True' or 'False' string only.", 400
    
    FIREWALL_IP.blacklist_clientipaddr(ip_addr, add_to_blacklist)
    return get_clients(), 200










