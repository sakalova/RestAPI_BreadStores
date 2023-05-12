from db import db


class BreadsTagsModel(db.Model):
    __tablename__ = "all_breads_tags"

    id = db.Column(db.Integer, primary_key=True)

    bread_id = db.Column(db.Integer, db.ForeignKey("all_breads.id"))
    tag_id = db.Column(db.Integer, db.ForeignKey("all_tags.id"))
