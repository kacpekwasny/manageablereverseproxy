from flask import Blueprint, render_template, request

from .firewallip import FirewallIP
from .client_ip_addr import ClientIPAddress
from ...wrapperclass import Request, Response


FIREWALL_IP_CONTROLLER = Blueprint("firewall_ip_controller", __name__, url_prefix='/firewall-ip-controller')

FIREWALL_IP = FirewallIP().set_time_window(5).set_max_requests_in_time_window(100)
FIREWALL_IP.set_lgr_level(20)


@FIREWALL_IP_CONTROLLER.route("/", methods=["GET"])
def index():
    clients = [client.c for client in ClientIPAddress._client_cache.values()]
    print(clients)
    rr = FIREWALL_IP.process_request(Request(request))
    return render_template("base.html", ip_clients=clients)








