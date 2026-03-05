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


def calculate_match_score(resume: str, job_description: str) -> Tuple[float, List[str]]:
    """
    Calculate skill match score between resume and job description.
    
    Args:
        resume: Resume text content
        job_description: Job description text
    
    Returns:
        Tuple of (match_score, list of missing skills)
    """
    try:
        # Validate inputs
        if not resume or not isinstance(resume, str):
            logger.warning("Invalid resume provided")
            resume = ""
        
        if not job_description or not isinstance(job_description, str):
            logger.warning("Invalid job description provided")
            return 0.0, []
        
        # Extract words from both texts
        resume_words = extract_words(resume)
        job_words = extract_words(job_description)
        
        # Handle edge case of empty job description
        if len(job_words) == 0:
            logger.info("Job description is empty")
            return 0.0, []
        
        # Calculate matched and missing skills
        matched = resume_words.intersection(job_words)
        missing = job_words - resume_words
        
        # Calculate match score as percentage
        # Weight technical skills more heavily
        matched_technical = matched.intersection(TECHNICAL_SKILLS)
        job_technical = job_words.intersection(TECHNICAL_SKILLS)
        
        if len(job_technical) > 0:
            technical_score = (len(matched_technical) / len(job_technical)) * 100
        else:
            technical_score = 0
        
        # Use standard word intersection as base score
        base_score = (len(matched) / len(job_words)) * 100
        
        # Weighted final score (60% technical, 40% general)
        if technical_score > 0:
            final_score = (technical_score * 0.6) + (base_score * 0.4)
        else:
            final_score = base_score
        
        # Round to 2 decimal places
        final_score = round(final_score, 2)
        
        # Get top missing skills (prioritize technical skills)
        missing_list = list(missing)
        
        # Sort missing skills to prioritize technical ones
        missing_technical = [s for s in missing_list if s in TECHNICAL_SKILLS]
        missing_general = [s for s in missing_list if s not in TECHNICAL_SKILLS]
        
        # Combine: technical skills first, then general
        prioritized_missing = missing_technical[:5] + missing_general[:5]
        
        logger.info(
            f"Match score calculated: {final_score}%. "
            f"Matched: {len(matched)}, Missing: {len(missing)}"
        )
        
        return final_score, prioritized_missing
        
    except Exception as e:
        logger.error(f"Error calculating match score: {str(e)}")
        return 0.0, []


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

