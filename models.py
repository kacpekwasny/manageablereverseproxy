import datetime
from app import db


class Firewall(db.Model):
    __tablename__ = 'firewall'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)
    modified_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)
