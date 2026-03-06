"""
Skill matching engine for HireMate AI.
Calculates match score between resume and job description.
"""
import re
import logging
from typing import Tuple, List, Optional

# Configure logger
logger = logging.getLogger(__name__)


# Common technical skills keywords for better matching
TECHNICAL_SKILLS = {
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
    'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
    'react', 'angular', 'vue', 'nodejs', 'django', 'flask', 'spring', 'express',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github',
    'machine learning', 'deep learning', 'nlp', 'tensorflow', 'pytorch', 'keras',
    'data science', 'data analysis', 'data engineering', 'etl', 'spark', 'hadoop',
    'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum', 'ci/cd',
    'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind', 'jquery',
    'linux', 'unix', 'bash', 'shell', 'powershell', 'networking', 'security',
    'testing', 'unit testing', 'integration testing', 'selenium', 'jest',
    'photoshop', 'figma', 'sketch', 'adobe', 'ui', 'ux', 'design',
    'communication', 'leadership', 'teamwork', 'problem solving', 'analytical'
}


def extract_words(text: str) -> set:
    """
    Extract and clean words from text.
    
    Args:
        text: Input text string
    
    Returns:
        Set of lowercase words
    """
    if not text or not isinstance(text, str):
        logger.warning("Invalid input to extract_words: not a string or empty")
        return set()
    
    # Use regex to find words (only alphabetic characters)
    words = re.findall(r'\b[A-Za-z]+\b', text.lower())
    
    # Filter out very short words (less than 2 characters)
    words = [w for w in words if len(w) >= 2]
    
    logger.debug(f"Extracted {len(words)} unique words from text")
    return set(words)


def extract_key_skills(text: str) -> set:
    """
    Extract key technical skills from text.
    
    Args:
        text: Input text string
    
    Returns:
        Set of identified technical skills
    """
    text_lower = text.lower()
    found_skills = set()
    
    for skill in TECHNICAL_SKILLS:
        if skill in text_lower:
            found_skills.add(skill)
    
    logger.debug(f"Identified {len(found_skills)} key skills")
    return found_skills


def calculate_match_score(resume: str, job_description: str) -> Tuple[float, List[str], List[str]]:
    """
    Calculate skill match score between resume and job description.
    
    Args:
        resume: Resume text content
        job_description: Job description text
    
    Returns:
        Tuple of (match_score, list of missing skills, list of matched skills)
    """
    try:
        # Validate inputs
        if not resume or not isinstance(resume, str):
            logger.warning("Invalid resume provided")
            resume = ""
        
        if not job_description or not isinstance(job_description, str):
            logger.warning("Invalid job description provided")
            return 0.0, [], []
        
        # Extract key skills from both texts using the skill extraction
        resume_skills = extract_key_skills(resume)
        job_skills = extract_key_skills(job_description)
        
        # Also extract general words for broader matching
        resume_words = extract_words(resume)
        job_words = extract_words(job_description)
        
        # Calculate matched and missing skills (focus on technical skills)
        matched = resume_skills.intersection(job_skills)
        missing_skills = job_skills - resume_skills
        
        # Also check for general word matches (soft skills, domain terms)
        general_matched = resume_words.intersection(job_words) - TECHNICAL_SKILLS
        general_missing = job_words - resume_words - TECHNICAL_SKILLS
        
        # Calculate match score
        if len(job_skills) > 0:
            technical_score = (len(matched) / len(job_skills)) * 100
        else:
            technical_score = 0
        
        # Include general word matching for softer score
        if len(job_words) > 0:
            general_score = (len(general_matched) / len(job_words)) * 100
        else:
            general_score = 0
        
        # Weighted final score (70% technical skills, 30% general terms)
        if technical_score > 0 or general_score > 0:
            final_score = (technical_score * 0.7) + (general_score * 0.3)
        else:
            final_score = 0
        
        # Ensure score is at least based on word overlap
        if final_score == 0 and len(general_matched) > 0:
            final_score = min(50, len(general_matched) * 5)
        
        # Round to 2 decimal places
        final_score = round(min(100, final_score), 2)
        
        # Get all missing skills (prioritize technical skills)
        missing_list = list(missing_skills) + list(general_missing)
        
        # Sort missing skills to prioritize technical ones
        missing_technical = [s for s in missing_list if s in TECHNICAL_SKILLS]
        missing_general = [s for s in missing_list if s not in TECHNICAL_SKILLS]
        
        # Combine: technical skills first (more items), then general
        prioritized_missing = missing_technical[:15] + missing_general[:10]
        
        logger.info(
            f"Match score calculated: {final_score}%. "
            f"Matched: {len(matched) + len(general_matched)}, Missing: {len(prioritized_missing)}"
        )
        
        # Return both matched technical skills and general matched words
        all_matched = list(matched) + list(general_matched)[:30]
        return final_score, prioritized_missing, all_matched
        
    except Exception as e:
        logger.error(f"Error calculating match score: {str(e)}")
        return 0.0, [], []


def get_resume_skills(resume: str) -> List[str]:
    """
    Extract identified skills from resume.
    
    Args:
        resume: Resume text content
    
    Returns:
        List of identified skills
    """
    try:
        if not resume or not isinstance(resume, str):
            return []
        
        skills = extract_key_skills(resume)
        return sorted(list(skills))
        
    except Exception as e:
        logger.error(f"Error extracting resume skills: {str(e)}")
        return []

