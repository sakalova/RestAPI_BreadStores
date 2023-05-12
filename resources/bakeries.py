from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import BakerySchema
from models.bakery_model import BakeryModel
from db import db


blp_bakeries = Blueprint("Bakeries", "bakeries", description="Operations on bakeries.")


@blp_bakeries.route("/bakeries/<string:bakery_id>")
class Bakery(MethodView):
    @blp_bakeries.response(200, BakerySchema)
    def get(self, bakery_id):
        """Get requested bakery."""
        bakery = BakeryModel.query.get_or_404(bakery_id)
        return bakery

    def delete(self, bakery_id):
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
    def get(self):
        """Get list of all bakeries."""
        return BakeryModel.query.all()

    @blp_bakeries.arguments(BakerySchema)
    @blp_bakeries.response(201, BakerySchema)
    def post(self, store_data):
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
