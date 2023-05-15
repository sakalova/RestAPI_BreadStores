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
from blocklist import BLOCKLIST
from emails import send_message
from sqlalchemy import or_

blp_users = Blueprint("Users", "users", description="Operations in users.")


@blp_users.route("/register")
class UserRegister(MethodView):
    @blp_users.arguments(UserRegisterSchema)
    def post(self, user_data):
        """Create a new user and add to database."""
        if UserModel.query.filter(
                or_(
                    UserModel.username == user_data["username"],
                    UserModel.email == user_data["email"]
                )
        ).first():
            abort(409, message="A user with that username or email already exists.")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
            email=user_data["email"]
        )

        db.session.add(user)
        db.session.commit()

        send_message(
            to=user.email,
            subject="Successfully signed up",
            text="Welcome! Thank you for signing up to the Breads Rest API!"
        )

        return {"message": "User created successfully."}, 201


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


@blp_users.route("/login")
class UserLogin(MethodView):

    @blp_users.arguments(UserSchema)
    def post(self, user_data):
        """Log in the user."""
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message="Invalid credentials.")


@blp_users.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        """Log out the user."""
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


@blp_users.route("/refresh")
class TokenRefresh(MethodView):

    @jwt_required(refresh=True)
    def post(self):
        new_token = create_access_token(identity=get_jwt_identity(), fresh=False)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}
