from flask import Blueprint, request, jsonify
from app.services.email_service import EmailService
from app.services.tracking_service import TrackingService
from app.exceptions import NotFoundError, ValidationError, EmailTrackerException

# Blueprint for email management
email_bp = Blueprint('emails', __name__)

# Initialize services
email_service = EmailService()
tracking_service = TrackingService()


@email_bp.route('/', methods=['GET'])
def list_emails():
    """
    GET /api/emails
    List all emails with optional filtering
    Query params: campaign_id, recipient_email, sender_email, limit, offset
    """
    try:
        # Parse query parameters
        campaign_id = request.args.get('campaign_id', type=int)
        recipient_email = request.args.get('recipient_email')
        sender_email = request.args.get('sender_email')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Validate limit and offset
        if limit < 1 or limit > 100:
            return jsonify({'error': 'limit must be between 1 and 100'}), 400

        if offset < 0:
            return jsonify({'error': 'offset must be non-negative'}), 400

        # Use service to get emails
        emails, total_count = email_service.list_emails(
            campaign_id=campaign_id,
            recipient_email=recipient_email,
            sender_email=sender_email,
            limit=limit,
            offset=offset
        )

        return jsonify({
            'emails': [email.to_dict() for email in emails],
            'total': total_count,
            'limit': limit,
            'offset': offset
        }), 200

    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except ValueError as e:
        return jsonify({'error': 'Invalid parameter type', 'details': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@email_bp.route('/<int:email_id>', methods=['GET'])
def get_email(email_id):
    """
    GET /api/emails/<id>
    Get a specific email by ID with all tracking events
    """
    try:
        email = email_service.get_email(email_id)

        email_data = email.to_dict()
        email_data['events'] = [event.to_dict() for event in email.events.all()]

        return jsonify(email_data), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@email_bp.route('/', methods=['POST'])
def create_email():
    """
    POST /api/emails
    Create a new email record
    Body: {
        "recipient_email": "user@example.com",
        "sender_email": "sender@example.com",
        "subject": "Email subject",
        "body": "Email body HTML",
        "campaign_id": 1 (optional)
    }
    """
    try:
        # Validate content type
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415

        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        # Validate required fields
        required_fields = ['recipient_email', 'sender_email']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400

        # Use service to create email
        email = email_service.create_email(
            recipient_email=data['recipient_email'],
            sender_email=data['sender_email'],
            subject=data.get('subject'),
            body=data.get('body'),
            campaign_id=data.get('campaign_id')
        )

        return jsonify({
            'message': 'Email created successfully',
            'email': email.to_dict(),
            'tracking_pixel_url': f'/track/pixel/{email.tracking_id}.png'
        }), 201

    except ValidationError as e:
        return jsonify({'error': str(e), 'field': e.field}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@email_bp.route('/<int:email_id>', methods=['PUT'])
def update_email(email_id):
    """
    PUT /api/emails/<id>
    Update an email record
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Use service to update email
        email = email_service.update_email(
            email_id=email_id,
            subject=data.get('subject'),
            body=data.get('body'),
            campaign_id=data.get('campaign_id')
        )

        return jsonify({
            'message': 'Email updated successfully',
            'email': email.to_dict()
        }), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValidationError as e:
        return jsonify({'error': str(e), 'field': e.field}), 400
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@email_bp.route('/<int:email_id>', methods=['DELETE'])
def delete_email(email_id):
    """
    DELETE /api/emails/<id>
    Delete an email and all associated tracking events
    """
    try:
        email_service.delete_email(email_id)

        return jsonify({'message': 'Email deleted successfully'}), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@email_bp.route('/<int:email_id>/events', methods=['GET'])
def get_email_events(email_id):
    """
    GET /api/emails/<id>/events
    Get all tracking events for a specific email
    Query params: event_type (open, click, bounce)
    """
    try:
        event_type = request.args.get('event_type')

        # Use tracking service to get events
        events = tracking_service.get_events_for_email(email_id, event_type=event_type)

        return jsonify({
            'email_id': email_id,
            'events': [event.to_dict() for event in events],
            'total': len(events)
        }), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
