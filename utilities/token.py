from datetime import datetime
from datetime import timezone

from db import db

from sqlalchemy.orm.exc import NoResultFound

from flask_jwt_extended import decode_token
from models import TokenBlocklistModel


def add_token_to_database(encoded_token):
    """
    Function adds provided token to blocklist_tokens table in database.
    """
    decoded_token = decode_token(encoded_token)
    jti = decoded_token["jti"]
    token_type = decoded_token["type"]
    token_created_at = datetime.now(timezone.utc)
    token_expires = datetime.fromtimestamp(decoded_token["exp"])
    token_revoked = False
    user_identity = decoded_token["sub"]

    db_token = TokenBlocklistModel(
        jti=jti,
        type=token_type,
        created_at=token_created_at,
        expires_at=token_expires,
        revoked=token_revoked,
        user_id=user_identity,
    )
    db.session.add(db_token)
    db.session.commit()


def revoke_jti_token(token_jti, user_identity):
    """
    Revokes given token.
    Using it only on logout.
    """
    try:
        token = TokenBlocklistModel.query.filter_by(
            jti=token_jti, user_id=user_identity
        ).one()
        token.revoked = True
        db.session.commit()
    except NoResultFound:
        raise Exception(f"Could not find the token {token_jti}.")
