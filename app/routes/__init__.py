from .email import email_bp
from .campaign import campaign_bp
from .tracking import tracking_bp
from .analytics import analytics_bp
from .templates import template_bp

__all__ = ['email_bp', 'campaign_bp', 'tracking_bp', 'analytics_bp', 'template_bp']