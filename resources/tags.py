from typing import Any, Dict, List

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models.bakery_model import BakeryModel
from models.bread_model import BreadModel
from models.tag_model import TagModel
from schemas import TagAndBreadSchema, TagSchema

blp_tags = Blueprint("Tags", "tags", description="Operations on tags.")


@blp_tags.route("/bakeries/<int:bakery_id>/tag")
class TagsInBakery(MethodView):
    """Segment related to the requested bakery tags."""

    @blp_tags.response(200, TagSchema(many=True))
    def get(self, bakery_id: int) -> List[TagModel]:
        """Get all tags of the requested bakery."""
        bakery = BakeryModel.query.get_or_404(bakery_id)
        all_tags: List[TagModel] = bakery.tags.all()
        return all_tags

    @blp_tags.arguments(TagSchema)
    @blp_tags.response(200, TagSchema)
    def post(self, tag_data: dict[str, Any], bakery_id: int) -> TagModel:
        """Create a tag for the requested bakery in database."""
        # Check the tag name. Whether any other tags have the same bakery id as we are receiving in post request.
        # if TagModel.query.filter(TagModel.bakery == bakery_id, TagModel.name == tag_data["name"]).first():
        #     abort(400, message="A tag with that name already exists in that bakery.")

        tag = TagModel(**tag_data, bakery_id=bakery_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag


@blp_tags.route("/tag/<int:tag_id>")
class Tag(MethodView):
    """Segment related to the requested bakery tags."""

    @blp_tags.response(201, TagSchema)
    def get(self, tag_id: int) -> TagModel:
        """Get the requested tag."""
        tag: TagModel = TagModel.query.get_or_404(tag_id)
        return tag

    @blp_tags.response(
        202,
        description="Deletes a tag if no bread is tagged with it.",
        example={"message": "Tag deleted."},
    )
    @blp_tags.alt_response(404, description="Requested tag not found.")
    @blp_tags.alt_response(
        400,
        description="Returned if the tag is assigned to one or more breads. In this case, the tag is not deleted.",
    )
    def delete(self, tag_id: int) -> Dict[str, str]:
        """Delete the requested tag itself if it is not associated with any breads."""
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.breads:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted successfully."}
        abort(
            400,
            message="Could not delete tag. Make sure tag is not associated with any breads, then try again.",
        )


@blp_tags.route("/breads/<int:bread_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    """Segment related to tags and breads that are related."""

    @blp_tags.response(201, TagSchema)
    def post(self, bread_id: int, tag_id: int) -> TagModel:
        """Add a tag to a bread."""
        bread = BreadModel.query.get_or_404(bread_id)
        tag: TagModel = TagModel.query.get_or_404(tag_id)

        bread.tags.append(tag)

        try:
            db.session.add(bread)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return tag

    @blp_tags.response(200, TagAndBreadSchema)
    def delete(self, bread_id: int, tag_id: int) -> Dict[str, str]:
        """Delete tag from bread."""
        bread = BreadModel.query.get_or_404(bread_id)
        tag = TagModel.query.get_or_404(tag_id)

        try:
            bread.tags.remove(tag)
            db.session.add(bread)
            db.session.commit()
        except ValueError:
            abort(404, message="Tag not found in tags of bread.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the tag.")

        return {"message": "Bread removed from tag", "bread": bread, "tag": tag}
