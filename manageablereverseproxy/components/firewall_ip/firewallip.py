from __future__ import annotations
from time import time

from flask import jsonify, make_response

from ..component_base import ComponentBase
from ..config import ConfigBase
from ...wrapperclass import MyResponse, MyRequest
from ...logger import InheritLogger

from .models import ClientIPAddress, db


class FirewallIPConfig(ConfigBase):
    disabled: bool = False
    """All traffic is passed directly through."""
    
    time_window: float = 3
    "Time window in which requests for an IP address cannot reach over specific number."

    max_requests_in_time_window: int = 20
    "If a request would be the 201 request during time_window, the request will be blocked (and registered)."




class FirewallIP(ComponentBase, InheritLogger):
    """
    Restrict the inbound requests from IP adresses.
    """

    def __init__(self, config: FirewallIPConfig) -> None:
        self.config = config

        self.registered_traffic: dict[str, list[float]] = {}
        "dict of all traffic timestamps"

    def set_time_window(self, seconds: float) -> FirewallIP:
        # time window smaller than .1 doesnt realy make sens
        self.config.time_window = seconds if seconds > .1 else 0
        if self.config.time_window == 0:
            self.lgr.warning("FirewallIP is DISABLED! The time window was set to %.2f[sec], so it was converted to zero, and thus the `FirewallIP` became disabled!", seconds)
        return self

    def set_max_requests_in_time_window(self, req_num: int) -> FirewallIP:
        self.config.max_requests_in_time_window = int(max(0, req_num))
        if self.config.max_requests_in_time_window == 0:
            self.lgr.warning("FirewallIP allows only whitelisted IP addresses! This is because `req_num` was set to zero.")
        return self

    def disable(self, disabled: bool) -> None:
        self.config.disabled = disabled

    def firewall_disabled(self) -> bool:
        return self.config.disabled
    
    def firewall_whitelist_only(self) -> bool:
        return self.config.max_requests_in_time_window < 1
    
    def firewall_all_except_blacklist(self) -> bool:
        return self.config.time_window == 0

    def process_request(self, req: MyRequest) -> MyResponse | MyRequest:
        if self.firewall_disabled():
            return req
        
        ip_addr = req.ip_address

        client = ClientIPAddress.query.filter_by(ip_address=ip_addr).first()
        if client is None:
            client = ClientIPAddress(ip_address=ip_addr)
            db.session.add(client)
            db.session.commit()

        if client.whitelisted:
            return req
        
        if self.firewall_whitelist_only():
            return make_response(jsonify(msg="Only whitelisted IP address are let through."), 401)
    
        if client.blacklisted:
            return make_response(jsonify(msg="You are banned."), 401)

        if self.firewall_all_except_blacklist():
            return req

        client_traffic = self.register_incoming_request(ip_addr)
        
        if self.too_many_requests(client_traffic):
            return make_response(jsonify(msg="To many requests, you are currently banned."), 401)
        
        return req

    def register_incoming_request(self, ip: str) -> list[float]:
        """
        Update cache with information on the traffic from this IP address.

        return
            list[float] - traffic timestamps of this ip address
        """
        curr_time = time()

        # register new traffic record
        if not ip in self.registered_traffic:
            self.registered_traffic[ip] = []
        traffic = self.registered_traffic[ip]

        traffic.append(curr_time)

        self.lgr.debug(f"{ip}: {len(traffic)=} {traffic[-1]-traffic[0]=}")

        # find old traffic recorods
        idx = -1
        for i, t in enumerate(traffic):
            # no requests are older than time_window
            if curr_time - t < self.config.time_window:
                idx = i
                break

        # discard old traffic records
        if idx > -1:
            traffic = traffic[idx:]
        
        self.registered_traffic[ip] = traffic

        self.lgr.debug(f"{ip}: {len(traffic)=} {traffic[-1]-traffic[0]=}")
        return traffic

    def too_many_requests(self, traffic: list[float]) -> bool:
        """
        IP address had made too many requests during time window.
        """
        # count requests in time window
        count = len(traffic)
        self.lgr.debug(f"{count=}, {self.config.max_requests_in_time_window=}")
        return count > self.config.max_requests_in_time_window
