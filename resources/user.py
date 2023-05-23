import os
import redis

from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from passlib.hash import pbkdf2_sha256

from db import db
from models import UserModel

from schemas import UserSchema, UserRegisterSchema
from emails import send_user_registration_email
from sqlalchemy import or_
from rq import Queue
from dotenv import load_dotenv

from utilities.token import add_token_to_database, revoke_jti_token


load_dotenv()

blp_users = Blueprint("Users", "users", description="Operations in users.")

url = os.getenv("REDIS_URL")

if url is None:
    raise ValueError("Redis url must not be None.")

connection = redis.from_url(url)  # Get this from Render.com or run in Docker

queue = Queue("emails", connection=connection)


@blp_users.route("/register")
class UserRegister(MethodView):
    @blp_users.arguments(UserRegisterSchema)
    def post(self, user_data):
        """Create a new user and add to database."""
        if UserModel.query.filter(
            or_(
                UserModel.username == user_data["username"],
                UserModel.email == user_data["email"],
            )
        ).first():
            abort(409, message="A user with that username or email already exists.")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
            email=user_data["email"],
        )

        db.session.add(user)
        db.session.commit()

        queue.enqueue(send_user_registration_email, user.email, user.username)

        return {"message": "User created successfully."}, 201


@blp_users.route("/login")
class UserLogin(MethodView):
    @blp_users.arguments(UserSchema)
    def post(self, user_data):
        """Log in the user."""
        username = user_data["username"]
        password = user_data["password"]

        user = UserModel.query.filter(UserModel.username == username).first()

        if user and pbkdf2_sha256.verify(password, user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)

            add_token_to_database(access_token)
            add_token_to_database(refresh_token)

            return (
                jsonify(
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "message": "Successfully logged in. Access token created.",
                    }
                ),
                200,
            )

        abort(401, message="Invalid credentials.")


@blp_users.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        new_access_token = create_access_token(identity=get_jwt_identity())
        add_token_to_database(new_access_token)
        return (
            jsonify(
                {
                    "access_token": new_access_token,
                    "message": "New access token created.",
                }
            ),
            200,
        )


@blp_users.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def delete(self):
        """
        Log out the user.
        """
        payload = get_jwt()  # TODO
        jti = payload["jti"]
        user_identity = payload["sub"]
        revoke_jti_token(jti, user_identity)
        return jsonify({"message": "Successfully logged out. JWT revoked."}), 200


@blp_users.route("/user/<int:user_id>")
class User(MethodView):
    """
    User resource is created for test purposes.
    It allows to retrieve info about a single used or delete user.
    """

    @blp_users.response(200, UserSchema)
    def get(self, user_id):
        """Get requested user."""
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200
