from app import db
from app.models import Campaign
from app.exceptions import NotFoundError, ValidationError


class CampaignService:
    """Service for managing campaigns"""

    def __init__(self, db_session=None):
        """
        Initialize CampaignService

        Args:
            db_session: Database session (defaults to db.session)
        """
        self._db_session = db_session

    @property
    def db(self):
        """Lazy database session property - only accesses db.session when used"""
        return self._db_session if self._db_session is not None else db.session

    def create_campaign(self, name, description=None, created_by=None, status='draft'):
        """
        Create a new campaign

        Args:
            name: Campaign name (required)
            description: Campaign description (optional)
            created_by: Creator identifier (optional)
            status: Campaign status (default: 'draft')

        Returns:
            Campaign: Created campaign instance

        Raises:
            ValidationError: If name is missing or status is invalid
        """
        if not name or not isinstance(name, str) or not name.strip():
            raise ValidationError("Campaign name is required")

        # Validate status
        valid_statuses = ['draft', 'active', 'completed', 'paused']
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status: {status}. Must be one of {valid_statuses}")

        campaign = Campaign(
            name=name.strip(),
            description=description,
            created_by=created_by,
            status=status
        )

        self.db.add(campaign)
        self.db.commit()

        return campaign

    def get_campaign(self, campaign_id):
        """
        Get campaign by ID

        Args:
            campaign_id: Campaign ID

        Returns:
            Campaign: Campaign instance

        Raises:
            NotFoundError: If campaign doesn't exist
        """
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            raise NotFoundError(f"Campaign with id {campaign_id} not found")

        return campaign

    def list_campaigns(self, status=None, created_by=None, limit=50, offset=0):
        """
        List campaigns with filtering and pagination

        Args:
            status: Filter by status (optional)
            created_by: Filter by creator (optional)
            limit: Maximum number of results (default: 50)
            offset: Number of results to skip (default: 0)

        Returns:
            list: List of Campaign instances
        """
        query = Campaign.query

        # Apply filters
        if status:
            query = query.filter_by(status=status)

        if created_by:
            query = query.filter_by(created_by=created_by)

        # Apply pagination
        query = query.limit(limit).offset(offset)

        return query.all()

    def update_campaign(self, campaign_id, name=None, description=None, status=None, created_by=None):
        """
        Update campaign fields

        Args:
            campaign_id: Campaign ID
            name: New name (optional)
            description: New description (optional)
            status: New status (optional)
            created_by: New creator (optional)

        Returns:
            Campaign: Updated campaign instance

        Raises:
            NotFoundError: If campaign doesn't exist
            ValidationError: If status is invalid or name is empty
        """
        campaign = self.get_campaign(campaign_id)

        # Update fields if provided
        if name is not None:
            if not isinstance(name, str) or not name.strip():
                raise ValidationError("Campaign name cannot be empty")
            campaign.name = name.strip()

        if description is not None:
            campaign.description = description

        if status is not None:
            valid_statuses = ['draft', 'active', 'completed', 'paused']
            if status not in valid_statuses:
                raise ValidationError(f"Invalid status: {status}. Must be one of {valid_statuses}")
            campaign.status = status

        if created_by is not None:
            campaign.created_by = created_by

        self.db.commit()

        return campaign

    def delete_campaign(self, campaign_id):
        """
        Delete campaign

        Args:
            campaign_id: Campaign ID

        Raises:
            NotFoundError: If campaign doesn't exist
        """
        campaign = self.get_campaign(campaign_id)

        self.db.delete(campaign)
        self.db.commit()

    def get_campaign_stats(self, campaign_id):
        """
        Get statistics for a campaign

        Args:
            campaign_id: Campaign ID

        Returns:
            dict: Statistics including total_emails, total_opens, total_clicks

        Raises:
            NotFoundError: If campaign doesn't exist
        """
        campaign = self.get_campaign(campaign_id)

        # Count total emails
        total_emails = campaign.emails.count()

        # Count total opens and clicks across all emails
        total_opens = 0
        total_clicks = 0

        for email in campaign.emails:
            total_opens += email.events.filter_by(event_type='open').count()
            total_clicks += email.events.filter_by(event_type='click').count()

        return {
            'campaign_id': campaign_id,
            'total_emails': total_emails,
            'total_opens': total_opens,
            'total_clicks': total_clicks,
            'open_rate': total_opens / total_emails if total_emails > 0 else 0,
            'click_rate': total_clicks / total_emails if total_emails > 0 else 0
        }
