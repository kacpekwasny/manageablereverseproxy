from flask_sqlalchemy import SQLAlchemy


def create_db() -> SQLAlchemy:
    db = SQLAlchemy(session_options=dict(expire_on_commit=False))
    return db

db = create_db()