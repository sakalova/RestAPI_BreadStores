from typing import Dict, Tuple

from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models.bread_model import BreadModel
from schemas import BreadSchema, BreadUpdateSchema

blp_breads = Blueprint("Breads", "breads", description="Operations on all breads")


@blp_breads.route("/breads")
class BreadsSegment(MethodView):
    """Segment related to all breads."""

    @jwt_required(fresh=True)
    @blp_breads.arguments(BreadSchema)
    @blp_breads.response(201, BreadSchema)
    def post(self, bread_data: Dict[str, int | float | str | bool]) -> BreadModel:  # TODO test type annotation
        """Create a bread and add it to breads database."""
        bread = BreadModel(**bread_data)
        try:
            db.session.add(bread)
            db.session.commit()
        except IntegrityError:
            abort(400, message="Bread with that name already exists.")
        except SQLAlchemyError:
            abort(
                500,
                message="An error occurred creating a new bread and adding it to database.",
            )
        return bread

    @jwt_required()
    @blp_breads.response(200, BreadSchema(many=True))
    def get(self):
        """Get all breads stored in database."""
        return BreadModel.query.all()


@blp_breads.route("/breads/<int:uid>")
class BreadSegment(MethodView):
    @jwt_required()
    @blp_breads.response(200, BreadSchema)
    def get(self, uid: int) -> BreadModel:
        """Get requested bread."""
        bread = BreadModel.query.get_or_404(uid)
        return bread

    @jwt_required()
    def delete(self, uid: int) -> Tuple[Dict[str, str | int], int]:
        """Delete requested bread from breads database."""
        jwt: dict[str, bool | str | int] = get_jwt()

        if not jwt.get("is_admin"):
            abort(401, message="Admin rights required.")

        bread = BreadModel.query.get_or_404(uid)
        db.session.delete(bread)
        db.session.commit()

        return {
            "message": "Bread deleted from database.",
            "bread_name": bread.name,
            "bread_id": bread.id,
        }, 200

    @blp_breads.arguments(BreadUpdateSchema)
    @blp_breads.response(200, BreadSchema)
    def put(self, bread_data: Dict[str, int | float | str | bool], uid: int) -> BreadModel:
        """Update bread."""
        bread = BreadModel.query.get_or_404(uid)
        bread.name = bread_data["name"]
        bread.price = bread_data["price"]
        bread.currency = bread_data["currency"]
        bread.gluten_free = bread_data["gluten_free"]

        db.session.add(bread)
        db.session.commit()

        return bread
