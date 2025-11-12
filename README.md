# Email Tracker API

A Flask-based email tracking system that monitors email opens, clicks, and provides analytics.

## Features

- **Email Management**: Create, read, update, and delete email records
- **Campaign Organization**: Group emails into campaigns for better organization
- **Tracking Pixels**: Track email opens with invisible 1x1 PNG pixels
- **Link Tracking**: Track link clicks with redirect endpoints
- **Analytics**: Comprehensive analytics for emails and campaigns
- **Device Detection**: Automatically detect device type, browser, and OS from user agents

## Tech Stack

- **Backend**: Python 3.x + Flask
- **Database**: SQLAlchemy (SQLite by default, supports PostgreSQL/MySQL)
- **Migrations**: Flask-Migrate (Alembic)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd email-tracker
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Initialize the database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Run the application

```bash
python run.py
# Or use Flask CLI:
flask run
```

The API will be available at `http://localhost:5000`

## API Documentation

### Base URL
```
http://localhost:5000
```

---

## Email Endpoints

### List Emails
```http
GET /api/emails
```

**Query Parameters:**
- `campaign_id` (optional): Filter by campaign ID
- `recipient_email` (optional): Filter by recipient
- `sender_email` (optional): Filter by sender
- `limit` (optional, default=50): Max records to return (1-100)
- `offset` (optional, default=0): Number of records to skip

**Response:**
```json
{
  "emails": [...],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

### Get Email
```http
GET /api/emails/{id}
```

**Response:**
```json
{
  "id": 1,
  "tracking_id": "abc123...",
  "recipient_email": "user@example.com",
  "sender_email": "sender@example.com",
  "subject": "Email Subject",
  "campaign_id": 1,
  "campaign_name": "Newsletter",
  "sent_at": "2024-01-01T12:00:00",
  "total_opens": 5,
  "total_clicks": 2,
  "events": [...]
}
```

### Create Email
```http
POST /api/emails
Content-Type: application/json
```

**Request Body:**
```json
{
  "recipient_email": "user@example.com",
  "sender_email": "sender@example.com",
  "subject": "Email Subject",
  "body": "<html>Email body with <img src='/track/pixel/{tracking_id}.png'></html>",
  "campaign_id": 1
}
```

**Response:**
```json
{
  "message": "Email created successfully",
  "email": {...},
  "tracking_pixel_url": "/track/pixel/abc123.png"
}
```

### Update Email
```http
PUT /api/emails/{id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "subject": "Updated Subject",
  "body": "Updated body",
  "campaign_id": 2
}
```

### Delete Email
```http
DELETE /api/emails/{id}
```

### Get Email Events
```http
GET /api/emails/{id}/events
```

**Query Parameters:**
- `event_type` (optional): Filter by event type (open, click, bounce)

---

## Campaign Endpoints

### List Campaigns
```http
GET /api/emails/campaigns
```

### Get Campaign
```http
GET /api/emails/campaigns/{id}
```

### Create Campaign
```http
POST /api/emails/campaigns
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Newsletter Campaign",
  "description": "Monthly newsletter",
  "created_by": "admin@example.com",
  "status": "draft"
}
```

### Update Campaign
```http
PUT /api/emails/campaigns/{id}
Content-Type: application/json
```

### Delete Campaign
```http
DELETE /api/emails/campaigns/{id}
```

---

## Tracking Endpoints

### Track Email Open (Pixel)
```http
GET /track/pixel/{tracking_id}.png
```

Embed this in your email HTML:
```html
<img src="http://your-domain.com/track/pixel/abc123def456.png" width="1" height="1" alt="" />
```

**Response:** Returns a 1x1 transparent PNG and records the open event.

### Track Link Click
```http
GET /track/click/{tracking_id}?url=https://example.com
```

Replace links in your email with:
```html
<a href="http://your-domain.com/track/click/abc123def456?url=https://example.com">Click Here</a>
```

**Response:** Redirects to the destination URL and records the click event.

### Track Custom Event
```http
POST /track/event
Content-Type: application/json
```

**Request Body:**
```json
{
  "tracking_id": "abc123def456",
  "event_type": "bounce"
}
```

---

## Analytics Endpoints

### Overview Analytics
```http
GET /api/analytics/overview
```

**Query Parameters:**
- `campaign_id` (optional): Filter by campaign

**Response:**
```json
{
  "total_emails": 1000,
  "total_opens": 750,
  "unique_opens": 500,
  "total_clicks": 200,
  "open_rate": 50.0,
  "click_rate": 20.0
}
```

### Email Analytics
```http
GET /api/analytics/email/{id}
```

**Response:**
```json
{
  "email_id": 1,
  "recipient": "user@example.com",
  "subject": "Email Subject",
  "sent_at": "2024-01-01T12:00:00",
  "total_opens": 5,
  "total_clicks": 2,
  "first_opened_at": "2024-01-01T12:30:00",
  "last_opened_at": "2024-01-02T10:00:00",
  "device_breakdown": {
    "desktop": 3,
    "mobile": 2
  }
}
```

### Campaign Analytics
```http
GET /api/analytics/campaign/{id}
```

---

## Database Models

### Email
- `id`: Primary key
- `tracking_id`: Unique tracking identifier (UUID)
- `recipient_email`: Recipient email address
- `sender_email`: Sender email address
- `subject`: Email subject
- `body`: Email body (HTML)
- `campaign_id`: Foreign key to Campaign
- `sent_at`: Timestamp when email was sent
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

### TrackingEvent
- `id`: Primary key
- `email_id`: Foreign key to Email
- `event_type`: Type of event (open, click, bounce, etc.)
- `ip_address`: Client IP address
- `user_agent`: Client user agent string
- `location`: Geographic location
- `device_type`: Device type (desktop, mobile, tablet)
- `clicked_url`: URL clicked (for click events)
- `created_at`: Event timestamp

### Campaign
- `id`: Primary key
- `name`: Campaign name
- `description`: Campaign description
- `created_by`: Creator email/username
- `status`: Campaign status (draft, active, completed, paused)
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

---

## Usage Example

### Python Example

```python
import requests

BASE_URL = "http://localhost:5000"

# 1. Create a campaign
campaign_response = requests.post(f"{BASE_URL}/api/emails/campaigns", json={
    "name": "Welcome Series",
    "description": "New user welcome emails"
})
campaign_id = campaign_response.json()['campaign']['id']

# 2. Create an email
email_response = requests.post(f"{BASE_URL}/api/emails", json={
    "recipient_email": "user@example.com",
    "sender_email": "noreply@myapp.com",
    "subject": "Welcome!",
    "body": "<html><body>Welcome!<img src='{pixel_url}' /></body></html>",
    "campaign_id": campaign_id
})

email_data = email_response.json()
tracking_pixel = email_data['tracking_pixel_url']
tracking_id = email_data['email']['tracking_id']

# 3. Send the email (using your email service)
# Include the tracking pixel in the HTML

# 4. Track a click
click_url = f"{BASE_URL}/track/click/{tracking_id}?url=https://myapp.com"

# 5. Get analytics
analytics = requests.get(f"{BASE_URL}/api/analytics/campaign/{campaign_id}")
print(analytics.json())
```

---

## Development

### Database Migrations

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

### Flask Shell

```bash
flask shell
```

In the shell:
```python
# Database and models are auto-imported
>>> email = Email.query.first()
>>> email.events.all()
>>> db.session.add(...)
>>> db.session.commit()
```

### Running Tests

```bash
pytest tests/
```

---

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Environment Variables

Make sure to set these in production:
- `FLASK_ENV=production`
- `DEBUG=False`
- `SECRET_KEY=<strong-random-key>`
- `DATABASE_URL=<production-database-url>`

### Database

For production, use PostgreSQL or MySQL instead of SQLite:

```bash
# PostgreSQL
pip install psycopg2-binary
export DATABASE_URL=postgresql://user:password@localhost:5432/email_tracker

# MySQL
pip install mysqlclient
export DATABASE_URL=mysql://user:password@localhost:3306/email_tracker
```

---

## Error Handling

All endpoints return errors in this format:

```json
{
  "error": "Error message",
  "details": "Detailed error information (in development mode)"
}
```

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `404`: Not Found
- `415`: Unsupported Media Type
- `500`: Internal Server Error

---

## Security Considerations

1. **Authentication**: Add authentication middleware for production
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **CORS**: Configure CORS properly for your frontend
4. **HTTPS**: Always use HTTPS in production
5. **Email Validation**: The API validates email formats, but additional checks may be needed
6. **SQL Injection**: SQLAlchemy protects against SQL injection by default

---

## License

MIT License

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Support

For issues and questions, please open an issue on GitHub.
