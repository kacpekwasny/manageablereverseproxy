import datetime

from ...db import db


class ClientIPAddress(db.Model):
    __tablename__ = 'client_ip_address'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)
    modified_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)

    ip_address = db.Column(db.Text(), nullable=False)
    whitelisted = db.Column(db.Boolean(), default=False, nullable=False)
    blacklisted = db.Column(db.Boolean(), default=False, nullable=False)

    def to_dict(self) -> dict:
        return {
            "ip_address": self.ip_address,
            "created_at": self.created_at,
            "whitelisted": self.whitelisted,
            "blacklisted": self.blacklisted,
        }