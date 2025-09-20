from marshmallow import Schema, fields, validate


class SubmitRequestSchema(Schema):
    reason = fields.String(
        required=False, 
        allow_none=True, 
        validate=validate.Length(max=1000)
    )


class ReviewRequestSchema(Schema):
    notes = fields.String(
        required=False, 
        allow_none=True, 
        validate=validate.Length(max=500)
    )


class RequestStatusSchema(Schema):
    id = fields.Integer()
    status = fields.String()
    reason = fields.String(allow_none=True)
    submitted_at = fields.DateTime()
    reviewed_at = fields.DateTime(allow_none=True)
    feedback = fields.String(allow_none=True)
    reapplication_guidance = fields.String(allow_none=True)
    admin_notes = fields.String(allow_none=True)


class RequestListSchema(Schema):
    requests = fields.List(fields.Nested(RequestStatusSchema))
    total = fields.Integer()
    pages = fields.Integer()
    current_page = fields.Integer()
    per_page = fields.Integer()
