from time import time

from ...logger import InheritLogger
from .models import ClientIPAddressDB

class ClientIPAddress(InheritLogger):

    def __init__(self, c: ClientIPAddressDB) -> None:
        if not isinstance(c, ClientIPAddressDB):
            raise TypeError(f"{type(c)=}, but should be of type {ClientIPAddressDB}")
        self.c = c
        self.registered_traffic: list[float] = []

    def register_incoming_request(self, time_window: float) -> None:
        """
        Update cache with information on the traffic from this IP address.
        """
        curr_time = time()

        # register new traffic record
        self.registered_traffic.append(curr_time)

        # find old traffic recorods
        idx = -1
        for i, t in enumerate(self.registered_traffic):
            if curr_time - t > time_window:
                idx = i
                break

        # discard old traffic records
        if idx > -1:
            self.registered_traffic = self.registered_traffic[idx + 1:]

        self.lgr.debug(f"{self.registered_traffic}")

    def too_many_requests(self, max_requests_in_time_window: int) -> bool:
        """
        IP address had made too many requests during time window.
        """       
        # count requests in time window
        count = len(self.registered_traffic)
        return count > max_requests_in_time_window
