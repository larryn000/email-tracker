from datetime import datetime
from typing import Optional, Dict, Any
from app import db


class Email(db.Model):
    """Model for tracking sent emails"""
    __tablename__ = 'emails'

    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    recipient_email = db.Column(db.String(255), nullable=False)
    sender_email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500))
    body = db.Column(db.Text)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=True)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    events = db.relationship('TrackingEvent', backref='email', lazy='dynamic', cascade='all, delete-orphan')
    campaign = db.relationship('Campaign', back_populates='emails')
    template = db.relationship('Template', back_populates='emails')

    def to_dict(self) -> Dict[str, Any]:
        """Convert email to dictionary"""
        return {
            'id': self.id,
            'tracking_id': self.tracking_id,
            'recipient_email': self.recipient_email,
            'sender_email': self.sender_email,
            'subject': self.subject,
            'campaign_id': self.campaign_id,
            'template_id': self.template_id,
            'campaign_name': self.campaign.name if self.campaign else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_opens': self.events.filter_by(event_type='open').count(),
            'total_clicks': self.events.filter_by(event_type='click').count()
        }


class TrackingEvent(db.Model):
    """Model for tracking email events (opens, clicks, etc.)"""
    __tablename__ = 'tracking_events'

    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False)  # 'open', 'click', 'bounce', etc.

    # Event metadata
    ip_address = db.Column(db.String(45))  # IPv6 support
    user_agent = db.Column(db.String(500))
    location = db.Column(db.String(255))  # City, Country
    device_type = db.Column(db.String(50))  # desktop, mobile, tablet

    # Click-specific data
    clicked_url = db.Column(db.String(2048))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert tracking event to dictionary"""
        return {
            'id': self.id,
            'email_id': self.email_id,
            'event_type': self.event_type,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'location': self.location,
            'device_type': self.device_type,
            'clicked_url': self.clicked_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Campaign(db.Model):
    """Model for grouping emails into campaigns"""
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(255))
    status = db.Column(db.String(50), default='draft')  # draft, active, completed, paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    emails = db.relationship('Email', back_populates='campaign', lazy='dynamic')

    def to_dict(self) -> Dict[str, Any]:
        """Convert campaign to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_emails': self.emails.count()
        }

class Template(db.Model):
    __tablename__ = 'templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    emails = db.relationship('Email', back_populates='template')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'body': self.body,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }



