from __future__ import annotations
import logging

from flask import Response as flResponse
from time import time


from ..component_base import ComponentBase, Response, Request
from ..shared_state import SharedStateBase


class FirewallIP(ComponentBase):
    """
    Restrict the inbound requests from IP adresses.
    """

    def __init__(self) -> None:
        self.st: SharedState = SharedState()
        """Multiprocessing requires the use of `multiprocessing.Manger` and shared variables."""

        self.lgr: logging.Logger = logging.getLogger()


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

    def firewall_disabled(self) -> bool:
        return self.time_window == 0
    
    def firewall_whitelist_only(self) -> bool:
        return self.max_requests_in_time_window == 0
    
    def ip_is_whitelisted(self, ip: str) -> bool:
        return ip in self.white_list

    def add_ip_to_whitelist(self, ip: str) -> None:
        if self.ip_is_whitelisted(ip):
            self.lgr.debug("IP %s was allready whitelisted", ip)
        self.white_list.add(ip)

    def process_request(self, req: Request) -> Response | Request:
        if self.firewall_disabled():
            return req

        # using "." in python is expensive :')
        ip = req.ip_address

        if self.ip_is_whitelisted(ip):
            return req
        
        if self.firewall_whitelist_only():
            return Response(flResponse("Only whitelisted IP address are let through.", status=401))
        
        self.register_incoming_request(ip)
        
        if self.ip_is_blocked(ip):
            return Response(flResponse("To many requests, you are currently banned.", status=401))
        
        return req
    
    def register_incoming_request(self, ip: str) -> None:
        """
        Update cache with information on the traffic from this IP address.
        """
        curr_time = time()

        if ip in self.registered_traffic:
            # register new traffic record
            ip_traffic = self.registered_traffic[ip]
            ip_traffic.append(curr_time)

            # find old traffic recorods
            idx = -1
            for i, t in enumerate(ip_traffic):
                if curr_time - t > self.time_window:
                    idx = i
                    break

            # discard old traffic records
            if idx > -1:
                ip_traffic = ip_traffic[idx+1:]
                self.registered_traffic[ip] = ip_traffic
            return
        
        # ip not in registered_traffic
        self.registered_traffic[ip] = [curr_time]

    def ip_is_blocked(self, ip: str) -> bool:
        """
        IP address had made too many requests during time window.
        """       
        # count requests in time window
        count = len(self.registered_traffic[ip])
        return count > self.max_requests_in_time_window


class SharedState(SharedStateBase):

    def __init__(self) -> None:
        super().__init__()

        self._request_count_lock = self._m.Lock()
        self._request_count: dict[str, int] = self._m.dict()
        "Maps number of requests to an IP address."

        self._count_clean_delay_lock = self._m.Lock()
        self._count_clean_delay: float = self._m.Value(typecode=float, value=10.0)
        "Time between reductions of count in `_request_count`."

        self._max_requests_count_lock = self._m.Lock()
        self._max_requests_count: int = self._m.Value(typecode=int, value=200)
        "If a request would be the 201 counted request, the request will be blocked (and counted)."

        self._white_list_lock = self._m.Lock()
        self._white_list: list[str] = self._m.list()
        "Set of IP addresses that are allowed to spam how much they want (like an admin)."

        self._black_list_lock = self._m.Lock()
        self._black_list: list[str] = self._m.list()
        "Set of IP addresses that are banned from all communication."

    def request_count_add(self, addr: str) -> bool:
        """
        return `bool` - addr allowed for further communications.
        """
        self._request_count_lock.acquire()
        try:
            count = self._request_count.get(addr, None)
            if count is None:
                count = 0
            else:
                count += 1
            self._request_count[addr] = count
            return count < self._max_requests_count
        
        finally:
            self._request_count_lock.release()
                    
    def white_black_list(self, addr: str) -> bool | None:
        """
        return bool - True (white), False (black), None (neither)
        """
        # Check whitelist
        self._white_list_lock.acquire()
        try:
            if addr in self._white_list:
                return True
        finally:
            self._white_list_lock.release()

        # Check blacklist
        self._black_list_lock.acquire()
        try:
            if addr in self._black_list:
                return False
        finally:
            self._black_list_lock.release()
        
        return None
        

