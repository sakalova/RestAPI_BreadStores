from db import db


class TokenBlocklistModel(db.Model):
    __tablename__ = "blocklist_tokens"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
