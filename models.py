"""
Pydantic models for HireMate AI API.
Includes request/response validation with detailed constraints.
"""
from pydantic import BaseModel, Field, field_validator, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum
import logging

# Configure logger
logger = logging.getLogger(__name__)


class ResumeTemplate(str, Enum):
    """Available resume template types."""
    MODERN = "modern"
    CLASSIC = "classic"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    ENTRY = "entry"


class IndustryType(str, Enum):
    """Industry types for resume customization."""
    TECH = "tech"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    MARKETING = "marketing"
    ENGINEERING = "engineering"
    GENERAL = "general"


class AnalyzeRequest(BaseModel):
    """Request model for resume analysis."""
    resume: str = Field(..., description="Resume text content")
    job_description: str = Field(..., description="Job description text")
    
    @field_validator('resume')
    @classmethod
    def validate_resume(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Resume cannot be empty")
        if len(v) > 50000:
            raise ValueError("Resume text is too long (max 50000 characters)")
        return v.strip()
    
    @field_validator('job_description')
    @classmethod
    def validate_job_description(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Job description cannot be empty")
        if len(v) < 10:
            raise ValueError("Job description must be at least 10 characters")
        if len(v) > 50000:
            raise ValueError("Job description is too long (max 50000 characters)")
        return v.strip()


class AnalyzeResponse(BaseModel):
    """Response model for resume analysis."""
    match_score: float = Field(..., description="Skill match percentage (0-100)", ge=0, le=100)
    ats_score: float = Field(default=0, description="ATS compatibility score (0-100)", ge=0, le=100)
    matched_skills: List[str] = Field(default_factory=list, description="List of matched skills")
    missing_skills: List[str] = Field(default_factory=list, description="List of missing skills")
    improved_summary: str = Field(default="", description="AI-generated professional summary")
    cover_letter: str = Field(default="", description="AI-generated tailored cover letter")
    resume_tips: List[str] = Field(default_factory=list, description="Tips to improve resume")
    resume_variations: List[str] = Field(default_factory=list, description="AI-generated resume variations tailored to the job")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "match_score": 75.5,
                "ats_score": 82.0,
                "matched_skills": ["python", "javascript"],
                "missing_skills": ["kubernetes", "aws", "docker"],
                "improved_summary": "Experienced software engineer...",
                "cover_letter": "Dear Hiring Manager...",
                "resume_tips": ["Add more quantifiable achievements", "Include relevant keywords"],
                "resume_variations": [
                    "Resume Variation 1: Professional Summary Focused...",
                    "Resume Variation 2: Achievement-Focused...",
                    "Resume Variation 3: Technical Skills Focused...",
                    "Resume Variation 4: Entry-Level Friendly..."
                ]
            }
        }
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    message: Optional[str] = Field(None, description="Additional message")


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")


# ==================== Resume Generation Models ====================

class ExperienceItem(BaseModel):
    """Experience item for resume."""
    title: str = Field(default="", description="Job title or position")
    company: str = Field(default="", description="Company name")
    duration: str = Field(default="", description="Duration (e.g., Jan 2020 - Present)")
    description: str = Field(default="", description="Job description")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies used")
    achievements: List[str] = Field(default_factory=list, description="Key achievements")


class EducationItem(BaseModel):
    """Education item for resume."""
    degree: str = Field(default="", description="Degree or certification")
    institution: str = Field(default="", description="School or university")
    year: str = Field(default="", description=" graduation year")
    description: Optional[str] = Field(None, description="Additional details (GPA, honors)")


class ResumeGenerateRequest(BaseModel):
    """Request model for generating a resume."""
    template_id: str = Field(default="modern", description="Template type: modern, classic, technical, executive, entry")
    industry: str = Field(default="general", description="Industry type: tech, finance, healthcare, marketing, engineering, general")
    include_photo: bool = Field(default=False, description="Whether to include photo")
    primary_color: str = Field(default="#8b5cf6", description="Primary color for template (hex)")
    
    # Personal Information
    full_name: str = Field(default="", description="Full name")
    email: str = Field(default="", description="Email address")
    phone: str = Field(default="", description="Phone number")
    location: str = Field(default="", description="Location/address")
    linkedin: str = Field(default="", description="LinkedIn URL")
    portfolio: str = Field(default="", description="Portfolio/website URL")
    
    # Content
    summary: str = Field(default="", description="Professional summary")
    skills: List[str] = Field(default_factory=list, description="List of skills")
    experience: List[ExperienceItem] = Field(default_factory=list, description="Work experience")
    education: List[EducationItem] = Field(default_factory=list, description="Education history")
    certifications: List[str] = Field(default_factory=list, description="Certifications")
    languages: List[str] = Field(default_factory=list, description="Languages known")


class ResumeGenerateResponse(BaseModel):
    """Response model for generated resume."""
    template_id: str
    template_name: str
    html_content: str
    available_templates: List[Dict[str, str]]
    industries: List[Dict[str, str]]


class ResumeParseRequest(BaseModel):
    """Request model for parsing existing resume."""
    resume_file: Optional[str] = Field(None, description="PDF file content as base64 (optional)")


class ResumeParseResponse(BaseModel):
    """Response model for parsed resume data."""
    full_name: str
    email: str
    phone: str
    location: str
    linkedin: str
    summary: str
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]


# ==================== Interview Questions Models ====================

class InterviewQuestion(BaseModel):
    """Single interview question with answer guidance."""
    question: str
    category: str  # technical, behavioral, situational
    difficulty: str  # easy, medium, hard
    answer_guidance: str
    sample_answer: Optional[str] = None


class InterviewQuestionsRequest(BaseModel):
    """Request model for generating interview questions."""
    resume_text: str = Field(..., description="Resume text content")
    job_description: str = Field(..., description="Job description text")
    num_questions: int = Field(default=10, description="Number of questions to generate", ge=5, le=30)
    question_types: List[str] = Field(default_factory=lambda: ["technical", "behavioral"], 
                                       description="Types: technical, behavioral, situational")


class InterviewQuestionsResponse(BaseModel):
    """Response model for interview questions."""
    questions: List[InterviewQuestion]
    total_questions: int
    job_title: str
    key_topics: List[str]


# ==================== Skills Gap Analysis Models ====================

class SkillGapItem(BaseModel):
    """Individual skill gap analysis."""
    skill: str
    importance: str  # high, medium, low
    current_level: str  # expert, intermediate, beginner, none
    suggested_resources: List[Dict[str, str]]  # courses, tutorials, etc.


class SkillsGapAnalysisRequest(BaseModel):
    """Request model for skills gap analysis."""
    resume_text: str = Field(..., description="Resume text content")
    job_description: str = Field(..., description="Job description text")


class SkillsGapAnalysisResponse(BaseModel):
    """Response model for skills gap analysis."""
    matched_skills: List[str]
    missing_skills: List[str]
    skill_gaps: List[SkillGapItem]
    overall_gap_score: float  # 0-100
    learning_priority: str  # high, medium, low
    recommended_courses: List[Dict[str, str]]


# ==================== Resume Comparison Models ====================

class ResumeComparisonItem(BaseModel):
    """Comparison between user resume and ideal resume."""
    category: str
    user_resume: str
    ideal_resume: str
    score: float  # 0-100
    recommendations: List[str]


class ResumeComparisonRequest(BaseModel):
    """Request model for comparing resumes."""
    user_resume_text: str = Field(..., description="User's resume text")
    job_description: str = Field(..., description="Target job description")


class ResumeComparisonResponse(BaseModel):
    """Response model for resume comparison."""
    overall_score: float
    ats_score: float
    comparison_items: List[ResumeComparisonItem]
    keyword_analysis: Dict[str, List[str]]  # found, missing
    improvement_suggestions: List[str]
    ideal_resume_summary: str

