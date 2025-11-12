from typing import List, Tuple
from app import db
from app.models import Email, Campaign
from app.utils import validate_email, generate_tracking_id
from app.exceptions import ValidationError, NotFoundError

class EmailService:
    def __init__(self, db_session=None):
        self._db_session = db_session

    @property
    def db(self):
        """Lazy database session property - only accesses db.session when used"""
        return self._db_session if self._db_session is not None else db.session

    def create_email(self, recipient_email, sender_email, subject=None, body=None, campaign_id=None):
        if not validate_email(recipient_email):
            raise ValidationError(f"Incorrect Recipient Email: {recipient_email}")
        
        if not validate_email(sender_email):
            raise ValidationError(f"Incorrect Sender Email: {sender_email}")
        
        if campaign_id is not None:
            campaign = Campaign.query.get(campaign_id)
            if not campaign:
                raise NotFoundError(f"Campaign with id {campaign_id} not found")
            
        tracking_id = generate_tracking_id()

        email = Email(
            tracking_id=tracking_id,
            recipient_email=recipient_email,
            sender_email=sender_email,
            subject=subject,
            body=body,
            campaign_id=campaign_id
        )

        self.db.add(email)
        self.db.commit()

        return email


    def get_email(self, email_id):
        email = Email.query.get(email_id)

        if not email:
            raise NotFoundError(f"Email not found: {email_id}")
    
        return email

    def get_email_by_tracking_id(self, tracking_id):
        email = Email.query.filter_by(tracking_id=tracking_id).first()

        if not email:
            raise NotFoundError(f"Tracking Event not found: {tracking_id}")
        
        return email

        
    def list_emails(self, campaign_id=None, recipient_email=None, sender_email=None, limit=50, offset=0) -> Tuple[List[Email], int]:
        """
        List emails with optional filters

        Returns:
            tuple: (emails, total_count) where emails is the paginated list and total_count is the total matching records
        """
        query = Email.query
        if campaign_id is not None:
            query = query.filter_by(campaign_id=campaign_id)
        if recipient_email is not None:
            query = query.filter_by(recipient_email=recipient_email)
        if sender_email is not None:
            query = query.filter_by(sender_email=sender_email)

        # Get total count before applying limit/offset
        total_count = query.count()

        # Apply pagination
        emails = query.limit(limit).offset(offset).all()

        return emails, total_count

    def update_email(self, email_id, subject=None, body=None, campaign_id=None):
        email = self.get_email(email_id)
        
        if campaign_id is not None:
            if not isinstance(campaign_id, int):
                raise ValidationError(f"Campaign ID is incorrect type: {campaign_id}")

            # TODO: use Campaign Service function
            campaign = Campaign.query.get(campaign_id)

            if not campaign:
                raise NotFoundError(f"Campaign not found: {campaign_id}")
            
            email.campaign_id = campaign_id

        if subject is not None:
            email.subject = subject

        if body is not None:
            email.body = body

        self.db.commit()
        
        return email

    def delete_email(self, email_id):
        email = self.get_email(email_id)

        self.db.delete(email)
        self.db.commit()

    def get_email_events(self, email_id, event_type):
        email = self.get_email(email_id)

        if event_type:
            return email.events.filter_by(event_type=event_type).all()

        return email.events.all()

    