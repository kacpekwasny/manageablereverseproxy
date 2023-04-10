from __future__ import annotations
import logging

from multiprocessing import Process
from flask import Response as flResponse
from time import sleep, time


from ..component_base import ComponentBase, Response, Request
from ..shared_state import SharedStateBase


class FirewallIP(ComponentBase):
    """
    Restrict the inbound requests from IP adresses.
    """

    def __init__(self) -> None:
        self._shared: SharedState = SharedState()
        """Multiprocessing requires the use of `multiprocessing.Manger` and shared variables."""

        self.lgr: logging.Logger = logging.getLogger()


    def firewall_disabled(self) -> bool:
        return self._shared._firewall_disabled.value
    
    def firewall_whitelist_only(self) -> bool:
        return self._shared._whitelist_only.value
    
    def ip_is_whitelisted(self, ip: str) -> bool:
        return ip in self._shared.get_blacklist_copy()

    def add_ip_to_whitelist(self, ip: str) -> None:
        if self.ip_is_whitelisted(ip):
            self.lgr.debug("IP %s was allready whitelisted", ip)
        self.whitelist.add(ip)

    def process_request(self, req: Request) -> Response | Request:
        if self.firewall_disabled():
            return req

        # using "." in python is expensive :')
        ip = req.ip_address

        if self.ip_is_whitelisted(ip):
            return req
        
        if self.firewall_whitelist_only():
            return Response(flResponse("Only whitelisted IP address are let through.", status=401))
        
        if not self.count_and_check_incoming_request(ip):
            return Response(flResponse("To many requests, you are currently banned.", status=401))
        
        return req
    
    def count_and_check_incoming_request(self, ip: str) -> bool:
        """
        Add `1` to request count for this IP address. \n
        return `bool` \n
            True - ip allowed to pass upstream \n
            False - ip not allowed to pass upstream \n
        """
        return self._shared.count_request_check_allowed(ip)



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

        self._whitelist_lock = self._m.Lock()
        self._whitelist: list[str] = self._m.list()
        "Set of IP addresses that are allowed to spam how much they want (like an admin)."

        self._blacklist_lock = self._m.Lock()
        self._blacklist: list[str] = self._m.list()
        "Set of IP addresses that are banned from all communication."

        self._firewall_disabled_lock = self._m.Lock()
        self._firewall_disabled: bool = self._m.Value(bool, False)
        "Firewall allows all traffic, and does not count requests nor forbid anyone."

        self._whitelist_only_lock = self._m.Lock()
        self._whitelist_only: bool = self._m.Value(bool, False)
        "Firewall allows only traffic that originate from whitelisted ip addresses."

        self._count_cleaner: Process = Process(self.run_count_cleaner)

    def run_count_cleaner(self) -> None:
        while True:
            sleep(self._count_clean_delay)
            self._request_count_lock.acquire()
            try:
                for addr, count in self._request_count.items():
                    self._request_count[addr] = max(0, count - self._max_requests_count.value)
            except Exception as e:
                raise e
            finally:
                self._request_count_lock.release()

    def count_request_check_allowed(self, addr: str) -> bool:
        """
        Add `1` to request count for this IP address. \n
        return `bool` \n
            True - ip allowed to pass upstream \n
            False - ip not allowed to pass upstream \n
        """
        self._request_count_lock.acquire()
        try:
            count = self._request_count.get(addr, None)
            if count is None:
                count = 1
            else:
                count += 1
            self._request_count[addr] = count
            return count < self._max_requests_count.value
        
        finally:
            self._request_count_lock.release()
                    
    def addr_in_white_black_list(self, addr: str) -> bool | None:
        """
        return bool - True (white), False (black), None (neither)
        """
        # Check whitelist
        self._whitelist_lock.acquire()
        try:
            if addr in self._whitelist:
                return True
        finally:
            self._whitelist_lock.release()

        # Check blacklist
        self._blacklist_lock.acquire()
        try:
            if addr in self._blacklist:
                return False
        finally:
            self._blacklist_lock.release()
        
        return None

    def get_blacklist_copy(self) -> list[str]:
        """
        """
        self._blacklist_lock.acquire()
        try:
            return self._blacklist[:]
        finally:
            self._blacklist_lock.release()
        
    def get_whitelist_copy(self) -> list[str]:
        """
        """
        self._whitelist_lock.acquire()
        try:
            return self._whitelist[:]
        finally:
            self._whitelist_lock.release()

    def set_count_clean_delay(self, seconds: float) -> SharedState:
        """
        `seconds` has to be greater than `0.1`.
        """
        self._count_clean_delay_lock.acquire()
        try:
            if seconds > 0.1:
                self._count_clean_delay.value = seconds
                return self
            raise ValueError("`seconds` has to be > 0.1.")
        finally:
            self._count_clean_delay_lock.release()

    def set_max_requests_count(self, count: int) -> SharedState:
        """
        `count` has to be greater than `1`.
        """
        self._max_requests_count_lock.acquire()
        try:
            if count > 1:
                self._max_requests_count.value = count
                return self
            raise ValueError("`count` has to be > `1`.")
        finally:
            self._max_requests_count_lock.release()

    def set_firewall_disabled(self, v: bool) -> SharedState:
        """
        """
        self._firewall_disabled_lock.acquire()
        try:
            self._firewall_disabled.value = v
            return self
        finally:
            self._firewall_disabled_lock.release()

    def set_whitelist_only(self, v: bool) -> SharedState:
        """
        """
        self._whitelist_only_lock.acquire()
        try:
            self._whitelist_only.value = v
            return self
        finally:
            self._whitelist_only_lock.release()


    def append_whitelist(self, ips: list[str]) -> SharedState:
        """
        Append an ip address to the white list.
        """
        self._whitelist_lock.acquire()
        try:
            for ip in ips:
                if isinstance(ip, str):
                    self._whitelist.append(ip)
        finally:
            self._whitelist_lock.release()

    def append_blacklist(self, ips: list[str]) -> SharedState:
        """
        Append an ip address to the black list.
        """
        self._blacklist_lock.acquire()
        try:
            for ip in ips:
                if isinstance(ip, str):
                    self._blacklist.append(ip)
        finally:
            self._blacklist_lock.release()

    def remove_whitelist(self, ips: list[str]) -> SharedState:
        """
        remove an ip address from the white list.
        """
        self._whitelist_lock.acquire()
        try:
            for ip in ips:
                if isinstance(ip, str):
                    self._whitelist.remove(ip)
        finally:
            self._whitelist_lock.release()

    def remove_blacklist(self, ips: list[str]) -> SharedState:
        """
        remove an ip address from the black list.
        """
        self._blacklist_lock.acquire()
        try:
            for ip in ips:
                if isinstance(ip, str):
                    self._blacklist.remove(ip)
        finally:
            self._blacklist_lock.release()

