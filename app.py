import os
import redis

from flask import Flask, jsonify
from flask_migrate import Migrate

from flask_smorest import Api
from flask_jwt_extended import JWTManager
from blocklist import BLOCKLIST
from db import db
from dotenv import load_dotenv
from rq import Queue

from resources.breads import blp_breads as BreadsSegmentBlueprint
from resources.bakeries import blp_bakeries as BakeriesSegmentBlueprint
from resources.tags import blp_tags as TagsSegmentBlueprint
from resources.user import blp_users as UserBlueprint


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    connection = redis.from_url(
        os.getenv("RADIS_URL")
    )
    app.queue = Queue("emails", connection=connection)
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Breads REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)

    with app.app_context():
        db.create_all()

    app.config["JWT_SECRET_KEY"] = "16890974721412720643745332657034989076"
    jwt = JWTManager(app)

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        return {"is_admin": identity == 1}

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        """
        Check whether any JWT received is in the blocklist.
        """
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token is not fresh.", "error": "fresh_token_required"}
            )
        )

    # Problem scenarios
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            400,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed", "error": "invalid_token"}
            ),
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

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(BreadsSegmentBlueprint)
    api.register_blueprint(BakeriesSegmentBlueprint)
    api.register_blueprint(TagsSegmentBlueprint)

    return app
