import unittest

from manageablereverseproxy.wrapperclass import Request, Response
from flask import Request as fRequest


class TestWrapperClass(unittest.TestCase):

    def test_inheritance_works(self) -> None:
        fr = fRequest({})
        IP = "192.168.1.2"
        fr.remote_addr = IP
        r = Request(fr)
        self.assertEqual(fr.remote_addr, IP, "Magic inheritance doesn't really work :(")
        self.assertEqual(r.remote_addr, IP, "Magic inheritance doesn't really work :(")


unittest.main()


