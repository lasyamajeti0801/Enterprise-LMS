"""Enterprise domain exceptions for the LMS application."""


class LMSException(Exception):
    """Base exception for all domain and application errors."""

    def __init__(self, message="An internal application error occurred.", code=500, payload=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.payload = payload or {}


class AuthenticationError(LMSException):
    """Raised when authentication credentials or tokens are invalid."""

    def __init__(self, message="Invalid authentication credentials.", payload=None):
        super().__init__(message=message, code=401, payload=payload)


class PermissionDeniedError(LMSException):
    """Raised when a user attempts an unauthorized action."""

    def __init__(self, message="You do not have permission to perform this action.", payload=None):
        super().__init__(message=message, code=403, payload=payload)


class ResourceNotFoundError(LMSException):
    """Raised when a requested entity does not exist."""

    def __init__(self, message="The requested resource was not found.", payload=None):
        super().__init__(message=message, code=404, payload=payload)


class ValidationError(LMSException):
    """Raised when request payload or business entity validation fails."""

    def __init__(self, message="Validation failed.", errors=None, payload=None):
        payload = payload or {}
        if errors:
            payload["errors"] = errors
        super().__init__(message=message, code=422, payload=payload)


class CourseNotFoundError(ResourceNotFoundError):
    """Raised when a specified course is not found."""

    def __init__(self, course_id=None):
        msg = f"Course with ID '{course_id}' was not found." if course_id else "Course not found."
        super().__init__(message=msg)


class EnrollmentError(LMSException):
    """Raised when course enrollment constraints are violated."""

    def __init__(self, message="Enrollment error.", payload=None):
        super().__init__(message=message, code=400, payload=payload)


class AssessmentError(LMSException):
    """Raised when quiz/exam rules or submission constraints are violated."""

    def __init__(self, message="Assessment error.", payload=None):
        super().__init__(message=message, code=400, payload=payload)


class CertificateIneligibleError(LMSException):
    """Raised when a student requests a certificate before meeting requirements."""

    def __init__(self, message="Student has not met all criteria for certificate issuance.", payload=None):
        super().__init__(message=message, code=400, payload=payload)
