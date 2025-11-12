from flask import Blueprint, request, jsonify, send_file, redirect
from app.services.tracking_service import TrackingService
from app.utils import create_tracking_pixel, validate_url, parse_user_agent
from app.exceptions import NotFoundError, ValidationError, EmailTrackerException
import io

# Blueprint for tracking (pixel/link tracking)
tracking_bp = Blueprint('tracking', __name__)

# Initialize service
tracking_service = TrackingService()


@tracking_bp.route('/pixel/<tracking_id>.png', methods=['GET'])
def track_pixel(tracking_id):
    """
    GET /track/pixel/<tracking_id>.png
    Tracking pixel endpoint - records email open
    Returns a 1x1 transparent PNG
    """
    try:
        # Extract request metadata
        metadata = tracking_service.parse_request_metadata(request)

        # Record open event using service
        tracking_service.record_open(
            tracking_id=tracking_id,
            ip_address=metadata['ip_address'],
            user_agent=metadata['user_agent'],
            location=metadata['location']
        )

    except NotFoundError:
        # Email not found - still return pixel but don't track
        pass
    except Exception as e:
        # Don't fail the pixel request even if tracking fails
        # Just log the error (in production, use proper logging)
        print(f"Tracking error: {e}")

    # Always return the pixel, even if tracking failed
    pixel = create_tracking_pixel()
    return send_file(
        io.BytesIO(pixel),
        mimetype='image/png',
        as_attachment=False,
        download_name='pixel.png'
    )


@tracking_bp.route('/click/<tracking_id>', methods=['GET'])
def track_click(tracking_id):
    """
    GET /track/click/<tracking_id>?url=<destination>
    Tracking link endpoint - records email link click
    Query params: url (destination URL to redirect to)
    """
    destination_url = request.args.get('url', '/')

    # Validate destination URL
    if destination_url != '/' and not validate_url(destination_url):
        return jsonify({'error': 'Invalid destination URL'}), 400

    try:
        # Extract request metadata
        metadata = tracking_service.parse_request_metadata(request)

        # Record click event using service
        tracking_service.record_click(
            tracking_id=tracking_id,
            clicked_url=destination_url,
            ip_address=metadata['ip_address'],
            user_agent=metadata['user_agent'],
            location=metadata['location']
        )

    except NotFoundError:
        # Email not found - still redirect but don't track
        pass
    except Exception as e:
        # Don't fail the redirect even if tracking fails
        print(f"Tracking error: {e}")

    # Always redirect, even if tracking failed
    return redirect(destination_url, code=302)


@tracking_bp.route('/event', methods=['POST'])
def track_custom_event():
    """
    POST /track/event
    Track a custom event (open, click, bounce, unsubscribe, etc.)
    Body: {
        "tracking_id": "abc123",
        "event_type": "open|click|bounce|unsubscribe|etc",
        "clicked_url": "https://example.com" (optional, for click events)
    }
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415

        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        # Validate required fields
        required_fields = ['tracking_id', 'event_type']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400

        # Extract request metadata
        metadata = tracking_service.parse_request_metadata(request)

        event_type = data['event_type']
        tracking_id = data['tracking_id']
        clicked_url = data.get('clicked_url')

        # Use the appropriate service method based on event type
        if event_type == 'open':
            event = tracking_service.record_open(
                tracking_id=tracking_id,
                ip_address=metadata['ip_address'],
                user_agent=metadata['user_agent'],
                location=metadata['location']
            )
        elif event_type == 'click':
            if not clicked_url:
                return jsonify({'error': 'clicked_url is required for click events'}), 400

            event = tracking_service.record_click(
                tracking_id=tracking_id,
                clicked_url=clicked_url,
                ip_address=metadata['ip_address'],
                user_agent=metadata['user_agent'],
                location=metadata['location']
            )
        else:
            # For other event types (bounce, unsubscribe, etc.), use record_open logic
            # but with the specified event_type
            email = tracking_service.email_service.get_email_by_tracking_id(tracking_id)

            device_type = None
            if metadata['user_agent']:
                parsed = parse_user_agent(metadata['user_agent'])
                device_type = parsed['device_type']

            from app.models import TrackingEvent
            event = TrackingEvent(
                email_id=email.id,
                event_type=event_type,
                ip_address=metadata['ip_address'],
                user_agent=metadata['user_agent'],
                location=metadata['location'],
                device_type=device_type,
                clicked_url=clicked_url
            )

            from app import db
            db.session.add(event)
            db.session.commit()

        return jsonify({
            'message': 'Event tracked successfully',
            'event': event.to_dict()
        }), 201

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValidationError as e:
        return jsonify({'error': str(e), 'field': e.field}), 400
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
