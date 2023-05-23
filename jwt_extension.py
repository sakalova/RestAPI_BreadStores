from flask import jsonify
from flask_jwt_extended import JWTManager
from flask import make_response, Response

from models.tokenblocklist_model import TokenBlocklistModel
from models.user_model import UserModel

from typing import Dict


jwt = JWTManager()


@jwt.additional_claims_loader
def add_claims_to_jwt(identity: int) -> Dict[str, bool]:
    return {"is_admin": identity == 1}


@jwt.user_lookup_loader
def user_loader_callback(
    jwt_header: Dict[str, str], jwt_payload: Dict[str, int | str | bool]
) -> UserModel:
    identity = jwt_payload["sub"]
    user: UserModel = UserModel.query.get(identity)
    return user


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(
    jwt_header: Dict[str, str], jwt_payload: Dict[str, int | str | bool]
) -> bool:
    """
    Check whether any JWT received is in the blocklist and token revoked.
    """
    jti = jwt_payload["jti"]
    return TokenBlocklistModel.is_jti_blacklisted(jti)


@jwt.revoked_token_loader
def revoked_token_callback(
    jwt_header: Dict[str, str], jwt_payload: Dict[str, int | str | bool]
) -> Response:
    resp = make_response(
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
    return resp


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(
    jwt_header: Dict[str, str], jwt_payload: Dict[str, int | str | bool]
) -> Response:
    resp = make_response(
        jsonify(
            {"description": "The token is not fresh.", "error": "fresh_token_required"}
        ),
        400,
    )
    return resp


@jwt.expired_token_loader
def expired_token_callback(
        jwt_header: Dict[str, str], jwt_payload: Dict[str, int | str | bool]
) -> Response:
    resp = make_response(
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
    return resp


@jwt.invalid_token_loader
def invalid_token_callback(error) -> Response:
    resp = make_response(
        jsonify({"message": "Signature verification failed", "error": "invalid_token"}),
        401
    )
    return resp


@jwt.unauthorized_loader
def missing_token_callback(error) -> Response:
    resp = make_response(
        {
            "description": "Request does not contain an access token.",
            "error": "authorization_required",
        },
        401
    )
    return resp
