# Recruiter Request System

This document describes the recruiter request functionality that allows users to request recruiter privileges and admins to manage these requests.

## Overview

The recruiter request system provides:
- **User Request Submission**: Authenticated users can submit requests to become recruiters
- **Email Verification Requirement**: Users must verify their email before submitting requests
- **Duplicate Prevention**: Users can only have one pending request at a time
- **Admin Management**: Admin users can approve or reject requests
- **Status Tracking**: Users can track their request status
- **Email Notifications**: Users receive notifications when requests are approved/rejected
- **Request Cleanup**: Completed requests are automatically deleted after a specified period

## API Endpoints

### User Endpoints

#### Submit Recruiter Request
```http
POST /api/recruiter-requests/
Authorization: Bearer <token>
Content-Type: application/json

{
  "reason": "I want to become a recruiter to help companies find talent"
}
```

**Response (201):**
```json
{
  "id": 1,
  "status": "pending",
  "reason": "I want to become a recruiter to help companies find talent",
  "submitted_at": "2024-01-15T10:30:00Z",
  "reviewed_at": null,
  "feedback": null,
  "reapplication_guidance": null,
  "admin_notes": null
}
```

**Error Responses:**
- `400`: Email verification required
- `409`: User already has a pending request

#### Get Request Status
```http
GET /api/recruiter-requests/my-status
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "status": "pending",
  "message": "Your request is under review"
}
```

#### Get User Requests
```http
GET /api/recruiter-requests/my-requests
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "status": "pending",
    "reason": "I want to become a recruiter",
    "submitted_at": "2024-01-15T10:30:00Z",
    "reviewed_at": null,
    "feedback": null,
    "reapplication_guidance": null,
    "admin_notes": null
  }
]
```

### Admin Endpoints

#### Get All Requests
```http
GET /api/admin/recruiter-requests?status=pending&page=1&per_page=10
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "requests": [
    {
      "id": 1,
      "status": "pending",
      "reason": "I want to become a recruiter",
      "submitted_at": "2024-01-15T10:30:00Z",
      "reviewed_at": null,
      "feedback": null,
      "reapplication_guidance": null,
      "admin_notes": null
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1,
  "per_page": 10
}
```

#### Approve Request
```http
PUT /api/admin/recruiter-requests/1/approve
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "notes": "Approved based on strong profile and experience"
}
```

**Response (200):**
```json
{
  "message": "Request approved successfully"
}
```

#### Reject Request
```http
PUT /api/admin/recruiter-requests/1/reject
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "notes": "Please gain more experience on the platform before reapplying"
}
```

**Response (200):**
```json
{
  "message": "Request rejected successfully"
}
```

#### Mark Requests as Viewed
```http
POST /api/admin/recruiter-requests/mark-viewed
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "All requests marked as viewed"
}
```

#### Cleanup Completed Requests
```http
POST /api/admin/recruiter-requests/cleanup
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "Cleaned up 5 completed requests"
}
```

## Database Schema

### RecruiterRequest Model

```python
class RecruiterRequest(db.Model):
    __tablename__ = "recruiter_requests"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.Enum("pending", "approved", "rejected"), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime(timezone=True), nullable=False)
    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    reapplication_guidance = db.Column(db.Text, nullable=True)
    is_new = db.Column(db.Boolean, default=True, nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
```

## Business Logic

### Request Submission Validation
1. **Email Verification**: User must have verified email (`is_verified = True`)
2. **Duplicate Prevention**: User cannot have multiple pending requests
3. **Reason Validation**: Optional reason field with 1000 character limit

### Request Processing
1. **Admin Review**: All requests require manual admin review
2. **Role Assignment**: Approved users get `recruiter` role added to their account
3. **Email Notifications**: Users receive emails for approval/rejection decisions

### Request Cleanup
- **Approved Requests**: Deleted after 30 days
- **Rejected Requests**: Deleted after 7 days
- **Pending Requests**: Never auto-deleted (require admin action)

## Security Features

### Authentication & Authorization
- **JWT Authentication**: All endpoints require valid JWT tokens
- **Admin Role Check**: Admin endpoints verify user has `admin` role
- **User Isolation**: Users can only access their own requests

### Data Validation
- **Input Sanitization**: All input is validated using Marshmallow schemas
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
- **XSS Protection**: Proper content-type headers and validation

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "error": "Email verification required to submit recruiter request"
}
```

#### 401 Unauthorized
```json
{
  "error": "Token has expired"
}
```

#### 403 Forbidden
```json
{
  "error": "Admin access required"
}
```

#### 409 Conflict
```json
{
  "error": "You already have a pending recruiter request"
}
```

## Testing

### Manual Testing
Use the provided test script:
```bash
python test_recruiter_requests.py
```

### Test Scenarios
1. **Unverified User**: Should be blocked from submitting requests
2. **Duplicate Requests**: Should prevent multiple pending requests
3. **Admin Actions**: Should require admin role for management endpoints
4. **Email Notifications**: Should send appropriate emails for decisions

## Configuration

### Environment Variables
- `MAIL_SERVER`: SMTP server for email notifications
- `MAIL_PORT`: SMTP port
- `MAIL_USERNAME`: SMTP username
- `MAIL_PASSWORD`: SMTP password
- `MAIL_USE_TLS`: Enable TLS for SMTP

### Database Configuration
- Uses existing SQLite database
- Tables created automatically on first run
- Migrations available for production deployments

## Future Enhancements

### Potential Improvements
1. **Automated Pre-screening**: Score requests based on profile completeness
2. **Request Categories**: Different types of recruiter roles
3. **Bulk Operations**: Approve/reject multiple requests at once
4. **Analytics Dashboard**: Request statistics and trends
5. **Real-time Notifications**: WebSocket updates for admin dashboard
6. **Request Templates**: Predefined reason options
7. **SLA Tracking**: Monitor admin response times

### Scalability Considerations
1. **Background Tasks**: Use Celery for email processing
2. **Caching**: Redis for frequently accessed data
3. **Database Optimization**: Indexes for common queries
4. **Load Balancing**: Multiple admin instances
5. **Monitoring**: Request processing metrics

## Troubleshooting

### Common Issues

#### Database Connection Errors
- Check database file permissions
- Verify SQLite file exists in `instance/` directory
- Run `python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.extensions import db; db.create_all()"`

#### Email Notification Failures
- Check SMTP configuration
- Verify email credentials
- Test with `MAIL_SUPPRESS_SEND=True` for development

#### Permission Errors
- Ensure user has admin role in database
- Check JWT token validity
- Verify user authentication status

### Debug Mode
Enable debug mode in development:
```python
app.config['DEBUG'] = True
```

This will provide detailed error messages and stack traces for easier debugging.
