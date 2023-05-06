import unittest

from flask import Request as flRequest
from time import sleep


from manageablereverseproxy.app import app, db
from manageablereverseproxy.wrapperclass import Request, Response
from manageablereverseproxy.components.firewall_ip.controller import FIREWALL_IP, FirewallIP
from manageablereverseproxy.components.firewall_ip.client_ip_addr import ClientIPAddress




class TestFirewallIP(unittest.TestCase):
    fw: FirewallIP

    def setUp(self) -> None:
        ClientIPAddress._dump_client_cache()
        self.fw = FirewallIP()
        # self.fw.set(20)
        self.r1 = Request(flRequest({}))
        self.r1.ip_address = "ip1"
        
        self.r2 = Request(flRequest({}))
        self.r2.ip_address = "ip2"

        self.fw.set_lgr_level(20)

        with app.app_context():
            db.drop_all()
            db.create_all()
            db.session.commit()


    def test_block_too_many_requests_time_window(self):
        self.fw.set_time_window(1).set_max_requests_in_time_window(5)
        self.fw.set_lgr_level(0)

        for i in range(6):
            rr = self.fw.process_request(self.r1)
            if isinstance(rr, Response):
                self.assertEqual(i, 5)
                return
        
        self.fail("The Firewall should have blocked the request on the sixth `process_request`, but didn't.")

    def test_no_block_when_not_too_often(self):
        self.fw.set_time_window(1).set_max_requests_in_time_window(5)
        for _ in range(10):
            # test on request coming from two ip addresses 
            for req in [self.r1, self.r2]:
                rr = self.fw.process_request(req)
                if isinstance(rr, Response):
                    self.fail("Requests are sent rarely enough, that they should not have been blocked.")

            sleep(.2) # 5 * 0.2 + latency > 1 second so no blocks should occur

    def test_whitelist_only(self):
        self.fw.set_max_requests_in_time_window(0)
        self.fw.whitelist_clientipaddr(self.r1.ip_address, True)

        self.assertIsInstance(self.fw.process_request(self.r1), Request)
        self.assertIsInstance(self.fw.process_request(self.r2), Response)

    def test_whitelist_is_allowed_to_spam(self):
        self.fw.set_max_requests_in_time_window(10).set_time_window(1)
        self.fw.whitelist_clientipaddr(self.r1.ip_address, True)

        for _ in range(1000):
            self.assertIsInstance(self.fw.process_request(self.r1), Request)
            r = self.fw.process_request(self.r2)
        self.assertIsInstance(r, Response)

    def test_firewall_disabled(self):
        self.fw.disable(True)
        for _ in range(1000):
            self.assertIsInstance(self.fw.process_request(self.r1), Request)
            self.assertIsInstance(self.fw.process_request(self.r2), Request)

    def test_firewall_all_except_blacklist(self):
        self.fw.set_time_window(0)
        self.assertTrue(self.fw.firewall_all_except_blacklist())
        for _ in range(1000):
            self.assertIsInstance(self.fw.process_request(self.r1), Request)
            self.assertIsInstance(self.fw.process_request(self.r2), Request)
            



unittest.main()