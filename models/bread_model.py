from db import db


class BreadModel(db.Model):  # type: ignore
    __tablename__ = "all_breads"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)
    currency = db.Column(db.String(3), unique=False, nullable=False)
    gluten_free = db.Column(db.Boolean, unique=False, nullable=False)
    info = db.Column(db.String)

    bakery_id = db.Column(
        db.Integer, db.ForeignKey("all_bakeries.id"), unique=False, nullable=False
    )

    tags = db.relationship(
        "TagModel", back_populates="breads", secondary="all_breads_tags"
    )
    bakery = db.relationship("BakeryModel", back_populates="breads")
