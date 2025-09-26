from marshmallow import Schema, fields, validate, ValidationError, validates_schema
import re
class RegisterSchema(Schema):
    email = fields.Email(required=True)
    # Let application-level strength validator handle length/complexity
    password = fields.String(required=True)
    username = fields.String(required=True, validate=validate.Regexp(r'^[a-zA-Z0-9_]+$'))
    @validates_schema
    def check_strength(self, data, **kwargs):
        pw = data.get("password", "")
        if not re.search(r'[A-Z]', pw):
            raise ValidationError("Password must contain at least one uppercase letter", field_name="password")
        if not re.search(r'[a-z]', pw):
            raise ValidationError("Password must contain at least one lowercase letter", field_name="password")
        if not re.search(r'\d', pw):
            raise ValidationError("Password must contain at least one number", field_name="password")

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class ResetPasswordRequestSchema(Schema):
    email = fields.Email(required=True)


class VerifyResetPasswordSchema(Schema):
    token = fields.String(required=True)
    # Let application-level strength validator handle length/complexity
    new_password = fields.String(required=True)
    @validates_schema
    def check_strength(self, data, **kwargs):
        pw = data.get("new_password", "")
        if not re.search(r'[A-Z]', pw):
            raise ValidationError("Password must contain at least one uppercase letter", field_name="password")
        if not re.search(r'[a-z]', pw):
            raise ValidationError("Password must contain at least one lowercase letter", field_name="password")
        if not re.search(r'\d', pw):
            raise ValidationError("Password must contain at least one number", field_name="password")
