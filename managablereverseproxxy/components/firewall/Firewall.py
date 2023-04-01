from flask import Response as flResponse
from time import time

from ..component import ComponentBase, Response, Request


class FirewallIP(ComponentBase):
    """
    Restrict the inbound requests from IP adresses.
    """

    def __init__(self) -> None:
        self.registered_traffic: dict[str, list[float]] = {}
        "Stores timestamps of incomping requests for ip address"

        self.time_window: float = 60
        "Time window in which requests for an IP address cannot reach over specific number."

        self.max_requests_in_time_window: int = 200
        "If a request would be the 201 request during time_window, the request will be blocked (and registered)."

        self.white_list: set[str] = set()
        "Set of IP addresses that are allowed to spam how much they want (like an admin)."


    def process_request(self, r: Request) -> Response | Request:
        # using "." in python is expensive :')
        ip = r.ip_address

        if ip in self.white_list:
            return r

        self.register_incoming_request(ip)
        if self.ip_is_blocked(ip):
            return Response(flResponse("To many requests, you are currently banned.", status=401))
        return r
    
    def register_incoming_request(self, ip: str) -> None:
        """
        
        """
        if ip in self.registered_traffic:
            # register new traffic record
            ip_traffic = self.registered_traffic[ip]
            curr_time = time()
            ip_traffic.append(curr_time)

            # find old traffic recorods
            for i, t in enumerate(ip_traffic):
                if curr_time - t < self.time_window:
                    break

            # discard old traffic records
            if i > 0:
                ip_traffic = ip_traffic[i-1:]
                self.registered_traffic[ip] = ip_traffic
            


    def ip_is_blocked(self, ip: str) -> bool:
        """
        If the requests are
        """       
        # count requests in time window
        return len(self.registered_traffic[ip]) > self.max_requests_in_time_window

