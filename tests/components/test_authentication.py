import unittest

from flask import Request as flRequest


from manageablereverseproxy.app import app, db, add_commit
from manageablereverseproxy.wrapperclass import Request, Response
from manageablereverseproxy.components.authentication.authentication import Authentication, HeadersPrivate, HeadersPublic
from manageablereverseproxy.components.authentication.models import UserDB, random_string_generator


class TestAuthentication(unittest.TestCase):
    auth: Authentication

    def setUp(self) -> None:
        self.auth = Authentication()

        with app.app_context():
            db.drop_all()
            db.create_all()
            db.session.commit()

    def make_user(self) -> tuple[str, str]:
        u = UserDB(username=random_string_generator(3)(),
                   passhash=random_string_generator(3)())
        add_commit(u)
        return u.user_id, u.token

    def make_request_from_user(self, user_id: str, token: str) -> Request:
        r = flRequest(environ={
            "HTTP_"+HeadersPublic.USER_ID.value: user_id,
            "HTTP_"+HeadersPublic.USER_TOKEN.value: token,
        })
        return Request(r)

    def test_authentication(self):
        """
        Good credentials -> request authenticated
        Bad credentials -> request unauthenticated
        """
        for _ in range(5):

            user_id1, token1 = self.make_user()
            r1 = self.make_request_from_user(user_id1, token1)

            user_id2, token2 = self.make_user()
            r2 = self.make_request_from_user(user_id2, token2+"dupen2")


            for _ in range(5):  
                r1 = self.auth.process_request(r1)
                self.assertIsInstance(r1.user, UserDB)

                r2 = self.auth.process_request(r2)
                self.assertEqual(r2.user, None)


with app.app_context():
    unittest.main()


