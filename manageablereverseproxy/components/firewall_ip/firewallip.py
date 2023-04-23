from __future__ import annotations

from flask import Response as flResponse
from sqlalchemy import inspect

from ..component_base import ComponentBase, Response, Request
from ...logger import InheritLogger

from .models import ClientIPAddressDB
from .client_ip_addr import ClientIPAddress
from ...app import app, db, add_commit


class FirewallIP(ComponentBase, InheritLogger):
    """
    Restrict the inbound requests from IP adresses.
    """

    def __init__(self) -> None:
        self.disabled: bool = False
        """All traffic is passed directly through."""
        
        self.client_cache: dict[str, ClientIPAddress] = {}
        "Cache of `ClientIPAddr`"

        self.time_window: float = 60
        "Time window in which requests for an IP address cannot reach over specific number."

        self.max_requests_in_time_window: int = 200
        "If a request would be the 201 request during time_window, the request will be blocked (and registered)."


    def set_time_window(self, seconds: float) -> FirewallIP:
        # time window smaller than .1 doesnt realy make sens
        self.time_window = seconds if seconds > .1 else 0
        if self.time_window == 0:
            self.lgr.warning("FirewallIP is DISABLED! The time window was set to %.2f[sec], so it was converted to zero, and thus the `FirewallIP` became disabled!", seconds)
        return self

    def set_max_requests_in_time_window(self, req_num: int) -> FirewallIP:
        self.max_requests_in_time_window = int(max(0, req_num))
        if self.max_requests_in_time_window == 0:
            self.lgr.warning("FirewallIP allows only whitelisted IP addresses! This is because `req_num` was set to zero.")
        return self

    def disable(self, disabled: bool) -> None:
        self.disabled = disabled

    def firewall_disabled(self) -> bool:
        return self.disabled
    
    def firewall_whitelist_only(self) -> bool:
        return self.max_requests_in_time_window < 1
    
    def firewall_all_except_blacklist(self) -> bool:
        return self.time_window == 0


    def ip_is_whitelisted(self, ip: str) -> bool:
        return ClientIPAddress(ip).whitelisted

    def whitelist_clientipaddr(self, ip: str, whitelist: bool) -> None:
        client = ClientIPAddress(ip)
        if client.c.whitelisted == whitelist:
            return
        client.c.whitelisted = whitelist
        add_commit(client.c)
        
    def ip_is_blacklisted(self, ip: str) -> bool:
        return ClientIPAddress(ip).blacklisted
    
    def blacklist_clientipaddr(self, ip: str, blacklist: bool) -> None:
        client = ClientIPAddress(ip)
        if client.c.blacklisted == blacklist:
            return
        client.c.blacklisted = blacklist
        add_commit(client.c)
        return

    def process_request(self, req: Request) -> Response | Request:
        with app.app_context():
            if self.firewall_disabled():
                return req

            client = ClientIPAddress(req.ip_address)

            if client.c.whitelisted:
                return req
            
            if self.firewall_whitelist_only():
                return Response(flResponse("Only whitelisted IP address are let through.", status=401))
        
            if client.c.blacklisted:
                return Response(flResponse("You are banned.", status=401))

            if self.firewall_all_except_blacklist():
                return req

            client.register_incoming_request(self.time_window)
            
            if client.too_many_requests(self.max_requests_in_time_window):
                return Response(flResponse("To many requests, you are currently banned.", status=401))
            
            return req
        

