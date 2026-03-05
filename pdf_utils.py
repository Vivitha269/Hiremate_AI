"""
PDF text extraction utilities for HireMate AI.
Provides robust error handling and validation for PDF processing.
"""
import logging
import io
import PyPDF2
from typing import Optional
from exceptions import (
    EmptyFileException,
    InvalidFileTypeException,
    FileSizeException
)
from config import settings

# Configure logger
logger = logging.getLogger(__name__)


async def validate_pdf_file(file, filename: str) -> None:
    """
    Validate the uploaded PDF file.
    
    Args:
        file: Uploaded file object (async UploadFile)
        filename: Name of the file
    
    Raises:
        InvalidFileTypeException: If file is not a PDF
        FileSizeException: If file exceeds size limit
    """
    # Check file extension
    if not any(filename.lower().endswith(ext) for ext in settings.ALLOWED_EXTENSIONS):
        logger.warning(f"Invalid file type attempted: {filename}")
        raise InvalidFileTypeException(
            f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check content type if available
    content_type = getattr(file, 'content_type', None)
    if content_type and content_type not in settings.ALLOWED_CONTENT_TYPES:
        logger.warning(f"Invalid content type: {content_type}")
        raise InvalidFileTypeException(
            f"Invalid content type. Allowed: {', '.join(settings.ALLOWED_CONTENT_TYPES)}"
        )
    
    # Check file size (read content to get size, then reset)
    try:
        # Read file content to determine size
        await file.seek(0)
        file_content = await file.read()
        file_size = len(file_content)
        await file.seek(0)  # Reset to beginning
        
        if file_size > settings.MAX_FILE_SIZE_BYTES:
            logger.warning(f"File size exceeded: {file_size} bytes")
            raise FileSizeException(
                f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        if file_size == 0:
            logger.warning("Empty file uploaded")
            raise EmptyFileException("The uploaded file is empty")
            
    except (EmptyFileException, FileSizeException):
        raise
    except Exception as e:
        logger.error(f"Error validating file: {str(e)}")
        raise


async def extract_text_from_pdf(file) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file: UploadFile object (must be a valid PDF)
    
    Returns:
        Extracted text as string
    
    Raises:
        EmptyFileException: If PDF is empty or cannot be read
        InvalidFileTypeException: If file is not a valid PDF
    """
    try:
        # Read file content first (since UploadFile needs async read)
        await file.seek(0)
        file_content = await file.read()
        
        # Create a BytesIO object from the content for PyPDF2
        pdf_file = io.BytesIO(file_content)
        
        # Create PDF reader
        reader = PyPDF2.PdfReader(pdf_file)
        
        # Check if PDF has pages
        if len(reader.pages) == 0:
            logger.warning("PDF has no pages")
            raise EmptyFileException("The PDF file has no content pages")
        
        # Extract text from all pages
        text_parts = []
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                    logger.debug(f"Extracted text from page {page_num}")
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
                continue
        
        # Join all text
        full_text = "\n".join(text_parts)
        
        # Check if any text was extracted
        if not full_text.strip():
            logger.warning("No text could be extracted from PDF")
            raise EmptyFileException(
                "Could not extract any text from the PDF. "
                "The file may be scanned or image-based."
            )
        
        logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
        return full_text
        
    except EmptyFileException:
        raise
    except InvalidFileTypeException:
        raise
    except PyPDF2.errors.PdfReadError as e:
        logger.error(f"Invalid PDF format: {str(e)}")
        raise InvalidFileTypeException("The file is not a valid PDF document")
    except Exception as e:
        logger.error(f"Unexpected error extracting PDF text: {str(e)}")
        raise EmptyFileException(f"Failed to read PDF: {str(e)}")


async def extract_text_from_pdf_safe(file, filename: str = "document.pdf") -> Optional[str]:
    """
    Safe wrapper for PDF extraction with validation.
    
    Args:
        file: Uploaded file object
        filename: Name of the uploaded file
    
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        await validate_pdf_file(file, filename)
        return await extract_text_from_pdf(file)
    except (InvalidFileTypeException, FileSizeException, EmptyFileException) as e:
        logger.error(f"PDF validation/extraction failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in PDF processing: {str(e)}")
        raise EmptyFileException(f"Failed to process PDF: {str(e)}")

