"""
Gemini AI service for HireMate AI.
Generates improved summaries, cover letters, interview questions, and more using Google Gemini API.
"""
import logging
import os
import asyncio
from typing import Optional, Dict, Any, List
import re
import google.generativeai as genai
from google.api_core.exceptions import (
    GoogleAPIError,
    ResourceExhausted,
    InvalidArgument
)
from google.generativeai import GenerationConfig

from config import settings
from exceptions import AIGenerationException

# Configure logger
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class GeminiService:
    """
    Service class for Google Gemini API integration.
    Provides async methods for generating AI content.
    """
    
    def __init__(self):
        """Initialize Gemini service with API configuration."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY is not set. Please configure it in .env file.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Generation config
        self.generation_config = GenerationConfig(
            temperature=0.7,
            top_p=0.8,
            top_k=40,
            max_output_tokens=2048,
        )
        
        logger.info("GeminiService initialized successfully")
    
    def _build_prompt(self, resume: str, job_description: str) -> str:
        """
        Build prompt for AI content generation.
        
        Args:
            resume: Resume text content
            job_description: Job description text
        
        Returns:
            Formatted prompt string
        """
        return f"""
You are an expert career consultant and resume writer with years of experience helping job seekers land their dream jobs.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

TASK:
Based on the resume and job description above, create:

1. An improved professional summary (4-5 lines) that highlights the candidate's relevant experience and skills for this specific role.

2. A tailored cover letter (formal tone, 3-4 paragraphs) that demonstrates how the candidate's background aligns with the job requirements.

IMPORTANT:
- Focus on the skills and experience most relevant to the job description
- Use professional business language
- Make it personalized to the specific job, not generic
- Keep the cover letter concise but impactful

Format your response as:

SUMMARY:
[Your professional summary here]

COVER_LETTER:
[Your cover letter here]
"""
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse AI response into structured format.
        
        Args:
            response_text: Raw response from Gemini API
        
        Returns:
            Dictionary with 'improved_summary' and 'cover_letter'
        """
        result = {
            "improved_summary": "",
            "cover_letter": ""
        }
        
        try:
            # Split by section headers
            if "SUMMARY:" in response_text and "COVER_LETTER:" in response_text:
                parts = response_text.split("COVER_LETTER:")
                result["improved_summary"] = parts[0].replace("SUMMARY:", "").strip()
                result["cover_letter"] = parts[1].strip()
            elif "SUMMARY:" in response_text:
                result["improved_summary"] = response_text.replace("SUMMARY:", "").strip()
            elif "COVER_LETTER:" in response_text:
                result["cover_letter"] = response_text.replace("COVER_LETTER:", "").strip()
            else:
                # If no clear separation, use entire response as cover letter
                result["cover_letter"] = response_text.strip()
                
        except Exception as e:
            logger.warning(f"Error parsing AI response: {str(e)}")
        
        return result
    
    async def generate_content_async(self, resume: str, job_description: str) -> Dict[str, str]:
        """
        Generate AI content asynchronously.
        
        Args:
            resume: Resume text content
            job_description: Job description text
        
        Returns:
            Dictionary with 'improved_summary', 'cover_letter', and 'resume_variations'
        
        Raises:
            AIGenerationException: If content generation fails
        """
        try:
            logger.info("Starting async AI content generation")
            
            # Build prompt for summary and cover letter
            prompt = self._build_prompt(resume, job_description)
            
            # Generate content using asyncio.to_thread for sync API
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
            )
            
            # Parse response
            result = self._parse_ai_response(response.text)
            
            # Generate resume variations
            logger.info("Generating resume variations")
            variations = await self._generate_resume_variations_async(resume, job_description)
            result['resume_variations'] = variations
            
            logger.info("AI content generated successfully")
            return result
            
        except ResourceExhausted as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            raise AIGenerationException(
                "AI service is temporarily busy. Please try again in a few moments."
            )
        except InvalidArgument as e:
            logger.error(f"Invalid request: {str(e)}")
            raise AIGenerationException(
                "Invalid request. Please check your input and try again."
            )
        except GoogleAPIError as e:
            logger.error(f"Google API error: {str(e)}")
            raise AIGenerationException(
                f"AI service error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in AI generation: {str(e)}")
            raise AIGenerationException(
                "Failed to generate AI content. Please try again."
            )
    
    async def _generate_resume_variations_async(self, resume: str, job_description: str) -> List[str]:
        """
        Generate 4 different resume variations tailored to the job description.
        
        Args:
            resume: Original resume text
            job_description: Job description text
        
        Returns:
            List of 4 resume variations
        """
        variations_prompt = f"""
You are an expert resume writer. Based on the original resume and job description below, 
create 4 different resume variations that maximize the chances of getting an interview.

ORIGINAL RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

Create exactly 4 resume variations with different approaches. For each variation:
- Rewrite the professional summary to highlight different aspects
- Reorder and emphasize different skills and experiences
- Use different action verbs and phrasing

Format your response as:

VARIATION 1 - Professional Summary Focused:
[Complete rewritten resume focusing on professional summary]

VARIATION 2 - Achievement Focused:
[Complete rewritten resume focusing on quantifiable achievements]

VARIATION 3 - Technical Skills Focused:
[Complete rewritten resume emphasizing technical skills]

VARIATION 4 - Leadership & Impact Focused:
[Complete rewritten resume highlighting leadership and impact]

Make each variation complete and ATS-friendly, incorporating keywords from the job description naturally.
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    variations_prompt,
                    GenerationConfig(
                        temperature=0.8,
                        top_p=0.9,
                        top_k=40,
                        max_output_tokens=4096,
                    )
                )
            )
            
            # Parse the variations
            variations = self._parse_variations(response.text)
            return variations
            
        except Exception as e:
            logger.error(f"Error generating resume variations: {str(e)}")
            return self._generate_fallback_variations(resume, job_description)
    
    def _parse_variations(self, response_text: str) -> List[str]:
        """Parse resume variations from AI response."""
        variations = []
        
        # Split by variation headers
        parts = response_text.split("VARIATION")
        
        for part in parts:
            if not part.strip():
                continue
            # Clean up the variation text
            variation = part.strip()
            if variation.startswith("1") or variation.startswith("2") or variation.startswith("3") or variation.startswith("4"):
                # Remove the number prefix (e.g., "1 - Professional...")
                lines = variation.split('\n', 1)
                if len(lines) > 1:
                    variation = lines[1].strip()
            variations.append(variation)
        
        # Ensure we have exactly 4 variations
        while len(variations) < 4:
            variations.append(f"Variation {len(variations) + 1}: Please regenerate to see this variation.")
        
        return variations[:4]
    
    def _generate_fallback_variations(self, resume: str, job_description: str) -> List[str]:
        """Generate fallback resume variations when AI fails."""
        job_words = set(re.findall(r'\b[a-z]{3,}\b', job_description.lower()))
        
        variations = [
            f"""PROFESSIONAL SUMMARY FOCUSED:
Based on the job requirements for {', '.join(list(job_words)[:5]) if job_words else 'this position'}, 
this variation emphasizes your professional background and career trajectory.
\n\nEXPERIENCE:\n[Your experience section tailored to highlight career progression]
\n\nSKILLS:\n[Emphasize skills matching: {', '.join(list(job_words)[:8]) if job_words else 'relevant skills'}]""",
            
            f"""ACHIEVEMENT FOCUSED:
This variation quantifies your accomplishments to stand out.
\n\nPROFESSIONAL SUMMARY:\nResults-driven professional with demonstrated success.
\n\nACHIEVEMENTS:\n• Increased efficiency by measurable percentages
• Led initiatives resulting in cost savings
• Delivered projects on time and under budget
\n\nInclude specific numbers from your experience.""",
            
            f"""TECHNICAL SKILLS FOCUSED:
Keywords: {', '.join(list(job_words)[:10]) if job_words else 'technical skills'}
\n\nSKILLS SECTION (Top):
{', '.join(list(job_words)[:15]) if job_words else 'Relevant technical skills'}
\n\nPROFESSIONAL SUMMARY:
Technical professional with hands-on experience in required technologies.
\n\nFocus on practical application of skills listed in job description.""",
            
            f"""LEADERSHIP & IMPACT FOCUSED:
\n\nPROFESSIONAL SUMMARY:
Proven leader with track record of driving results and mentoring teams.
\n\nLEADERSHIP EXPERIENCE:
• Managed teams of X people
• Made strategic decisions impacting business
• Mentored junior team members
\n\nQuantify your leadership impact in your specific role."""
        ]
        
        return variations
    
    def generate_content(self, resume: str, job_description: str) -> str:
        """
        Synchronous wrapper for generate_content_async.
        
        Args:
            resume: Resume text content
            job_description: Job description text
        
        Returns:
            Combined AI response as string
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create new one
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run,
                        self.generate_content_async(resume, job_description)
                    )
                    result = future.result()
            else:
                result = loop.run_until_complete(
                    self.generate_content_async(resume, job_description)
                )
            
            # Convert back to string format for backward compatibility
            response = f"SUMMARY:\n{result.get('improved_summary', '')}\n\nCOVER_LETTER:\n{result.get('cover_letter', '')}"
            return response
            
        except Exception as e:
            logger.error(f"Error in sync generate_content: {str(e)}")
            raise AIGenerationException(f"Failed to generate content: {str(e)}")


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """
    Get or create Gemini service instance.
    
    Returns:
        GeminiService instance
    """
    global _gemini_service
    
    if _gemini_service is None:
        try:
            _gemini_service = GeminiService()
        except ValueError as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise
    
    return _gemini_service


# Backward compatible function
def generate_ai_content(resume: str, job_description: str) -> str:
    """
    Generate AI content (backward compatible wrapper).
    
    Args:
        resume: Resume text content
        job_description: Job description text
    
    Returns:
        Combined AI response as string
    """
    try:
        service = get_gemini_service()
        return service.generate_content(resume, job_description)
    except Exception as e:
        logger.error(f"Error in generate_ai_content: {str(e)}")
        raise AIGenerationException(f"Failed to generate AI content: {str(e)}")


# Async version
async def generate_ai_content_async(resume: str, job_description: str) -> Dict[str, str]:
    """
    Generate AI content asynchronously.
    
    Args:
        resume: Resume text content
        job_description: Job description text
    
    Returns:
        Dictionary with 'improved_summary' and 'cover_letter'
    """
    service = get_gemini_service()
    return await service.generate_content_async(resume, job_description)


# ==================== New AI Features ====================

async def generate_interview_questions_async(resume_text: str, job_description: str, 
                                            num_questions: int = 10, 
                                            question_types: List[str] = None) -> Dict[str, Any]:
    """
    Generate interview questions based on resume and job description.
    
    Args:
        resume_text: Resume text content
        job_description: Job description text
        num_questions: Number of questions to generate
        question_types: Types of questions (technical, behavioral, situational)
    
    Returns:
        Dictionary with interview questions and metadata
    """
    if question_types is None:
        question_types = ["technical", "behavioral"]
    
    types_str = ", ".join(question_types)
    
    prompt = f"""
You are an expert interviewer and career coach. Based on the resume and job description below,
generate {num_questions} interview questions.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Generate questions from these categories: {types_str}

For each question include:
1. The question itself
2. Category (technical/behavioral/situational)
3. Difficulty level (easy/medium/hard)
4. Guidance on how to answer
5. A sample answer

Format as JSON array:
[
  {{
    "question": "...",
    "category": "...",
    "Difficulty": "...",
    "answer_guidance": "...",
    "sample_answer": "..."
  }}
]

Make sure questions are relevant to the specific job and candidate's experience.
"""
    
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: get_gemini_service().model.generate_content(
                prompt,
                GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=4096,
                )
            )
        )
        
        # Parse JSON response
        import json
        questions_text = response.text
        
        # Try to extract JSON from response
        try:
            # Find JSON array in response
            import re
            json_match = re.search(r'\[.*\]', questions_text, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
            else:
                questions = _generate_fallback_questions(resume_text, job_description, num_questions)
        except:
            questions = _generate_fallback_questions(resume_text, job_description, num_questions)
        
        # Extract job title and key topics
        job_title = _extract_job_title(job_description)
        key_topics = _extract_key_topics(job_description)
        
        return {
            "questions": questions,
            "total_questions": len(questions),
            "job_title": job_title,
            "key_topics": key_topics
        }
        
    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}")
        return {
            "questions": _generate_fallback_questions(resume_text, job_description, num_questions),
            "total_questions": num_questions,
            "job_title": _extract_job_title(job_description),
            "key_topics": _extract_key_topics(job_description)
        }


def _generate_fallback_questions(resume_text: str, job_description: str, num: int) -> List[Dict]:
    """Generate fallback interview questions."""
    return [
        {
            "question": "Tell me about yourself and why you're interested in this role.",
            "category": "behavioral",
            "difficulty": "easy",
            "answer_guidance": "Start with your current role, highlight relevant experience, and end with why this position excites you.",
            "sample_answer": "I'm a software engineer with 5 years of experience in web development..."
        },
        {
            "question": "Describe a challenging project you worked on and how you overcame the challenges.",
            "category": "behavioral",
            "difficulty": "medium",
            "answer_guidance": "Use the STAR method (Situation, Task, Action, Result) to structure your answer.",
            "sample_answer": "In my previous role, we needed to migrate a legacy system..."
        },
        {
            "question": "What are your greatest strengths and how do they relate to this position?",
            "category": "behavioral",
            "difficulty": "easy",
            "answer_guidance": "Choose 2-3 strengths that directly match the job requirements.",
            "sample_answer": "My greatest strengths are problem-solving and communication..."
        }
    ][:num]


def _extract_job_title(job_description: str) -> str:
    """Extract job title from job description."""
    lines = job_description.split('\n')
    for line in lines[:5]:
        if len(line.strip()) > 3:
            return line.strip()[:50]
    return "Target Position"


def _extract_key_topics(job_description: str) -> List[str]:
    """Extract key topics/skills from job description."""
    import re
    words = re.findall(r'\b[a-z#+.]{3,}\b', job_description.lower())
    common_words = {'the', 'and', 'for', 'are', 'with', 'this', 'from', 'that', 'have', 'will', 'your', 'experience', 'work', 'job', 'role', 'position', 'team', 'skills', 'ability', 'years', 'plus', 'minimum'}
    topics = [w for w in set(words) if w not in common_words and len(w) > 3]
    return topics[:10]


async def generate_skills_gap_analysis_async(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Generate skills gap analysis with learning resources.
    
    Args:
        resume_text: Resume text content
        job_description: Job description text
    
    Returns:
        Dictionary with skills gap analysis and recommendations
    """
    prompt = f"""
Analyze the skills gap between the resume and job description. Provide:
1. Matched skills
2. Missing skills
3. For each missing skill, suggest learning resources (courses, tutorials, certifications)

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Format as JSON:
{{
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill3", "skill4"],
  "skill_gaps": [
    {{
      "skill": "skill_name",
      "importance": "high/medium/low",
      "current_level": "expert/intermediate/beginner/none",
      "suggested_resources": [
        {{"type": "course", "title": "...", "url": "..."}},
        {{"type": "tutorial", "title": "...", "url": "..."}}
      ]
    }}
  ],
  "overall_gap_score": 0-100,
  "learning_priority": "high/medium/low",
  "recommended_courses": [
    {{"title": "...", "provider": "...", "url": "..."}}
  ]
}}
"""
    
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: get_gemini_service().model.generate_content(
                prompt,
                GenerationConfig(temperature=0.5, max_output_tokens=4096)
            )
        )
        
        import json
        import re
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
    except Exception as e:
        logger.error(f"Error generating skills gap analysis: {str(e)}")
    
    # Fallback
    return _generate_fallback_skills_gap(resume_text, job_description)


def _generate_fallback_skills_gap(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Generate fallback skills gap analysis."""
    from skill_engine import calculate_match_score
    
    score, missing = calculate_match_score(resume_text, job_description)
    matched_score = 100 - score
    
    return {
        "matched_skills": [],
        "missing_skills": missing[:10],
        "skill_gaps": [
            {
                "skill": skill,
                "importance": "high",
                "current_level": "none",
                "suggested_resources": [
                    {"type": "course", "title": f"Learn {skill}", "url": f"https://www.udemy.com/courses/search/?q={skill}"}
                ]
            } for skill in missing[:5]
        ],
        "overall_gap_score": matched_score,
        "learning_priority": "high" if matched_score > 50 else "medium",
        "recommended_courses": [
            {"title": f"Master {skill}", "provider": "Udemy/Coursera", "url": f"https://www.coursera.org/search?query={skill}"}
            for skill in missing[:3]
        ]
    }


async def generate_resume_comparison_async(user_resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Compare user resume against ideal resume for the job.
    
    Args:
        user_resume_text: User's resume text
        job_description: Target job description
    
    Returns:
        Dictionary with comparison analysis
    """
    prompt = f"""
Compare the user's resume against the ideal resume for this job. Provide:
1. Overall score (0-100)
2. ATS score
3. Category-by-category comparison (summary, skills, experience, education)
4. Keyword analysis (found vs missing)
5. Specific improvement suggestions
6. Summary of what the ideal resume should contain

USER RESUME:
{user_resume_text}

JOB DESCRIPTION:
{job_description}

Format as JSON:
{{
  "overall_score": 75,
  "ats_score": 80,
  "comparison_items": [
    {{
      "category": "summary",
      "user_resume": "what user has",
      "ideal_resume": "what ideal has",
      "score": 70,
      "recommendations": ["..."]
    }}
  ],
  "keyword_analysis": {{
    "found": ["keyword1", "keyword2"],
    "missing": ["keyword3", "keyword4"]
  }},
  "improvement_suggestions": ["suggestion1", "suggestion2"],
  "ideal_resume_summary": "description of ideal resume"
}}
"""
    
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: get_gemini_service().model.generate_content(
                prompt,
                GenerationConfig(temperature=0.5, max_output_tokens=4096)
            )
        )
        
        import json
        import re
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        logger.error(f"Error generating resume comparison: {str(e)}")
    
    # Fallback
    return _generate_fallback_comparison(user_resume_text, job_description)


def _generate_fallback_comparison(user_resume_text: str, job_description: str) -> Dict[str, Any]:
    """Generate fallback resume comparison."""
    from skill_engine import calculate_match_score
    from main import calculate_ats_score
    
    score, missing = calculate_match_score(user_resume_text, job_description)
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

