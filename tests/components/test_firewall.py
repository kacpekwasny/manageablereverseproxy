from unittest import TestCase

from manageablereverseproxy import Request, Response, FirewallIP

from flask import Request as flRequest

class TestFirewallIP(TestCase):
    
    def setUp(self) -> None:
        self.fw = FirewallIP()
        self.r = Request(flRequest({}))
        self.r.ip_address = "ip1"

    def test_block_too_many_requests_time_window(self):
        self.fw.set_time_window(1).set_max_requests_in_time_window(5)

        for i in range(6):
            rr = self.fw.process_request(self.r)
            if isinstance(rr, Response):
                self.assertEqual(i, 5)
                return
        self.fail("The Firewall should have blocked the request on the sixth `process_request`, but didn't.")



