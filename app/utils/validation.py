import re

def validate_email(email) -> bool:
    """
    Validate email address format

    Args:
        email: Email address string

    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(email, str) or not email:
        return False

    # Basic email regex pattern
    # Matches: user@domain.com, user.name@domain.co.uk, etc.
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    return re.match(email_regex, email) is not None


def validate_url(url) -> bool:
    """
    Validate URL format

    Args:
        url: URL string

    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(url, str) or not url:
        return False

    # Basic URL regex pattern
    url_regex = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'

    return re.match(url_regex, url) is not None

def validate_template(template) -> bool:
    return False