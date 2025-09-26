from marshmallow import Schema, fields, validate, ValidationError, validates_schema
import re


class ApplicationSubmitSchema(Schema):
    """Schema for validating job application submission"""
    
    # Required personal information
    firstName = fields.String(required=True, validate=validate.Length(min=1, max=100))
    lastName = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    
    # Optional personal information
    phone = fields.String(validate=validate.Length(max=20), allow_none=True)
    
    # Professional information
    currentCompany = fields.String(validate=validate.Length(max=255), allow_none=True)
    currentPosition = fields.String(validate=validate.Length(max=255), allow_none=True)
    experience = fields.String(
        validate=validate.OneOf([
            '0-1 years', '1-2 years', '2-3 years', '3-5 years', 
            '5-10 years', '10+ years'
        ]), 
        allow_none=True
    )
    education = fields.String(
        validate=validate.OneOf([
            'high-school', 'associate', 'bachelor', 'master', 'phd', 'other'
        ]), 
        allow_none=True
    )
    skills = fields.String(validate=validate.Length(max=2000), allow_none=True)
    
    # Contact information
    portfolio = fields.String(validate=validate.Length(max=500), allow_none=True)
    linkedin = fields.String(validate=validate.Length(max=500), allow_none=True)
    github = fields.String(validate=validate.Length(max=500), allow_none=True)
    
    # Application details
    availability = fields.String(validate=validate.Length(max=255), allow_none=True)
    salaryExpectation = fields.String(validate=validate.Length(max=100), allow_none=True)
    noticePeriod = fields.String(validate=validate.Length(max=100), allow_none=True)
    workAuthorization = fields.String(validate=validate.Length(max=255), allow_none=True)
    relocation = fields.String(validate=validate.Length(max=100), allow_none=True)
    additionalInfo = fields.String(validate=validate.Length(max=2000), allow_none=True)
    
    @validates_schema
    def validate_names(self, data, **kwargs):
        """Validate that names contain only letters, spaces, hyphens, and apostrophes"""
        first_name = data.get('firstName', '')
        last_name = data.get('lastName', '')
        
        name_pattern = r"^[a-zA-Z\s\-']+$"
        
        if first_name and not re.match(name_pattern, first_name):
            raise ValidationError('First name can only contain letters, spaces, hyphens, and apostrophes', field_name='firstName')
        
        if last_name and not re.match(name_pattern, last_name):
            raise ValidationError('Last name can only contain letters, spaces, hyphens, and apostrophes', field_name='lastName')
    
    @validates_schema
    def validate_urls(self, data, **kwargs):
        """Validate that URLs are properly formatted"""
        urls = ['portfolio', 'linkedin', 'github']
        
        for url_field in urls:
            url_value = data.get(url_field)
            if url_value and not url_value.startswith(('http://', 'https://')):
                raise ValidationError(f'{url_field} must be a valid URL starting with http:// or https://', field_name=url_field)


class ApplicationListSchema(Schema):
    """Schema for validating application list query parameters"""
    
    page = fields.Integer(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Integer(validate=validate.Range(min=1, max=100), load_default=20)
    status = fields.String(
        validate=validate.OneOf(['submitted', 'reviewed', 'accepted', 'rejected']), 
        allow_none=True
    )


class ApplicationUpdateSchema(Schema):
    """Schema for updating application status (admin/recruiter use)"""
    
    status = fields.String(
        required=True,
        validate=validate.OneOf(['submitted', 'reviewed', 'accepted', 'rejected'])
    )
    notes = fields.String(validate=validate.Length(max=1000), allow_none=True)
    feedback = fields.String(validate=validate.Length(max=2000), allow_none=True)


class FileUploadSchema(Schema):
    """Schema for validating file uploads"""
    
    @validates_schema
    def validate_file_type(self, data, **kwargs):
        """Validate that uploaded files are PDFs"""
        # This validation is handled at the service level for file uploads
        # but we can add additional validation here if needed
        pass
