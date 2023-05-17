from db import db


class BakeryModel(db.Model):  # type: ignore
    __tablename__ = "all_bakeries"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    address = db.Column(db.String(80), unique=True, nullable=False)

    tags = db.relationship("TagModel", back_populates="bakery", lazy="dynamic")
    breads = db.relationship("BreadModel", back_populates="bakery", lazy="dynamic")
