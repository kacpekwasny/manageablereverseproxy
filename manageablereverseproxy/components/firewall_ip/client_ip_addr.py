from __future__ import annotations

from time import time
from sqlalchemy import inspect


from ...app import app
from ...logger import InheritLogger
from .models import ClientIPAddressDB

class ClientIPAddress(InheritLogger):

    _client_cache: dict[str, ClientIPAddress] = {}


    def __new__(cls, ip: str, *args, **kwargs) -> ClientIPAddress:
        client = cls._client_cache.get(ip, None)
        
        if client is None \
        or inspect(client.c).detached:
            # client not in cache
            # or client session timeout
            
            with app.app_context():
                clientdb: ClientIPAddressDB = ClientIPAddressDB.query.filter_by(ip_address=ip).first()
                if clientdb is None:
                    # client not in db
                    clientdb = ClientIPAddressDB(ip_address=ip)

                client = super().__new__(cls)
                client._init(client_db=clientdb)

            cls._client_cache[ip] = client

        return client

    def _init(self, *, client_db: ClientIPAddressDB) -> None:
        self.c = client_db
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

    @classmethod
    def _dump_client_cache(cls):
        cls._client_cache = {}
