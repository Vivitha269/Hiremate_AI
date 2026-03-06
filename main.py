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
import asyncio
import random
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, Request, status
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import ValidationError
from google.generativeai import GenerationConfig

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
    ResumeComparisonRequest, ResumeComparisonResponse,
    UnifiedAnalysisRequest, UnifiedAnalysisResponse, ResumeModificationSuggestion,
    ResumeParseResponse
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
    Generate summary and cover letter using intelligent templates when AI is unavailable.
    
    Args:
        resume_text: Resume content
        job_description: Job description
        missing_skills: List of missing skills
    
    Returns:
        Tuple of (summary, cover_letter)
    """
    # Extract job title from job description
    job_lines = job_description.split('\n')
    job_title = "Professional"
    company_name = "your organization"
    
    for line in job_lines[:5]:
        line = line.strip()
        # Look for job title patterns
        if len(line) > 5 and len(line) < 80:
            # Check if it looks like a job title (contains common words)
            lower_line = line.lower()
            if any(word in lower_line for word in ['engineer', 'developer', 'manager', 'analyst', 'designer', 'specialist', 'coordinator', 'consultant', 'assistant', 'associate']):
                job_title = line.strip()[:60]
                break
            elif not job_title or job_title == "Professional":
                job_title = line.strip()[:60]
    
    # Extract key requirements from job description
    job_lower = job_description.lower()
    
    # Extract skills from job description (including special characters)
    job_words = set(re.findall(r'\b[a-z+#\.]{3,}\b', job_lower))
    resume_words = set(re.findall(r'\b[a-z+#\.]{3,}\b', resume_text.lower()))
    matched = job_words.intersection(resume_words)
    
    # Generate personalized summary based on resume content
    resume_lower = resume_text.lower()
    
    # Detect candidate's background - years of experience
    experience_years = 0
    if 'year' in resume_lower:
        year_match = re.search(r'(\d+)\+?\s*year', resume_lower)
        if year_match:
            experience_years = int(year_match.group(1))
    
    # Detect key skills from resume
    common_skills = ['python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular', 'node', 'django', 
                     'flask', 'spring', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'linux', 'database',
                     'machine learning', 'data analysis', 'project management', 'communication', 'leadership',
                     'marketing', 'sales', 'design', 'testing', 'agile', 'scrum']
    
    found_skills = [s for s in common_skills if s in resume_lower]
    
    # Build personalized summary with multiple options
    summary_templates = [
        f"Results-driven professional with {experience_years}+ years of experience in {', '.join(found_skills[:3]) if found_skills else 'various domains'}. Demonstrated expertise in delivering high-impact projects and driving organizational success.",
        f"Detail-oriented professional with strong background in {', '.join(found_skills[:3]) if found_skills else 'technical and business domains'}. Proven track record of achieving measurable results and exceeding performance targets.",
        f"Dynamic professional combining technical proficiency in {', '.join(found_skills[:2]) if found_skills else 'multiple technologies'} with excellent communication and problem-solving abilities. Committed to continuous improvement and professional growth.",
        f"Accomplished professional with extensive experience in {', '.join(found_skills[:3]) if found_skills else 'delivering value through innovative solutions'}. Skilled at adapting to new challenges and contributing to team success."
    ]
    
    # Add job-specific details if we have matched skills
    if matched:
        summary_templates.append(
            f"Professional with demonstrated expertise in {', '.join(list(matched)[:4]) if matched else 'relevant skills'}. "
            f"Proven ability to leverage technical and interpersonal skills to drive business outcomes."
        )
    
    summary = random.choice(summary_templates)
    
    # Add specific achievements if available in resume
    achievement_keywords = ['achieved', 'increased', 'reduced', 'improved', 'led', 'managed', 'developed', 'created', 'implemented']
    achievements = []
    for keyword in achievement_keywords:
        for sentence in resume_text.split('.'):
            if keyword in sentence.lower() and len(sentence.strip()) > 20:
                achievements.append(sentence.strip())
                if len(achievements) >= 2:
                    break
        if len(achievements) >= 2:
            break
    
    if achievements:
        summary += f" Notable achievements include {achievements[0][:100]}."
    
    # Generate cover letter
    skills_str = ', '.join(list(matched)[:4]) if matched else 'relevant technical and professional skills'
    missing_str = ', '.join(missing_skills[:3]) if missing_skills else 'additional competencies'
    
    # Extract company name if mentioned in job description
    company_patterns = ['at ', 'with ', 'joining ']
    for pattern in company_patterns:
        for line in job_lines:
            if pattern in line.lower():
                parts = line.lower().split(pattern)
                if len(parts) > 1:
                    company_candidate = parts[1].strip()[:30]
                    if company_candidate and len(company_candidate) > 2:
                        company_name = company_candidate
                        break
    
    # Build personalized cover letter
    cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With my background in {skills_str}, I am confident that I would be a valuable addition to your team.

"""
    
    # Add personalized paragraph based on matched skills
    if matched:
        matched_phrase = ' and '.join(list(matched)[:2]) if matched else 'the opportunity to apply my skills in a new environment'
        cover_letter += f"In my career, I have developed strong expertise in {skills_str}. My experience has equipped me with the skills necessary to contribute effectively to your organization. I am particularly drawn to this position because {matched_phrase} aligns perfectly with my professional background.\n\n"
    else:
        cover_letter += f"In my career, I have developed a versatile skill set that enables me to adapt quickly to new challenges. I am excited about the opportunity to bring my abilities to your organization and contribute to your team's success.\n\n"
    
    # Add paragraph about missing skills/learning attitude
    if missing_skills:
        cover_letter += f"I am aware that this role requires skills in {missing_str}, and I am eager to develop these competencies further. I have a proven track record of quickly learning new skills and technologies, and I am committed to continuous professional development.\n\n"
    
    # Add closing paragraph
    cover_letter += f"""I am enthusiastic about the opportunity to contribute to {company_name} and would welcome the chance to discuss how my background, skills, and enthusiasm would benefit your team.

Thank you for considering my application. I look forward to the opportunity to speak with you about this position.

Best regards,
[Your Name]"""
    
    return summary, cover_letter


def _generate_fallback_modifications(resume_text: str, job_description: str, missing_skills: List[str]) -> List[Dict]:
    """Generate fallback resume modification suggestions when AI fails."""
    
    resume_lower = resume_text.lower()
    
    # Check what sections are missing
    has_summary = 'summary' in resume_lower or 'objective' in resume_lower
    has_achievements = any(word in resume_lower for word in ['achieved', 'increased', 'reduced', 'improved', 'led'])
    
    modifications = []
    
    # Check for summary
    if not has_summary:
        modifications.append({
            "category": "summary",
            "title": "Add Professional Summary",
            "current_content": "Not present",
            "suggested_content": "Results-driven professional with expertise in relevant skills and proven track record of delivering measurable results.",
            "reason": "Professional summary increases interview chances by 30% as it gives recruiters a quick overview of your value proposition.",
            "priority": "high",
            "impact_score": 80
        })
    
    # Check for quantifiable achievements
    if not has_achievements:
        modifications.append({
            "category": "achievements",
            "title": "Quantify Your Achievements",
            "current_content": "Generic descriptions without numbers",
            "suggested_content": "Increased sales by 45% | Managed team of 8 people | Reduced costs by $50K annually",
            "reason": "Quantified achievements get 40% more callbacks as they provide concrete evidence of your impact.",
            "priority": "high",
            "impact_score": 90
        })
    
    # Add missing skills suggestion
    if missing_skills:
        modifications.append({
            "category": "keywords",
            "title": "Add Missing Keywords",
            "current_content": "Missing job-specific keywords",
            "suggested_content": "Incorporate: " + ", ".join(missing_skills[:5]),
            "reason": "ATS systems require keyword matching. Missing keywords can cause your resume to be filtered out.",
            "priority": "high",
            "impact_score": 85
        })
    
    # Add action verbs suggestion
    modifications.append({
        "category": "experience",
        "title": "Use Action Verbs",
        "current_content": "Passive language usage",
        "suggested_content": "Replace 'was responsible for' with: Led, Developed, Implemented, Achieved, Created",
        "reason": "Action verbs make your accomplishments more impactful and demonstrate initiative.",
        "priority": "medium",
        "impact_score": 70
    })
    
    # Add formatting suggestion
    modifications.append({
        "category": "format",
        "title": "Improve Resume Formatting",
        "current_content": "Check for consistent formatting",
        "suggested_content": "Use consistent bullet points, font sizes, and spacing throughout the document",
        "reason": "Clean formatting improves readability and ensures ATS systems can parse your resume correctly.",
        "priority": "medium",
        "impact_score": 65
    })
    
    return modifications


def _generate_fallback_interview_questions(resume_text: str, job_description: str) -> Dict:
    """Generate fallback interview questions when AI fails."""
    
    resume_lower = resume_text.lower()
    
    # Detect common skills/experience to customize questions
    has_leadership = any(word in resume_lower for word in ['led', 'managed', 'supervised', 'mentored'])
    has_technical = any(word in resume_lower for word in ['python', 'java', 'code', 'developer', 'engineer'])
    has_teamwork = any(word in resume_lower for word in ['team', 'collaborated', 'worked with'])
    
    questions = [
        {
            "question": "Tell me about yourself and why you're interested in this role.",
            "category": "behavioral",
            "difficulty": "easy",
            "answer_guidance": "Start with your current role, highlight relevant experience, and end with why this position excites you.",
            "sample_answer": "I'm a professional with experience in... I'm excited about this role because..."
        }
    ]
    
    if has_leadership:
        questions.append({
            "question": "Describe a time when you led a team through a challenging project.",
            "category": "behavioral",
            "difficulty": "medium",
            "answer_guidance": "Use the STAR method: Situation, Task, Action, Result. Focus on your leadership decisions and the outcome.",
            "sample_answer": "As a team leader, I faced a challenging project where..."
        })
    
    if has_technical:
        questions.append({
            "question": "Walk me through a technical project you're most proud of.",
            "category": "technical",
            "difficulty": "medium",
            "answer_guidance": "Explain the problem, your approach, the technologies used, and the outcome. Be specific about your role.",
            "sample_answer": "One project I'm proud of was... where I used Python and Django to..."
        })
    
    if has_teamwork:
        questions.append({
            "question": "Describe a situation where you had to collaborate with a difficult team member.",
            "category": "behavioral",
            "difficulty": "medium",
            "answer_guidance": "Focus on how you managed the situation professionally and achieved the team goal.",
            "sample_answer": "I worked with a challenging team member by..."
        })
    
    # Add common questions
    questions.extend([
        {
            "question": "What are your greatest strengths and how do they relate to this position?",
            "category": "behavioral",
            "difficulty": "easy",
            "answer_guidance": "Choose 2-3 strengths that directly match the job requirements. Provide specific examples.",
            "sample_answer": "My greatest strengths are problem-solving and communication..."
        },
        {
            "question": "Where do you see yourself in 5 years?",
            "category": "behavioral",
            "difficulty": "easy",
            "answer_guidance": "Show ambition but also loyalty. Connect your goals to the company's growth.",
            "sample_answer": "In 5 years, I see myself growing into a role where I can..."
        },
        {
            "question": "Why should we hire you over other candidates?",
            "category": "behavioral",
            "difficulty": "medium",
            "answer_guidance": "Highlight your unique value proposition. Focus on what makes you specifically qualified for this role.",
            "sample_answer": "You should hire me because..."
        },
        {
            "question": "Describe a challenging problem you faced and how you solved it.",
            "category": "behavioral",
            "difficulty": "medium",
            "answer_guidance": "Use STAR method. Focus on your problem-solving process and the results.",
            "sample_answer": "I faced a challenging situation where..."
        }
    ])
    
    return {
        "questions": questions[:10],
        "total_questions": len(questions),
        "job_title": "Target Position",
        "key_topics": []
    }


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
        score, missing_skills, matched_skills = calculate_match_score(resume_text, job_description)
        logger.info(f"Match score calculated: {score}%, Matched: {len(matched_skills)}, Missing: {len(missing_skills)}")
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
    
    # Create ResumeData object - handle both list and string inputs
    def ensure_list(value, field_name):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        # If it's a string, try to parse it as a list
        if isinstance(value, str):
            # Return as single item list if it's not empty
            return [value] if value.strip() else []
        return []
    
    # Handle experience and education - convert to dict if needed
    experience_list = []
    if request.experience:
        for exp in request.experience:
            if hasattr(exp, 'model_dump'):
                experience_list.append(exp.model_dump())
            elif isinstance(exp, dict):
                experience_list.append(exp)
    
    education_list = []
    if request.education:
        for edu in request.education:
            if hasattr(edu, 'model_dump'):
                education_list.append(edu.model_dump())
            elif isinstance(edu, dict):
                education_list.append(edu)
    
    # Create ResumeData object
    resume_data = ResumeData(
        full_name=request.full_name or "Your Name",
        email=request.email or "email@example.com",
        phone=request.phone or "",
        location=request.location or "",
        linkedin=request.linkedin or "",
        portfolio=request.portfolio or "",
        summary=request.summary or "",
        skills=ensure_list(request.skills, "skills"),
        experience=experience_list,
        education=education_list,
        certifications=ensure_list(request.certifications, "certifications"),
        languages=ensure_list(request.languages, "languages")
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
        # Use fallback instead of raising exception
        return _generate_fallback_interview_questions(request.resume_text, request.job_description)


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
        # Use fallback instead of raising exception
        return _generate_fallback_skills_gap(request.resume_text, request.job_description)


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
        # Use fallback instead of raising exception
        return _generate_fallback_comparison(request.user_resume_text, request.job_description)


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


# ==================== UNIFIED ANALYSIS ENDPOINT ====================

@app.post("/api/analyze/unified", tags=["Analysis"])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def unified_analysis(
    request: Request,
    resume_file: UploadFile = File(..., description="PDF resume file"),
    job_description: str = Form(..., description="Job description text"),
    include_interview_questions: bool = Form(True, description="Generate interview questions"),
    include_skills_gap: bool = Form(True, description="Analyze skills gap"),
    include_resume_variations: bool = Form(True, description="Generate resume variations"),
    include_comparison: bool = Form(True, description="Compare to ideal resume")
):
    """
    Unified Analysis Endpoint - Upload resume ONCE, get ALL results!
    
    This endpoint performs all analyses in a single call:
    - Resume parsing and extraction
    - Match score & ATS scoring
    - Skills analysis (matched/missing)
    - AI-generated improved summary and cover letter
    - Resume modification suggestions
    - Resume variations (4 types)
    - Interview questions
    - Skills gap analysis
    - Resume comparison
    
    Upload your resume once and get comprehensive career insights!
    """
    import time
    start_time = time.time()
    from datetime import datetime
    
    logger.info("Starting unified analysis")
    
    # Validate job description
    if not job_description or len(job_description.strip()) < settings.MIN_JOB_DESCRIPTION_LENGTH:
        raise InvalidJobDescriptionException(
            f"Job description must be at least {settings.MIN_JOB_DESCRIPTION_LENGTH} characters"
        )
    
    # Extract text from PDF
    try:
        resume_text = await extract_text_from_pdf_safe(resume_file, resume_file.filename)
    except Exception as e:
        logger.error(f"Error extracting PDF: {str(e)}")
        raise EmptyFileException("Failed to process the uploaded resume")
    
    if not resume_text or not resume_text.strip():
        raise EmptyFileException("Could not extract text from the resume")
    
    # Parse the resume
    parsed_data = parse_resume_from_text(resume_text)
    
    # Calculate match score
    score, missing_skills, matched_skills = calculate_match_score(resume_text, job_description)
    ats_score = calculate_ats_score(resume_text, job_description)
    
    # Generate resume tips
    resume_tips = generate_resume_tips(missing_skills, ats_score)
    
    # Generate AI content (summary + cover letter)
    ai_generated = False
    try:
        ai_result = await generate_ai_content_async(resume_text, job_description)
        improved_summary = ai_result.get("improved_summary", "")
        cover_letter = ai_result.get("cover_letter", "")
        resume_variations = ai_result.get("resume_variations", [])
        ai_generated = True
        logger.info("AI content generated successfully")
    except Exception as e:
        logger.warning(f"AI content generation failed, using fallback: {str(e)}")
        # Use improved fallback template-based generation
        improved_summary, cover_letter = generate_fallback_content(resume_text, job_description, missing_skills)
        resume_variations = []
    
    # Generate resume modifications suggestions
    try:
        modifications = await generate_resume_modifications_async(resume_text, job_description, parsed_data)
    except Exception as e:
        logger.warning(f"Error generating modifications: {str(e)}")
        # Use improved fallback modifications
        modifications = _generate_fallback_modifications(resume_text, job_description, missing_skills)
    
    # Initialize optional results
    interview_questions_result = None
    skills_gap_result = None
    comparison_result = None
    
    # Run optional analyses - use fallbacks if AI fails
    if include_interview_questions:
        try:
            interview_questions_result = await generate_interview_questions_async(resume_text, job_description, 10, ["technical", "behavioral"])
        except Exception as e:
            logger.warning(f"Error generating interview questions: {str(e)}")
            interview_questions_result = _generate_fallback_interview_questions(resume_text, job_description)
    
    if include_skills_gap:
        try:
            skills_gap_result = await generate_skills_gap_analysis_async(resume_text, job_description)
        except Exception as e:
            logger.warning(f"Error generating skills gap: {str(e)}")
            skills_gap_result = _generate_fallback_skills_gap(resume_text, job_description)
    
    if include_comparison:
        try:
            comparison_result = await generate_resume_comparison_async(resume_text, job_description)
        except Exception as e:
            logger.warning(f"Error generating comparison: {str(e)}")
            comparison_result = _generate_fallback_comparison(resume_text, job_description)
    
    processing_time = time.time() - start_time
    
    return UnifiedAnalysisResponse(
        parsed_resume=ResumeParseResponse(
            full_name=parsed_data.full_name,
            email=parsed_data.email,
            phone=parsed_data.phone,
            location=parsed_data.location,
            linkedin=parsed_data.linkedin,
            summary=parsed_data.summary,
            skills=parsed_data.skills,
            experience=parsed_data.experience,
            education=parsed_data.education
        ),
        match_score=score,
        ats_score=ats_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        improved_summary=improved_summary,
        cover_letter=cover_letter,
        resume_tips=resume_tips,
        resume_modifications=modifications,
        resume_variations=resume_variations,
        interview_questions=interview_questions_result.get("questions") if interview_questions_result else None,
        total_interview_questions=interview_questions_result.get("total_questions") if interview_questions_result else None,
        skills_gap=skills_gap_result,
        comparison=comparison_result,
        processing_time=round(processing_time, 2),
        timestamp=datetime.now().isoformat()
    )


async def generate_resume_modifications_async(resume_text: str, job_description: str, parsed_data) -> List[Dict]:
    """Generate AI-powered resume modification suggestions."""
    from gemini_service import get_gemini_service
    
    prompt = f"""
You are an expert resume writer and career consultant. Analyze this resume against the job description 
and provide specific, actionable modification suggestions.

CURRENT RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide 5-7 specific modification suggestions. For each suggestion include:
1. Category: summary/skills/experience/achievements/keywords
2. Title: brief title of the suggestion
3. Current Content: what the resume currently has (or "Not present")
4. Suggested Content: what it should say instead
5. Reason: why this change would improve the resume
6. Priority: high/medium/low
7. Impact Score: 0-100 (how much this improves the resume)

Format as JSON array:
[
  {{
    "category": "summary",
    "title": "Strengthen Professional Summary",
    "current_content": "Current summary text or 'Not present'",
    "suggested_content": "Improved version",
    "reason": "Why this helps",
    "priority": "high",
    "impact_score": 85
  }}
]

Make suggestions specific and actionable, not generic advice.
"""
    
    try:
        import json
        import re
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: get_gemini_service().model.generate_content(
                contents=prompt,
                generation_config=GenerationConfig(temperature=0.7, max_output_tokens=2048)
            )
        )
        
        # Try to parse JSON
        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        logger.error(f"Error in AI modification generation: {str(e)}")
    
    # Fallback modifications
    return _generate_fallback_modifications(resume_text, job_description, [])


def _generate_fallback_skills_gap(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Generate fallback skills gap analysis."""
    from skill_engine import calculate_match_score
    
    score, missing, matched = calculate_match_score(resume_text, job_description)
    matched_score = 100 - score
    
    # Extract common technical skills from job description
    job_lower = job_description.lower()
    common_tech = ['python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular', 'node', 'django', 
                   'flask', 'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'machine learning']
    
    missing_tech = [s for s in common_tech if s in job_lower and s not in resume_text.lower()]
    
    return {
        "matched_skills": [],
        "missing_skills": missing[:10],
        "skill_gaps": [
            {
                "skill": skill,
                "importance": "high",
                "current_level": "none",
                "suggested_resources": [
                    {"type": "course", "title": f"Learn {skill.title()}", "url": f"https://www.udemy.com/courses/search/?q={skill}"},
                    {"type": "tutorial", "title": f"{skill.title()} Tutorial", "url": f"https://www.w3schools.com/{skill}/"}
                ]
            } for skill in missing_tech[:5]
        ],
        "overall_gap_score": matched_score,
        "learning_priority": "high" if matched_score > 50 else "medium",
        "recommended_courses": [
            {"title": f"Master {skill}", "provider": "Udemy/Coursera", "url": f"https://www.coursera.org/search?query={skill}"}
            for skill in missing_tech[:3]
        ]
    }


def _generate_fallback_comparison(user_resume_text: str, job_description: str) -> Dict[str, Any]:
    """Generate fallback resume comparison."""
    from skill_engine import calculate_match_score
    
    score, missing, matched = calculate_match_score(user_resume_text, job_description)
    ats = calculate_ats_score(user_resume_text, job_description)
    
    import re
    job_keywords = set(re.findall(r'\b[a-z]{3,}\b', job_description.lower()))
    resume_keywords = set(re.findall(r'\b[a-z]{3,}\b', user_resume_text.lower()))
    found = list(job_keywords.intersection(resume_keywords))
    missing_kw = list(job_keywords - resume_keywords)
    
    return {
        "overall_score": score,
        "ats_score": ats,
        "comparison_items": [
            {
                "category": "Skills",
                "user_resume": f"Has {len(found)} relevant skills",
                "ideal_resume": "Should have all job-required skills",
                "score": score,
                "recommendations": [f"Add these skills: {', '.join(missing_kw[:5])}"]
            }
        ],
        "keyword_analysis": {
            "found": found[:10],
            "missing": missing_kw[:10]
        },
        "improvement_suggestions": [
            "Add more keywords from job description",
            "Quantify your achievements",
            "Include relevant certifications"
        ],
        "ideal_resume_summary": "An ideal resume should include all required skills from the job description, quantifiable achievements, and relevant certifications."
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

