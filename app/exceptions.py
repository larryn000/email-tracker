"""
Custom exceptions for the email tracker application
"""


class EmailTrackerException(Exception):
    """Base exception for email tracker"""
    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field
        self.status_code = 500

class ValidationError(EmailTrackerException):
    """Raised when validation fails"""
    def __init__(self, message, field=None):
        super().__init__(message, field)
        self.field = field
        self.status_code = 400
    pass


class NotFoundError(EmailTrackerException):
    """Raised when a resource is not found"""
    def __init__(self, message, field=None):
        super().__init__(message, field)
        self.field = field
        self.status_code = 404


class DatabaseError(EmailTrackerException):
    """Raised when a database operation fails"""
    def __init__(self, message, field=None):
        super().__init__(message, field)
        self.field = field
        self.status_code = 400

