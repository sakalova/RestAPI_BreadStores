from marshmallow import Schema, fields


class TemplateBreadSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    currency = fields.Str(required=True)
    gluten_free = fields.Bool(required=True)


class TemplateBakerySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    address = fields.Str(required=True)


class TemplateTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class BreadSchema(TemplateBreadSchema):
    bakery_id = fields.Int(required=True, load_only=True)
    bakery = fields.Nested(TemplateBakerySchema(), dump_only=True)
    tags = fields.List(fields.Nested(TemplateTagSchema()), dump_only=True)


class BakerySchema(TemplateBakerySchema):
    breads = fields.List(fields.Nested(TemplateBreadSchema()), dump_only=True)
    tags = fields.List(fields.Nested(TemplateTagSchema()), dump_only=True)


class TagSchema(TemplateTagSchema):
    bakery_id = fields.Int(load_only=True)
    breads = fields.List(fields.Nested(TemplateBreadSchema()), dump_only=True)
    bakery = fields.Nested(TemplateBakerySchema(), dump_only=True)


class TagAndBreadSchema(Schema):
    message = fields.Str()
    bread = fields.Nested(BreadSchema)
    tag = fields.Nested(TagSchema)


class BreadUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    currency = fields.Str()
    gluten_free = fields.Bool()


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserRegisterSchema(UserSchema):
    email = fields.Str(required=True)


class TokenBlocklistSchema(UserSchema):
    pass