from flask import jsonify
from flask_jwt_extended import JWTManager

from models import TokenBlocklistModel, UserModel


jwt = JWTManager()


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    return {"is_admin": identity == 1}


@jwt.user_lookup_loader
def user_loader_callback(jwt_headers, jwt_payload):
    identity = jwt_payload["sub"]
    return UserModel.query.get(identity)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    """
    Check whether any JWT received is in the blocklist and token revoked.
    """
    jti = jwt_payload["jti"]
    return TokenBlocklistModel.is_jti_blacklisted(jti)


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "description": "The token has been revoked.",
                "error": "token_revoked",
                "jwt_header": jwt_header,
                "jwt_payload": jwt_payload,
            }
        ),
        401,
    )


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify(
        {"description": "The token is not fresh.", "error": "fresh_token_required"}
    )


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "message": "The token has expired.",
                "error": "token_expired",
                "jwt_header": jwt_header,
                "jwt_payload": jwt_payload,
            }
        ),
        400,
    )


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify({"message": "Signature verification failed", "error": "invalid_token"}),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )
