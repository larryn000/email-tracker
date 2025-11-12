from app import db
from app.models import TrackingEvent, Email
from app.exceptions import NotFoundError, ValidationError
from app.utils import parse_user_agent
from app.services.email_service import EmailService


class TrackingService:
    """Service for managing tracking events"""

    def __init__(self, db_session=None, email_service=None):
        """
        Initialize TrackingService

        Args:
            db_session: Database session (defaults to db.session)
            email_service: EmailService instance (defaults to new instance)
        """
        self._db_session = db_session
        self._email_service = email_service

    @property
    def db(self):
        """Lazy database session property - only accesses db.session when used"""
        return self._db_session if self._db_session is not None else db.session

    @property
    def email_service(self):
        """Lazy email service property"""
        if self._email_service is None:
            self._email_service = EmailService(self._db_session)
        return self._email_service

    def record_open(self, tracking_id, ip_address=None, user_agent=None, location=None):
        """
        Record an email open event

        Args:
            tracking_id: Email tracking ID
            ip_address: IP address of the user
            user_agent: User agent string
            location: Geographic location (optional)

        Returns:
            TrackingEvent: Created tracking event

        Raises:
            NotFoundError: If email with tracking_id doesn't exist
        """
        # Use email service to get email (handles NotFoundError)
        email = self.email_service.get_email_by_tracking_id(tracking_id)

        # Parse device type from user agent
        device_type = None
        if user_agent:
            parsed = parse_user_agent(user_agent)
            device_type = parsed['device_type']

        # Create tracking event
        event = TrackingEvent(
            email_id=email.id,
            event_type='open',
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            device_type=device_type
        )

        self.db.add(event)
        self.db.commit()

        return event

    def record_click(self, tracking_id, clicked_url, ip_address=None, user_agent=None, location=None):
        """
        Record a link click event

        Args:
            tracking_id: Email tracking ID
            clicked_url: URL that was clicked
            ip_address: IP address of the user
            user_agent: User agent string
            location: Geographic location (optional)

        Returns:
            TrackingEvent: Created tracking event

        Raises:
            NotFoundError: If email with tracking_id doesn't exist
            ValidationError: If clicked_url is missing
        """
        if not clicked_url:
            raise ValidationError("clicked_url is required for click events")

        # Use email service to get email (handles NotFoundError)
        email = self.email_service.get_email_by_tracking_id(tracking_id)

        # Parse device type from user agent
        device_type = None
        if user_agent:
            parsed = parse_user_agent(user_agent)
            device_type = parsed['device_type']

        # Create tracking event
        event = TrackingEvent(
            email_id=email.id,
            event_type='click',
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            device_type=device_type,
            clicked_url=clicked_url
        )

        self.db.add(event)
        self.db.commit()

        return event

    def get_event(self, event_id):
        """
        Get a tracking event by ID

        Args:
            event_id: Event ID

        Returns:
            TrackingEvent: Tracking event instance

        Raises:
            NotFoundError: If event doesn't exist
        """
        event = TrackingEvent.query.get(event_id)
        if not event:
            raise NotFoundError(f"Tracking event with id {event_id} not found")

        return event

    def get_events_for_email(self, email_id, event_type=None):
        """
        Get all tracking events for an email

        Args:
            email_id: Email ID
            event_type: Filter by event type (optional: 'open', 'click', etc.)

        Returns:
            list: List of TrackingEvent instances

        Raises:
            NotFoundError: If email doesn't exist
        """
        # Verify email exists using email service
        email = self.email_service.get_email(email_id)

        query = TrackingEvent.query.filter_by(email_id=email.id)

        if event_type:
            query = query.filter_by(event_type=event_type)

        return query.all()

    def get_events_for_campaign(self, campaign_id, event_type=None):
        """
        Get all tracking events for a campaign

        Args:
            campaign_id: Campaign ID
            event_type: Filter by event type (optional: 'open', 'click', etc.)

        Returns:
            list: List of TrackingEvent instances
        """
        # Join with Email to filter by campaign
        query = TrackingEvent.query.join(Email).filter(Email.campaign_id == campaign_id)

        if event_type:
            query = query.filter(TrackingEvent.event_type == event_type)

        return query.all()

    def parse_request_metadata(self, request):
        """
        Extract metadata from Flask request object

        Args:
            request: Flask request object

        Returns:
            dict: Metadata dictionary with ip_address, user_agent, location
        """
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')

        # Location could be extracted from IP using a service like GeoIP
        # For now, we'll leave it as None
        location = None

        return {
            'ip_address': ip_address,
            'user_agent': user_agent,
            'location': location
        }
