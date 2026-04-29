class AttendanceBaseException(Exception):
    """Base exception for all attendance system errors."""
    pass


# ----------------------------
# Parsing / OCR errors
# ----------------------------

class OCRProcessingError(AttendanceBaseException):
    """Raised when OCR fails or returns invalid text."""
    pass


class ParsingError(AttendanceBaseException):
    """Raised when a row or report cannot be parsed."""
    pass


# ----------------------------
# Strategy / Transformation
# ----------------------------

class TransformationError(AttendanceBaseException):
    """
    Raised when a transformation strategy or decorator fails
    (e.g. invalid time after variation, rule violation).
    """
    pass


class UnknownReportTypeError(AttendanceBaseException):
    """Raised when classifier returns an unsupported report type."""
    pass


# ----------------------------
# Validation errors
# ----------------------------

class ValidationError(AttendanceBaseException):
    """Raised when data violates business rules (e.g. exit < entry)."""
    pass


class TimeBoundaryError(ValidationError):
    """Raised when time is outside allowed min/max boundaries."""
    pass


class BreakValidationError(ValidationError):
    """Raised when break time is invalid or out of range."""
    pass


# ----------------------------
# System / Infrastructure
# ----------------------------

class PDFGenerationError(AttendanceBaseException):
    """Raised when PDF rendering fails."""
    pass


class ConfigurationError(AttendanceBaseException):
    """Raised when system configuration is missing or invalid."""
    pass