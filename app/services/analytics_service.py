from app import db
from app.models import Email, Campaign, TrackingEvent
from app.exceptions import NotFoundError
from app.services.email_service import EmailService
from app.services.campaign_service import CampaignService
from sqlalchemy import func


class AnalyticsService:
    """Service for analytics and statistics"""

    def __init__(self, db_session=None, email_service=None, campaign_service=None):
        """
        Initialize AnalyticsService

        Args:
            db_session: Database session (defaults to db.session)
            email_service: EmailService instance (optional)
            campaign_service: CampaignService instance (optional)
        """
        self._db_session = db_session
        self._email_service = email_service
        self._campaign_service = campaign_service

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

    @property
    def campaign_service(self):
        """Lazy campaign service property"""
        if self._campaign_service is None:
            self._campaign_service = CampaignService(self._db_session)
        return self._campaign_service

    def get_email_stats(self, email_id):
        """
        Get statistics for a specific email

        Args:
            email_id: Email ID

        Returns:
            dict: Statistics including total_opens, total_clicks, unique_opens, etc.

        Raises:
            NotFoundError: If email doesn't exist
        """
        email = self.email_service.get_email(email_id)

        # Get all events for this email
        events = email.events.all()

        # Count total opens and clicks
        # sum() iterates through events and adds 1 for each matching event
        total_opens = sum(1 for e in events if e.event_type == 'open')
        total_clicks = sum(1 for e in events if e.event_type == 'click')

        # Count unique opens/clicks by IP address
        # set() automatically deduplicates - same IP counted only once
        unique_open_ips = set(e.ip_address for e in events if e.event_type == 'open' and e.ip_address)
        unique_click_ips = set(e.ip_address for e in events if e.event_type == 'click' and e.ip_address)

        unique_opens = len(unique_open_ips)
        unique_clicks = len(unique_click_ips)

        # Device breakdown - count events per device type
        device_breakdown = {}
        for event in events:
            if event.device_type:
                device_breakdown[event.device_type] = device_breakdown.get(event.device_type, 0) + 1

        # Get timestamp of first and last open
        first_open = next((e.created_at for e in events if e.event_type == 'open'), None)
        last_open = None
        for event in reversed(events):
            if event.event_type == 'open':
                last_open = event.created_at
                break

        # Get timestamp of most recent click
        last_click = None
        for event in reversed(events):
            if event.event_type == 'click':
                last_click = event.created_at
                break

        return {
            'email_id': email_id,
            'total_opens': total_opens,
            'total_clicks': total_clicks,
            'unique_opens': unique_opens,
            'unique_clicks': unique_clicks,
            'device_breakdown': device_breakdown,
            'first_opened_at': first_open.isoformat() if first_open else None,
            'last_opened_at': last_open.isoformat() if last_open else None,
            'last_click_at': last_click.isoformat() if last_click else None
        }

    def get_campaign_stats(self, campaign_id):
        """
        Get statistics for a campaign

        Args:
            campaign_id: Campaign ID

        Returns:
            dict: Comprehensive campaign statistics

        Raises:
            NotFoundError: If campaign doesn't exist
        """
        campaign = self.campaign_service.get_campaign(campaign_id)

        # Get all emails in campaign
        emails = campaign.emails.all()
        total_emails = len(emails)

        if total_emails == 0:
            return {
                'campaign_id': campaign_id,
                'campaign_name': campaign.name,
                'total_emails': 0,
                'total_opens': 0,
                'total_clicks': 0,
                'unique_opens': 0,
                'unique_clicks': 0,
                'open_rate': 0,
                'click_rate': 0,
                'click_through_rate': 0,
                'device_breakdown': {}
            }

        # Aggregate stats across all emails
        total_opens = 0
        total_clicks = 0
        emails_with_opens = set()  # Set to track which emails were opened
        emails_with_clicks = set()  # Set to track which emails were clicked
        device_breakdown = {}

        for email in emails:
            events = email.events.all()

            email_has_open = False
            email_has_click = False

            for event in events:
                if event.event_type == 'open':
                    total_opens += 1
                    email_has_open = True
                elif event.event_type == 'click':
                    total_clicks += 1
                    email_has_click = True

                # Track device breakdown
                if event.device_type:
                    device_breakdown[event.device_type] = device_breakdown.get(event.device_type, 0) + 1

            # Track unique emails (recipients) that opened/clicked
            if email_has_open:
                emails_with_opens.add(email.id)
            if email_has_click:
                emails_with_clicks.add(email.id)

        unique_opens = len(emails_with_opens)
        unique_clicks = len(emails_with_clicks)

        # Calculate rates as percentages
        open_rate = (unique_opens / total_emails * 100) if total_emails > 0 else 0
        click_rate = (unique_clicks / total_emails * 100) if total_emails > 0 else 0
        click_through_rate = (unique_clicks / unique_opens * 100) if unique_opens > 0 else 0

        return {
            'campaign_id': campaign_id,
            'campaign_name': campaign.name,
            'total_emails': total_emails,
            'total_opens': total_opens,
            'total_clicks': total_clicks,
            'unique_opens': unique_opens,
            'unique_clicks': unique_clicks,
            'open_rate': round(open_rate, 2),
            'click_rate': round(click_rate, 2),
            'click_through_rate': round(click_through_rate, 2),
            'device_breakdown': device_breakdown
        }

    def get_global_stats(self):
        """
        Get global statistics across all campaigns and emails

        Returns:
            dict: Global statistics
        """
        total_campaigns = Campaign.query.count()
        total_emails = Email.query.count()
        total_events = TrackingEvent.query.count()
        total_opens = TrackingEvent.query.filter_by(event_type='open').count()
        total_clicks = TrackingEvent.query.filter_by(event_type='click').count()

        # Count unique emails that have opens/clicks
        unique_opens = self.db.query(TrackingEvent.email_id).filter(
            TrackingEvent.event_type == 'open'
        ).distinct().count()

        unique_clicks = self.db.query(TrackingEvent.email_id).filter(
            TrackingEvent.event_type == 'click'
        ).distinct().count()

        # Device breakdown across all events using SQL GROUP BY
        device_breakdown = {}
        devices = self.db.query(
            TrackingEvent.device_type,
            func.count(TrackingEvent.id)
        ).filter(
            TrackingEvent.device_type.isnot(None)
        ).group_by(TrackingEvent.device_type).all()

        for device_type, count in devices:
            device_breakdown[device_type] = count

        return {
            'total_campaigns': total_campaigns,
            'total_emails': total_emails,
            'total_events': total_events,
            'total_opens': total_opens,
            'total_clicks': total_clicks,
            'unique_opens': unique_opens,
            'unique_clicks': unique_clicks,
            'open_rate': (unique_opens / total_emails * 100) if total_emails > 0 else 0,
            'click_rate': (unique_clicks / total_emails * 100) if total_emails > 0 else 0,
            'device_breakdown': device_breakdown
        }

    def get_top_performing_campaigns(self, limit=10, metric='open_rate'):
        """
        Get top performing campaigns

        Args:
            limit: Number of campaigns to return (default: 10)
            metric: Metric to sort by ('open_rate', 'click_rate', 'total_opens', 'total_clicks')

        Returns:
            list: List of campaign stats sorted by metric
        """
        campaigns = Campaign.query.all()
        campaign_stats = []

        for campaign in campaigns:
            stats = self.get_campaign_stats(campaign.id)
            campaign_stats.append(stats)

        # Sort by metric (descending order)
        valid_metrics = ['open_rate', 'click_rate', 'total_opens', 'total_clicks', 'click_through_rate']
        if metric not in valid_metrics:
            metric = 'open_rate'

        sorted_campaigns = sorted(campaign_stats, key=lambda x: x.get(metric, 0), reverse=True)

        return sorted_campaigns[:limit]
