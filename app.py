import os

from flask import Flask
from flask_migrate import Migrate
from flask_smorest import Api

from db import db
from dotenv import load_dotenv

from resources.breads import blp_breads as BreadsSegmentBlueprint
from resources.bakeries import blp_bakeries as BakeriesSegmentBlueprint
from resources.tags import blp_tags as TagsSegmentBlueprint
from resources.user import blp_users as UserBlueprint

from jwt_extension import jwt


def create_app(db_url=None):
    app = Flask(__name__)

    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Breads REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)

    with app.app_context():
        db.create_all()

    app.config["JWT_SECRET_KEY"] = "16890974721412720643745332657034989076"
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

    jwt.init_app(app)

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(BreadsSegmentBlueprint)
    api.register_blueprint(BakeriesSegmentBlueprint)
    api.register_blueprint(TagsSegmentBlueprint)

    return app
