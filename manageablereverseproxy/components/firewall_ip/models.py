import datetime

from time import time

from ...app import db
from ...logger import InheritLogger


class ClientIPAddressDB(db.Model):
    __tablename__ = 'client_ip_address'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)
    modified_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)

    ip_address = db.Column(db.Text(), nullable=False)
    whitelisted = db.Column(db.Boolean(), default=False, nullable=False)
    blacklisted = db.Column(db.Boolean(), default=False, nullable=False)

