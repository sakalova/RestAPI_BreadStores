from db import db


class TokenBlocklistModel(db.Model):
    __tablename__ = "blocklist_tokens"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)  # JSON Web Token
    created_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("all_users.id"), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)

    user = db.relationship("UserModel", lazy="joined")

    @classmethod
    def is_jti_blacklisted(cls, jti):
        """
        Checking if token is blacklisted.
        """
        query = cls.query.filter_by(jti=jti).first()
        if query is not None:
            return query.revoked
        else:
            return False
