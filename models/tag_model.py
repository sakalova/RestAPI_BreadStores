from db import db


class TagModel(db.Model):
    __tablename__ = "all_tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)

    bakery_id = db.Column(db.Integer, db.ForeignKey("all_bakeries.id"), nullable=False)

    bakery = db.relationship("BakeryModel", back_populates="tags")
    breads = db.relationship(
        "BreadModel", back_populates="tags", secondary="all_breads_tags"
    )
