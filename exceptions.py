"""
Custom exceptions for HireMate AI application.
"""
from fastapi import HTTPException, status


class HireMateException(Exception):
    """Base exception for HireMate AI."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidFileTypeException(HireMateException):
    """Raised when uploaded file is not a valid PDF."""
    def __init__(self, message: str = "Only PDF files are allowed"):
        super().__init__(message, status_code=400)


class FileSizeException(HireMateException):
    """Raised when uploaded file exceeds size limit."""
    def __init__(self, message: str = "File size exceeds the maximum limit of 5MB"):
        super().__init__(message, status_code=400)


class EmptyFileException(HireMateException):
    """Raised when uploaded PDF is empty or cannot be read."""
    def __init__(self, message: str = "The uploaded PDF is empty or cannot be read"):
        super().__init__(message, status_code=400)


class AIGenerationException(HireMateException):
    """Raised when AI content generation fails."""
    def __init__(self, message: str = "Failed to generate AI content"):
        super().__init__(message, status_code=500)


class InvalidJobDescriptionException(HireMateException):
    """Raised when job description is invalid or too short."""
    def __init__(self, message: str = "Job description is required and must be at least 10 characters"):
        super().__init__(message, status_code=400)


def hiremate_exception_handler(request, exc: HireMateException):
    """Handler for HireMate custom exceptions."""
    raise HTTPException(
        status_code=exc.status_code,
        detail=exc.message
    )

