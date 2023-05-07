
import datetime
import random
import string

import typing as T


from ...app import db

ALPHANUM = string.ascii_lowercase + string.ascii_uppercase + string.digits
WRITEABLE = ALPHANUM + string.punctuation

def random_string_generator(length: int, choose_from: T.Iterable=ALPHANUM) -> str:
    return lambda: "".join([random.choice(choose_from) for _ in range(length)])


class UserDB(db.Model):
    __tablename__ = "users_authentication"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)
    modified_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)

    username = db.Column(db.UnicodeText(), nullable=False)
    user_id  = db.Column(db.UnicodeText(), nullable=False, default=random_string_generator(20))
    
    token    = db.Column(db.UnicodeText(), nullable=False, default=random_string_generator(50, choose_from=WRITEABLE))
    passhash = db.Column(db.UnicodeText(), nullable=False)
    roles    = db.Column(db.UnicodeText(), nullable=False, default="")

    def __repr__(self) -> str:
        return f"<{self.__class__} {self.id} username='{self.username}' token='{self.token}'>"




