from typing import Dict, List, Tuple

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models.bakery_model import BakeryModel
from schemas import BakerySchema

blp_bakeries = Blueprint("Bakeries", "bakeries", description="Operations on bakeries.")


@blp_bakeries.route("/bakeries/<string:bakery_id>")
class Bakery(MethodView):
    @blp_bakeries.response(200, BakerySchema)
    def get(self, bakery_id: str):
        """Get requested bakery."""
        return BakeryModel.query.get_or_404(bakery_id)

    def delete(self, bakery_id: str) -> Tuple[Dict[str, str | int], int]:
        """Delete requested bakery."""
        bakery = BakeryModel.query.get_or_404(bakery_id)
        db.session.delete(bakery)
        db.session.commit()
        return {
            "message": "Bakery deleted",
            "bakery_name": bakery.name,
            "bakery_id": bakery.id,
        }, 200


@blp_bakeries.route("/bakeries")
class Bakeries(MethodView):
    @blp_bakeries.response(200, BakerySchema(many=True))
    def get(self) -> List[BakeryModel]:
        """Get list of all bakeries."""
        all_bakeries = BakeryModel.query.all()
        return all_bakeries

    @blp_bakeries.arguments(BakerySchema)
    @blp_bakeries.response(201, BakerySchema)
    def post(self, store_data: Dict[str, str]) -> BakeryModel:
        """Create a new bakery and add it to database."""
        bakery = BakeryModel(**store_data)
        try:
            db.session.add(bakery)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message=f"A bakery with the name {bakery.name} already exists.",
            )
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the bakery.")

        return bakery
