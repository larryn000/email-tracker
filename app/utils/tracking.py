from uuid import uuid4


def generate_tracking_id():
    """
    Generate a unique tracking ID for emails
    Returns a UUID4 string without dashes
    """
    return uuid4().hex


def create_tracking_pixel():
    """
    Create a 1x1 transparent PNG pixel for email tracking
    Returns bytes of the PNG image
    """
    # 1x1 transparent PNG in bytes
    # This is the smallest possible valid PNG file
    transparent_pixel = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
        b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return transparent_pixel