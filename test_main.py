"""
Unit tests for HireMate AI application.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio

# Import modules to test
from pdf_utils import extract_text_from_pdf, validate_pdf_file
from skill_engine import extract_words
from skill_engine import calculate_match_score, get_resume_skills, extract_key_skills
from models import AnalyzeResponse, AnalyzeRequest
from exceptions import (
    InvalidFileTypeException,
    FileSizeException,
    EmptyFileException
)
from config import settings


class TestPdfUtils:
    """Tests for PDF utility functions."""
    
    def test_extract_words_basic(self):
        """Test basic word extraction."""
        text = "Python JavaScript React"
        result = extract_words(text)
        assert "python" in result
        assert "javascript" in result
        assert "react" in result
    
    def test_extract_words_removes_short(self):
        """Test that short words are removed."""
        text = "I am a developer in Python"
        result = extract_words(text)
        assert "i" not in result  # Too short (1 char)
        assert "python" in result
    
    def test_extract_words_handles_empty(self):
        """Test empty input handling."""
        result = extract_words("")
        assert result == set()
    
    def test_extract_words_handles_none(self):
        """Test None input handling."""
        result = extract_words(None)
        assert result == set()
    
    @pytest.mark.asyncio
    @patch('pdf_utils.PyPDF2.PdfReader')
    async def test_extract_text_from_pdf_success(self, mock_reader):
        """Test successful PDF text extraction."""
        # Mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test resume content"
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_reader.return_value = mock_reader_instance
        
        # Test - configure Mock to handle async file operations
        file = Mock()
        file.seek = AsyncMock(return_value=None)
        file.read = AsyncMock(return_value=b"fake pdf content")
        
        result = await extract_text_from_pdf(file)
        
        assert result == "Test resume content"
    
    @pytest.mark.asyncio
    @patch('pdf_utils.PyPDF2.PdfReader')
    async def test_extract_text_from_pdf_empty(self, mock_reader):
        """Test empty PDF handling."""
        mock_reader_instance = Mock()
        mock_reader_instance.pages = []
        mock_reader.return_value = mock_reader_instance
        
        # Configure Mock to handle async file operations
        file = Mock()
        file.seek = AsyncMock(return_value=None)
        file.read = AsyncMock(return_value=b"empty pdf")
        
        with pytest.raises(EmptyFileException):
            await extract_text_from_pdf(file)


class TestSkillEngine:
    """Tests for skill matching engine."""
    
    def test_calculate_match_score_perfect_match(self):
        """Test 100% match score."""
        resume = "Python JavaScript React"
        job_description = "We need Python JavaScript React developer"
        
        score, missing, matched = calculate_match_score(resume, job_description)
        
        assert score > 0
        assert isinstance(missing, list)
    
    def test_calculate_match_score_no_match(self):
        """Test 0% match score."""
        resume = "Python JavaScript"
        job_description = "Looking for Go Rust developer"
        
        score, missing, matched = calculate_match_score(resume, job_description)
        
        assert score >= 0
        assert isinstance(missing, list)
    
    def test_calculate_match_score_empty_resume(self):
        """Test empty resume handling - should return job skills as missing."""
        score, missing, matched = calculate_match_score("", "Python developer")
        
        assert score == 0.0
        assert len(missing) > 0  # Job skills are now returned as missing
        assert "python" in missing
    
    def test_calculate_match_score_empty_job(self):
        """Test empty job description handling."""
        score, missing, matched = calculate_match_score("Python developer", "")
        
        assert score == 0.0
        assert missing == []
    
    def test_extract_key_skills(self):
        """Test key skill extraction."""
        text = "I work with Python, JavaScript, React and AWS"
        skills = extract_key_skills(text)
        
        assert "python" in skills
        assert "javascript" in skills
        assert "aws" in skills
    
    def test_get_resume_skills(self):
        """Test resume skills extraction."""
        resume = "Python Java React AWS Docker"
        skills = get_resume_skills(resume)
        
        assert isinstance(skills, list)
        assert len(skills) > 0


class TestModels:
    """Tests for Pydantic models."""
    
    def test_analyze_response_valid(self):
        """Test valid response model."""
        response = AnalyzeResponse(
            match_score=75.5,
            missing_skills=["kubernetes", "docker"],
            improved_summary="Summary text",
            cover_letter="Cover letter text"
        )
        
        assert response.match_score == 75.5
        assert len(response.missing_skills) == 2
    
    def test_analyze_response_defaults(self):
        """Test response model defaults."""
        response = AnalyzeResponse(match_score=50.0)
        
        assert response.match_score == 50.0
        assert response.missing_skills == []
        assert response.improved_summary == ""
        assert response.cover_letter == ""
    
    def test_analyze_request_valid(self):
        """Test valid request model."""
        request = AnalyzeRequest(
            resume="Python developer with 5 years experience",
            job_description="Looking for Python developer"
        )
        
        assert request.resume is not None
        assert request.job_description is not None
    
    def test_analyze_request_empty_resume(self):
        """Test empty resume validation."""
        with pytest.raises(ValueError):
            AnalyzeRequest(resume="", job_description="Python developer")
    
    def test_analyze_request_short_job(self):
        """Test short job description validation."""
        with pytest.raises(ValueError):
            AnalyzeRequest(
                resume="Python developer",
                job_description="Short"
            )


class TestConfig:
    """Tests for configuration settings."""
    
    def test_settings_exist(self):
        """Test that settings are properly configured."""
        assert settings.MAX_FILE_SIZE_MB == 5
        assert settings.MAX_FILE_SIZE_BYTES == 5 * 1024 * 1024
        assert settings.MIN_JOB_DESCRIPTION_LENGTH == 10
        assert settings.RATE_LIMIT_PER_MINUTE == 10
        assert settings.GEMINI_MODEL == "gemini-2.0-flash"
    
    def test_allowed_extensions(self):
        """Test allowed file extensions."""
        assert ".pdf" in settings.ALLOWED_EXTENSIONS
        assert "application/pdf" in settings.ALLOWED_CONTENT_TYPES


class TestExceptions:
    """Tests for custom exceptions."""
    
    def test_invalid_file_type_exception(self):
        """Test InvalidFileTypeException."""
        exc = InvalidFileTypeException()
        
        assert exc.status_code == 400
        assert "PDF" in exc.message
    
    def test_file_size_exception(self):
        """Test FileSizeException."""
        exc = FileSizeException()
        
        assert exc.status_code == 400
        assert "5MB" in exc.message
    
    def test_empty_file_exception(self):
        """Test EmptyFileException."""
        exc = EmptyFileException()
        
        assert exc.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

