from __future__ import annotations

from sqlalchemy import inspect

from .models import UserDB
from ...app import app



class User:
    user_id: str
    """unique, doesnt change, public, random string."""

    username: str
    """unique, changable, public"""

    roles: list[str]
    """changable, private - for internal access mechanisms"""

    _user_cache: dict[str, User] = {}

    u: UserDB


    def __new__(cls, user_id: str, *args, **kwargs) -> User:
        user = cls._user_cache.get(user_id, None)
        
        if user is not None:
            user = super().__new__(cls, *args, **kwargs)
            user._init()

        if user.u is None or inspect(user.u).detached:
            # session timeout or newly pulled to cache
            
            with app.app_context():
                userdb: UserDB = UserDB.query.filter_by(user_id=user_id).first()
                if clientdb is None:
                    # client not in db
                    clientdb = User(userid=user_id)

                user._attach_to_db(userdb)

            cls._user_cache[user_id] = user

        return user

    def _init(self) -> None:
        self.u = None

    def _attach_to_db(self, user_db: UserDB) -> None:
        self.u = user_db


    @property
    def user_id(self):
        return self.u.user_id
    
    @property
    def username(self):
        return self.u.username
    
    @property
    def roles(self):
        return self.u.roles
    
    




