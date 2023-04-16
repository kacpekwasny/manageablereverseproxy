import datetime
from ...app import db


class ClientIPAddress(db.Model):
    __tablename__ = 'client_ip_address'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)
    modified_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)

    whitelisted = db.Column(db.Boolean(), default=False, nullable=False)
    blacklisted = db.Column(db.Boolean(), default=False, nullable=False)



