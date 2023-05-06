from flask import Blueprint, render_template, request

from .firewallip import FirewallIP
from .client_ip_addr import ClientIPAddress
from ...wrapperclass import Request, Response


FIREWALL_IP_CONTROLLER = Blueprint("firewall_ip_controller", __name__, url_prefix='/firewall-ip-controller')

FIREWALL_IP = FirewallIP().set_time_window(5).set_max_requests_in_time_window(4)
FIREWALL_IP.set_lgr_level(-1)


@FIREWALL_IP_CONTROLLER.route("/", methods=["GET"])
def index():
    clients = [client.c for client in ClientIPAddress._client_cache.values()]
    return render_template("firewall_ip_controller.html", ip_clients=clients)

@FIREWALL_IP_CONTROLLER.route("/whitelist/<add>/<ip_addr>", methods=["POST"])
def whitelist(add: str, ip_addr: str):

    add_to_whitelist = {
        "True": True,
        "False": False,
    }.get(add, None)

    if add_to_whitelist is None:
        return 400, "`add` may be 'True' or 'False' string only."
    
    FIREWALL_IP.whitelist_clientipaddr(ip_addr, add_to_whitelist)
    return "ok", 200











