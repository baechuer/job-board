from marshmallow import Schema, fields, validate, ValidationError, validates_schema


class RecruiterPostJobSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=3))
    description = fields.String(required=True, validate=validate.Length(min=10))
    salary_min = fields.Float(required=True, validate=validate.Range(min=0))
    salary_max = fields.Float(required=True, validate=validate.Range(min=0))
    location = fields.String(required=True)
    requirements = fields.List(fields.String(validate=validate.Length(min=1)), required=True)
    responsibilities = fields.String(required=True)
    skills = fields.List(fields.String(validate=validate.Length(min=1)), required=True)
    application_deadline = fields.Date(required=True)

    @validates_schema
    def validate_salary_range(self, data, **kwargs):
        min_val = data.get('salary_min')
        max_val = data.get('salary_max')
        if min_val is not None and max_val is not None and min_val > max_val:
            raise ValidationError('salary_min must be less than or equal to salary_max', field_name='salary')

    # Optional extended fields (validated with choices where sensible)
    employment_type = fields.String(validate=validate.OneOf(['full_time','part_time','contract','internship','temporary']))
    seniority = fields.String(validate=validate.OneOf(['intern','junior','mid','senior','lead']))
    work_mode = fields.String(validate=validate.OneOf(['onsite','remote','hybrid']))
    visa_sponsorship = fields.Boolean()
    work_authorization = fields.String(allow_none=True)
    nice_to_haves = fields.String(allow_none=True)
    about_team = fields.String(allow_none=True)


class RecruiterJobUpdateSchema(Schema):
    title = fields.String(validate=validate.Length(min=3))
    description = fields.String(validate=validate.Length(min=10))
    salary_min = fields.Float()
    salary_max = fields.Float()
    location = fields.String()
    requirements = fields.List(fields.String(validate=validate.Length(min=1)))
    responsibilities = fields.String()
    skills = fields.List(fields.String(validate=validate.Length(min=1)))
    application_deadline = fields.Date()
    employment_type = fields.String(validate=validate.OneOf(['full_time','part_time','contract','internship','temporary']))
    seniority = fields.String(validate=validate.OneOf(['intern','junior','mid','senior','lead']))
    work_mode = fields.String(validate=validate.OneOf(['onsite','remote','hybrid']))
    visa_sponsorship = fields.Boolean()
    work_authorization = fields.String()
    nice_to_haves = fields.String()
    about_team = fields.String()