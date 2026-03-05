"""
HireMate AI - Main Application Entry Point
FastAPI backend with production-ready features:
- Async processing
- Rate limiting
- CORS configuration
- Comprehensive error handling
- Structured logging

Features:
- Resume Analysis (match score, ATS scoring)
- AI Resume Generation (5 unique templates)
- Interview Questions Generator
- Skills Gap Analysis
- Resume Comparison Tool
"""
import logging
import os
import re
from contextlib import asynccontextmanager
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form, Request, status
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import ValidationError

from config import settings
from exceptions import (
    HireMateException,
    InvalidFileTypeException,
    FileSizeException,
    EmptyFileException,
    AIGenerationException,
    InvalidJobDescriptionException
)
from models import (
    AnalyzeResponse, HealthResponse, ErrorResponse,
    ResumeGenerateRequest, ResumeGenerateResponse,
    InterviewQuestionsRequest, InterviewQuestionsResponse,
    SkillsGapAnalysisRequest, SkillsGapAnalysisResponse,
    ResumeComparisonRequest, ResumeComparisonResponse
)
from pdf_utils import extract_text_from_pdf_safe
from skill_engine import calculate_match_score
from gemini_service import (
    generate_ai_content_async,
    generate_interview_questions_async,
    generate_skills_gap_analysis_async,
    generate_resume_comparison_async
)
from resume_generator import (
    generate_resume, ResumeTemplate, ResumeData, 
    parse_resume_from_text, convert_photo_to_base64
)

# Configure logger
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info("Application initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiter to app state
app.state.limiter = limiter


def calculate_ats_score(resume_text: str, job_description: str) -> float:
    """
    Calculate ATS (Applicant Tracking System) compatibility score.
    
    Args:
        resume_text: Resume content
        job_description: Job description
    
    Returns:
        ATS score (0-100)
    """
    score = 50.0  # Base score
    
    resume_lower = resume_text.lower()
    job_lower = job_description.lower()
    
    # Check for common sections (15 points)
    sections = ['experience', 'education', 'skills', 'summary', 'objective']
    found_sections = sum(1 for s in sections if s in resume_lower)
    score += (found_sections / len(sections)) * 15
    
    # Check for action verbs (10 points)
    action_verbs = ['led', 'managed', 'developed', 'created', 'implemented', 'achieved', 'designed', 'built']
    found_verbs = sum(1 for v in action_verbs if v in resume_lower)
    score += min(10, found_verbs * 2)
    
    # Check for quantifiable metrics (10 points)
    metrics = ['percent', '%', 'increased', 'reduced', 'saved', '$', 'million', 'thousand']
    found_metrics = sum(1 for m in metrics if m in resume_lower)
    score += min(10, found_metrics * 2)
    
    # Keyword matching (15 points)
    job_words = set(re.findall(r'\b[a-z]{3,}\b', job_lower))
    resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_lower))
    common_words = job_words.intersection(resume_words)
    if job_words:
        keyword_score = (len(common_words) / len(job_words)) * 15
        score += keyword_score
    
    return min(100.0, round(score, 1))


def generate_resume_tips(missing_skills: List[str], ats_score: float) -> List[str]:
    """
    Generate resume improvement tips.
    
    Args:
        missing_skills: List of missing skills
        ats_score: Current ATS score
    
    Returns:
        List of tips
    """
    tips = []
    
    if ats_score < 70:
        tips.append("Add more quantifiable achievements (e.g., 'increased sales by 25%')")
        tips.append("Include relevant keywords from the job description")
    
    if len(missing_skills) > 0:
        tips.append(f"Consider highlighting these skills: {', '.join(missing_skills[:3])}")
    
    if ats_score < 50:
        tips.append("Add a professional summary at the top of your resume")
        tips.append("Include standard sections: Experience, Education, Skills")
    
    tips.append("Use action verbs to describe your accomplishments")
    tips.append("Keep your resume format clean and ATS-friendly")
    tips.append("Tailor your resume for each job application")
    
    return tips


def generate_fallback_content(resume_text: str, job_description: str, missing_skills: List[str]) -> tuple:
    """
    Generate summary and cover letter using templates when AI is unavailable.
    
    Args:
        resume_text: Resume content
        job_description: Job description
        missing_skills: List of missing skills
    
    Returns:
        Tuple of (summary, cover_letter)
    """
    # Extract key info from job description
    job_lines = job_description.split('\n')
    job_title = "Professional"
    for line in job_lines[:3]:
        if len(line.strip()) > 5:
            job_title = line.strip()[:50]
            break
    
    # Extract skills mentioned in job
    job_words = set(re.findall(r'\b[a-z]{3,}\b', job_description.lower()))
    resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_text.lower()))
    matched = job_words.intersection(resume_words)
    
    # Generate summary
    summary = f"""Experienced {job_title} with a proven track record of delivering results.
Demonstrated expertise in {', '.join(list(matched)[:5]) if matched else 'various technologies'}.
Strong background in implementing strategic initiatives and driving operational excellence.
Quick learner with excellent problem-solving abilities and communication skills."""
    
    # Generate cover letter
    skills_str = ', '.join(list(matched)[:5]) if matched else 'relevant technical skills'
    missing_str = ', '.join(missing_skills[:3]) if missing_skills else 'additional skills'
    
    cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at your organization. With my background in {skills_str}, I am confident that I would be a valuable addition to your team.

In my career, I have demonstrated the ability to deliver results and drive success. My experience aligns well with your requirements, particularly in {skills_str}. While I notice you are looking for candidates with experience in {missing_str}, I am eager to learn and develop these skills quickly.

I am excited about the opportunity to contribute to your organization and would welcome the chance to discuss how my background and skills would benefit your team.

Thank you for considering my application. I look forward to hearing from you soon.

Best regards,
[Your Name]"""
    
    return summary, cover_letter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    logger.warning(f"Rate limit exceeded for {request.client.host}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "RateLimitExceeded",
            "message": "Too many requests. Please try again later.",
            "details": {"retry_after": str(exc.detail)}
        }
    )


@app.exception_handler(HireMateException)
async def hiremate_exception_handler(request: Request, exc: HireMateException):
    """Handle custom HireMate exceptions."""
    logger.error(f"HireMate exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message
        }
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Invalid input data",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - serves the frontend."""
    return FileResponse("index.html")


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        message="HireMate AI is running"
    )


@app.post("/api/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def analyze_resume(
    request: Request,
    resume_file: UploadFile = File(..., description="PDF resume file"),
    job_description: str = Form(..., description="Job description text")
):
    """
    Analyze resume against job description.
    
    - **resume_file**: PDF file containing the resume
    - **job_description**: Text of the job description
    
    Returns:
        - match_score: Percentage of skill matching (0-100)
        - missing_skills: List of skills from job description not found in resume
        - improved_summary: AI-generated professional summary
        - cover_letter: AI-generated tailored cover letter
    """
    logger.info("Received analyze request")
    
    # Validate job description
    if not job_description or len(job_description.strip()) < settings.MIN_JOB_DESCRIPTION_LENGTH:
        logger.warning(f"Invalid job description: too short or empty")
        raise InvalidJobDescriptionException(
            f"Job description must be at least {settings.MIN_JOB_DESCRIPTION_LENGTH} characters"
        )
    
    if len(job_description) > settings.MAX_JOB_DESCRIPTION_LENGTH:
        logger.warning(f"Job description too long: {len(job_description)} chars")
        raise InvalidJobDescriptionException(
            f"Job description must not exceed {settings.MAX_JOB_DESCRIPTION_LENGTH} characters"
        )
    
    # Extract text from PDF
    try:
        resume_text = await extract_text_from_pdf_safe(resume_file, resume_file.filename)
    except (InvalidFileTypeException, FileSizeException, EmptyFileException) as e:
        logger.warning(f"PDF processing error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in PDF extraction: {str(e)}")
        raise EmptyFileException("Failed to process the uploaded resume")
    
    if not resume_text or not resume_text.strip():
        logger.warning("Empty resume text extracted")
        raise EmptyFileException("Could not extract text from the resume")
    
    # Calculate match score
    try:
        score, missing_skills = calculate_match_score(resume_text, job_description)
        logger.info(f"Match score calculated: {score}%")
    except Exception as e:
        logger.error(f"Error calculating match score: {str(e)}")
        raise HireMateException("Failed to calculate match score", status_code=500)
    
    # Calculate ATS score
    ats_score = calculate_ats_score(resume_text, job_description)
    logger.info(f"ATS score calculated: {ats_score}%")
    
    # Generate resume tips
    resume_tips = generate_resume_tips(missing_skills, ats_score)
    
    # Generate AI content
    try:
        logger.info("Starting AI content generation")
        ai_result = await generate_ai_content_async(resume_text, job_description)
        improved_summary = ai_result.get("improved_summary", "")
        cover_letter = ai_result.get("cover_letter", "")
        logger.info("AI content generated successfully")
    except AIGenerationException:
        # Use fallback template-based generation
        logger.info("Using fallback content generation")
        improved_summary, cover_letter = generate_fallback_content(resume_text, job_description, missing_skills)
    except Exception as e:
        logger.error(f"Error generating AI content: {str(e)}")
        # Use fallback template-based generation
        improved_summary, cover_letter = generate_fallback_content(resume_text, job_description, missing_skills)
    
    return AnalyzeResponse(
        match_score=score,
        ats_score=ats_score,
        matched_skills=[],  # Frontend derives this from missing skills
        missing_skills=missing_skills,
        improved_summary=improved_summary,
        cover_letter=cover_letter,
        resume_tips=resume_tips
    )


# ==================== NEW API ENDPOINTS ====================

@app.post("/api/resume/generate", response_model=ResumeGenerateResponse, tags=["Resume Generator"])
async def generate_resume_endpoint(request: ResumeGenerateRequest):
    """
    Generate a professional resume in 5 different template formats.
    
    Choose from:
    - Modern: Sleek design with colored accents
    - Classic: Traditional professional layout
    - Technical: Skills-focused for developers
    - Executive: Senior-level format
    - Entry-Level: Student-friendly format
    """
    logger.info(f"Generating resume with template: {request.template_id}")
    
    # Create ResumeData object
    resume_data = ResumeData(
        full_name=request.full_name,
        email=request.email,
        phone=request.phone,
        location=request.location,
        linkedin=request.linkedin,
        portfolio=request.portfolio,
        summary=request.summary,
        skills=request.skills,
        experience=[exp.model_dump() for exp in request.experience],
        education=[edu.model_dump() for edu in request.education],
        certifications=request.certifications,
        languages=request.languages
    )
    
    # Generate resume HTML
    html_content = generate_resume(request.template_id, resume_data, request.primary_color)
    
    # Get template info
    template_names = {
        "modern": "Modern",
        "classic": "Classic",
        "technical": "Technical",
        "executive": "Executive",
        "entry": "Entry-Level"
    }
    
    return ResumeGenerateResponse(
        template_id=request.template_id,
        template_name=template_names.get(request.template_id, "Modern"),
        html_content=html_content,
        available_templates=[
            {"id": "modern", "name": "Modern", "description": "Sleek design with colored accents"},
            {"id": "classic", "name": "Classic", "description": "Traditional professional layout"},
            {"id": "technical", "name": "Technical", "description": "Skills-focused for developers"},
            {"id": "executive", "name": "Executive", "description": "Senior-level format"},
            {"id": "entry", "name": "Entry-Level", "description": "Student-friendly format"}
        ],
        industries=[
            {"id": "tech", "name": "Technology"},
            {"id": "finance", "name": "Finance"},
            {"id": "healthcare", "name": "Healthcare"},
            {"id": "marketing", "name": "Marketing"},
            {"id": "engineering", "name": "Engineering"},
            {"id": "general", "name": "General"}
        ]
    )


@app.get("/api/resume/templates", tags=["Resume Generator"])
async def get_resume_templates():
    """Get all available resume templates."""
    return {
        "templates": [
            {"id": "modern", "name": "Modern", "description": "Sleek design with colored accents, ideal for tech and creative roles"},
            {"id": "classic", "name": "Classic", "description": "Traditional professional layout, perfect for corporate positions"},
            {"id": "technical", "name": "Technical", "description": "Skills-focused layout, best for developers and IT professionals"},
            {"id": "executive", "name": "Executive", "description": "Senior-level format emphasizing leadership and achievements"},
            {"id": "entry", "name": "Entry-Level", "description": "Student-friendly format highlighting education and internships"}
        ],
        "industries": [
            {"id": "tech", "name": "Technology"},
            {"id": "finance", "name": "Finance"},
            {"id": "healthcare", "name": "Healthcare"},
            {"id": "marketing", "name": "Marketing"},
            {"id": "engineering", "name": "Engineering"},
            {"id": "general", "name": "General"}
        ]
    }


@app.post("/api/interview/questions", tags=["Interview"])
async def generate_interview_questions(request: InterviewQuestionsRequest):
    """
    Generate personalized interview questions based on resume and job description.
    
    Returns questions categorized as:
    - Technical: Job-specific technical questions
    - Behavioral: Situational and past experience questions
    - Situational: Hypothetical scenario questions
    """
    logger.info("Generating interview questions")
    
    try:
        result = await generate_interview_questions_async(
            request.resume_text,
            request.job_description,
            request.num_questions,
            request.question_types
        )
        return result
    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}")
        raise AIGenerationException("Failed to generate interview questions")


@app.post("/api/skills/gap-analysis", tags=["Skills"])
async def skills_gap_analysis(request: SkillsGapAnalysisRequest):
    """
    Analyze skills gap between resume and job description.
    
    Returns:
    - Matched and missing skills
    - Learning resources for missing skills
    - Priority recommendations
    """
    logger.info("Performing skills gap analysis")
    
    try:
        result = await generate_skills_gap_analysis_async(
            request.resume_text,
            request.job_description
        )
        return result
    except Exception as e:
        logger.error(f"Error in skills gap analysis: {str(e)}")
        raise AIGenerationException("Failed to analyze skills gap")


@app.post("/api/resume/compare", tags=["Resume"])
async def compare_resumes(request: ResumeComparisonRequest):
    """
    Compare user's resume against ideal resume for the job.
    
    Returns:
    - Overall score and ATS score
    - Category-by-category comparison
    - Keyword analysis
    - Improvement suggestions
    """
    logger.info("Comparing resume to ideal")
    
    try:
        result = await generate_resume_comparison_async(
            request.user_resume_text,
            request.job_description
        )
        return result
    except Exception as e:
        logger.error(f"Error comparing resumes: {str(e)}")
        raise AIGenerationException("Failed to compare resumes")


@app.post("/api/resume/parse", tags=["Resume"])
async def parse_resume(
    resume_file: UploadFile = File(None, description="PDF resume file (optional)")
):
    """
    Parse existing PDF resume and extract structured data.
    """
    logger.info("Parsing resume")
    
    resume_text = ""
    
    if resume_file:
        try:
            resume_text = await extract_text_from_pdf_safe(resume_file, resume_file.filename)
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
    
    # Parse the text into structured data
    parsed_data = parse_resume_from_text(resume_text)
    
    return {
        "full_name": parsed_data.full_name,
        "email": parsed_data.email,
        "phone": parsed_data.phone,
        "location": parsed_data.location,
        "linkedin": parsed_data.linkedin,
        "summary": parsed_data.summary,
        "skills": parsed_data.skills,
        "experience": parsed_data.experience,
        "education": parsed_data.education
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

