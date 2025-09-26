import pytest
from marshmallow import ValidationError
from app.schemas.application_schema import (
    ApplicationSubmitSchema,
    ApplicationListSchema,
    ApplicationUpdateSchema
)


class TestApplicationSubmitSchema:
    """Test ApplicationSubmitSchema validation"""
    
    def test_valid_data(self):
        """Test schema with valid data"""
        schema = ApplicationSubmitSchema()
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'currentCompany': 'Tech Corp',
            'currentPosition': 'Software Engineer',
            'experience': '3-5 years',
            'education': 'bachelor',
            'skills': 'Python, JavaScript, React',
            'portfolio': 'https://johndoe.dev',
            'linkedin': 'https://linkedin.com/in/johndoe',
            'github': 'https://github.com/johndoe',
            'availability': 'Immediately',
            'salaryExpectation': '$80,000 - $100,000',
            'noticePeriod': '2 weeks',
            'workAuthorization': 'US Citizen',
            'relocation': 'Yes',
            'additionalInfo': 'Passionate about technology'
        }
        
        result = schema.load(data)
        assert result['firstName'] == 'John'
        assert result['email'] == 'john.doe@example.com'
    
    def test_required_fields(self):
        """Test that required fields are validated"""
        schema = ApplicationSubmitSchema()
        data = {
            'lastName': 'Doe',
            'email': 'john.doe@example.com'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'firstName' in str(exc_info.value.messages)
    
    def test_invalid_email(self):
        """Test invalid email validation"""
        schema = ApplicationSubmitSchema()
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'invalid-email'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'email' in str(exc_info.value.messages)
    
    def test_invalid_name_characters(self):
        """Test name validation with invalid characters"""
        schema = ApplicationSubmitSchema()
        data = {
            'firstName': 'John123',
            'lastName': 'Doe',
            'email': 'john.doe@example.com'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'firstName' in str(exc_info.value.messages)
    
    def test_invalid_experience_choice(self):
        """Test invalid experience choice"""
        schema = ApplicationSubmitSchema()
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'experience': 'invalid-experience'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'experience' in str(exc_info.value.messages)
    
    def test_invalid_url_format(self):
        """Test invalid URL format"""
        schema = ApplicationSubmitSchema()
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'portfolio': 'not-a-url'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'portfolio' in str(exc_info.value.messages)
    
    def test_url_without_protocol(self):
        """Test URL without http/https protocol"""
        schema = ApplicationSubmitSchema()
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'linkedin': 'linkedin.com/in/johndoe'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'linkedin' in str(exc_info.value.messages)


class TestApplicationListSchema:
    """Test ApplicationListSchema validation"""
    
    def test_valid_query_params(self):
        """Test schema with valid query parameters"""
        schema = ApplicationListSchema()
        data = {
            'page': 2,
            'per_page': 10,
            'status': 'submitted'
        }
        
        result = schema.load(data)
        assert result['page'] == 2
        assert result['per_page'] == 10
        assert result['status'] == 'submitted'
    
    def test_default_values(self):
        """Test default values for missing fields"""
        schema = ApplicationListSchema()
        data = {}
        
        result = schema.load(data)
        assert result['page'] == 1
        assert result['per_page'] == 20
        # Status is optional and won't be included if not provided
        assert 'status' not in result
    
    def test_invalid_page_range(self):
        """Test invalid page range"""
        schema = ApplicationListSchema()
        data = {
            'page': 0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'page' in str(exc_info.value.messages)
    
    def test_invalid_per_page_range(self):
        """Test invalid per_page range"""
        schema = ApplicationListSchema()
        data = {
            'per_page': 200
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'per_page' in str(exc_info.value.messages)
    
    def test_invalid_status(self):
        """Test invalid status value"""
        schema = ApplicationListSchema()
        data = {
            'status': 'invalid-status'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'status' in str(exc_info.value.messages)


class TestApplicationUpdateSchema:
    """Test ApplicationUpdateSchema validation"""
    
    def test_valid_update_data(self):
        """Test schema with valid update data"""
        schema = ApplicationUpdateSchema()
        data = {
            'status': 'accepted',
            'notes': 'Great candidate',
            'feedback': 'Excellent technical skills'
        }
        
        result = schema.load(data)
        assert result['status'] == 'accepted'
        assert result['notes'] == 'Great candidate'
        assert result['feedback'] == 'Excellent technical skills'
    
    def test_required_status(self):
        """Test that status is required"""
        schema = ApplicationUpdateSchema()
        data = {
            'notes': 'Great candidate'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'status' in str(exc_info.value.messages)
    
    def test_invalid_status(self):
        """Test invalid status value"""
        schema = ApplicationUpdateSchema()
        data = {
            'status': 'invalid-status'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'status' in str(exc_info.value.messages)
    
    def test_long_notes(self):
        """Test notes field length validation"""
        schema = ApplicationUpdateSchema()
        data = {
            'status': 'reviewed',
            'notes': 'x' * 1001  # Exceeds 1000 character limit
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'notes' in str(exc_info.value.messages)
    
    def test_long_feedback(self):
        """Test feedback field length validation"""
        schema = ApplicationUpdateSchema()
        data = {
            'status': 'rejected',
            'feedback': 'x' * 2001  # Exceeds 2000 character limit
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'feedback' in str(exc_info.value.messages)
