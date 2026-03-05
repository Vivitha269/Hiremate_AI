"""
Resume Generator Service for HireMate AI.
Generates professional resumes in 5 different formats/templates.
"""
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import base64
from io import BytesIO

logger = logging.getLogger(__name__)


class ResumeTemplate:
    """Base class for resume templates."""
    
    TEMPLATES = {
        "modern": "Modern",
        "classic": "Classic", 
        "technical": "Technical",
        "executive": "Executive",
        "entry": "Entry-Level"
    }
    
    INDUSTRIES = {
        "tech": "Technology",
        "finance": "Finance",
        "healthcare": "Healthcare",
        "marketing": "Marketing",
        "engineering": "Engineering",
        "general": "General"
    }
    
    @staticmethod
    def get_available_templates() -> List[Dict[str, str]]:
        """Get list of available resume templates."""
        return [
            {"id": "modern", "name": "Modern", "description": "Sleek design with colored accents, ideal for tech and creative roles"},
            {"id": "classic", "name": "Classic", "description": "Traditional professional layout, perfect for corporate positions"},
            {"id": "technical", "name": "Technical", "description": "Skills-focused layout, best for developers and IT professionals"},
            {"id": "executive", "name": "Executive", "description": "Senior-level format emphasizing leadership and achievements"},
            {"id": "entry", "name": "Entry-Level", "description": "Student-friendly format highlighting education and internships"}
        ]
    
    @staticmethod
    def get_industries() -> List[Dict[str, str]]:
        """Get list of available industries."""
        return [
            {"id": "tech", "name": "Technology"},
            {"id": "finance", "name": "Finance"},
            {"id": "healthcare", "name": "Healthcare"},
            {"id": "marketing", "name": "Marketing"},
            {"id": "engineering", "name": "Engineering"},
            {"id": "general", "name": "General"}
        ]


class ResumeData:
    """Data class for resume information."""
    
    def __init__(self, 
                 full_name: str = "",
                 email: str = "",
                 phone: str = "",
                 location: str = "",
                 linkedin: str = "",
                 portfolio: str = "",
                 summary: str = "",
                 skills: List[str] = None,
                 experience: List[Dict] = None,
                 education: List[Dict] = None,
                 certifications: List[str] = None,
                 languages: List[str] = None,
                 photo_base64: str = None):
        
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.location = location
        self.linkedin = linkedin
        self.portfolio = portfolio
        self.summary = summary
        self.skills = skills or []
        self.experience = experience or []
        self.education = education or []
        self.certifications = certifications or []
        self.languages = languages or []
        self.photo_base64 = photo_base64
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ResumeData':
        """Create ResumeData from dictionary."""
        return cls(
            full_name=data.get("full_name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            location=data.get("location", ""),
            linkedin=data.get("linkedin", ""),
            portfolio=data.get("portfolio", ""),
            summary=data.get("summary", ""),
            skills=data.get("skills", []),
            experience=data.get("experience", []),
            education=data.get("education", []),
            certifications=data.get("certifications", []),
            languages=data.get("languages", []),
            photo_base64=data.get("photo_base64", None)
        )


def generate_modern_resume(data: ResumeData, primary_color: str = "#8b5cf6") -> str:
    """Generate Modern template resume (HTML format)."""
    
    skills_html = ""
    for skill in data.skills:
        skills_html += f'<span class="skill-tag">{skill}</span>'
    
    experience_html = ""
    for exp in data.experience:
        experience_html += f"""
        <div class="experience-item">
            <div class="exp-header">
                <h3>{exp.get('title', 'Position')}</h3>
                <span class="date">{exp.get('duration', '')}</span>
            </div>
            <div class="company">{exp.get('company', 'Company')}</div>
            <p class="description">{exp.get('description', '')}</p>
        </div>
        """
    
    education_html = ""
    for edu in data.education:
        education_html += f"""
        <div class="education-item">
            <div class="edu-header">
                <h3>{edu.get('degree', 'Degree')}</h3>
                <span class="date">{edu.get('year', '')}</span>
            </div>
            <div class="school">{edu.get('institution', 'Institution')}</div>
        </div>
        """
    
    photo_html = ""
    if data.photo_base64:
        photo_html = f'<img src="{data.photo_base64}" alt="Profile Photo" class="profile-photo">'
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{data.full_name} - Resume</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .resume {{ max-width: 800px; margin: 0 auto; background: #fff; }}
        .header {{ background: linear-gradient(135deg, {primary_color} 0%, #f472b6 100%); color: white; padding: 40px; }}
        .header-content {{ display: flex; align-items: center; gap: 30px; }}
        .profile-photo {{ width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 4px solid white; }}
        .name {{ font-size: 32px; font-weight: 700; margin-bottom: 5px; }}
        .contact-info {{ font-size: 14px; opacity: 0.9; }}
        .contact-info span {{ margin-right: 20px; }}
        .summary {{ background: #f8f9fa; padding: 30px 40px; border-left: 4px solid {primary_color}; }}
        .summary h2 {{ color: {primary_color}; font-size: 18px; margin-bottom: 10px; }}
        .content {{ padding: 30px 40px; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ font-size: 18px; color: {primary_color}; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #eee; }}
        .skill-tag {{ display: inline-block; background: {primary_color}20; color: {primary_color}; padding: 6px 14px; border-radius: 20px; margin: 4px; font-size: 13px; font-weight: 500; }}
        .experience-item, .education-item {{ margin-bottom: 20px; }}
        .exp-header, .edu-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .exp-header h3, .edu-header h3 {{ font-size: 16px; font-weight: 600; }}
        .date {{ color: #666; font-size: 13px; }}
        .company, .school {{ color: {primary_color}; font-weight: 500; margin: 4px 0; }}
        .description {{ font-size: 14px; color: #555; margin-top: 8px; }}
        .certifications {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .cert-item {{ background: #f0f0f0; padding: 8px 16px; border-radius: 4px; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="resume">
        <div class="header">
            <div class="header-content">
                {photo_html}
                <div>
                    <div class="name">{data.full_name or 'Your Name'}</div>
                    <div class="contact-info">
                        {f'<span>✉ {data.email}</span>' if data.email else ''}
                        {f'<span>📱 {data.phone}</span>' if data.phone else ''}
                        {f'<span>📍 {data.location}</span>' if data.location else ''}
                    </div>
                    <div class="contact-info">
                        {f'<span>🔗 {data.linkedin}</span>' if data.linkedin else ''}
                        {f'<span>🌐 {data.portfolio}</span>' if data.portfolio else ''}
                    </div>
                </div>
            </div>
        </div>
        
        {f'''
        <div class="summary">
            <h2>Professional Summary</h2>
            <p>{data.summary}</p>
        </div>
        ''' if data.summary else ''}
        
        <div class="content">
            {f'''
            <div class="section">
                <h2 class="section-title">Skills</h2>
                <div class="skills-list">{skills_html}</div>
            </div>
            ''' if data.skills else ''}
            
            {f'''
            <div class="section">
                <h2 class="section-title">Experience</h2>
                {experience_html}
            </div>
            ''' if data.experience else ''}
            
            {f'''
            <div class="section">
                <h2 class="section-title">Education</h2>
                {education_html}
            </div>
            ''' if data.education else ''}
            
            {f'''
            <div class="section">
                <h2 class="section-title">Certifications</h2>
                <div class="certifications">
                    {''.join(f'<span class="cert-item">{cert}</span>' for cert in data.certifications)}
                </div>
            </div>
            ''' if data.certifications else ''}
        </div>
    </div>
</body>
</html>
"""


def generate_classic_resume(data: ResumeData) -> str:
    """Generate Classic template resume."""
    
    skills_html = ", ".join(data.skills) if data.skills else ""
    
    experience_html = ""
    for exp in data.experience:
        experience_html += f"""
        <div class="experience-item">
            <h3>{exp.get('title', 'Position')}</h3>
            <div class="company-date">{exp.get('company', 'Company')} | {exp.get('duration', '')}</div>
            <p>{exp.get('description', '')}</p>
        </div>
        """
    
    education_html = ""
    for edu in data.education:
        education_html += f"""
        <div class="education-item">
            <h3>{edu.get('degree', 'Degree')}</h3>
            <div class="school-date">{edu.get('institution', 'Institution')} | {edu.get('year', '')}</div>
        </div>
        """
    
    photo_html = ""
    if data.photo_base64:
        photo_html = f'<img src="{data.photo_base64}" alt="Photo" class="profile-photo">'
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{data.full_name} - Resume</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Times New Roman', serif; line-height: 1.8; color: #000; background: #fff; }}
        .resume {{ max-width: 800px; margin: 0 auto; padding: 40px; }}
        .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 20px; margin-bottom: 25px; }}
        .header-content {{ display: flex; align-items: center; justify-content: center; gap: 30px; }}
        .profile-photo {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #000; }}
        .name {{ font-size: 28px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; }}
        .contact {{ font-size: 12px; margin-top: 8px; }}
        .contact span {{ margin: 0 10px; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #000; padding-bottom: 5px; margin-bottom: 15px; }}
        .experience-item, .education-item {{ margin-bottom: 15px; }}
        .experience-item h3, .education-item h3 {{ font-size: 14px; font-weight: bold; }}
        .company-date, .school-date {{ font-size: 12px; font-style: italic; }}
        .skills {{ font-size: 12px; }}
    </style>
</head>
<body>
    <div class="resume">
        <div class="header">
            <div class="header-content">
                {photo_html}
                <div>
                    <div class="name">{data.full_name or 'Your Name'}</div>
                    <div class="contact">
                        {f'{data.email} | {data.phone} | {data.location}' if all([data.email, data.phone, data.location]) else ''}
                        {f'<br>{data.linkedin}' if data.linkedin else ''}
                        {f'<br>{data.portfolio}' if data.portfolio else ''}
                    </div>
                </div>
            </div>
        </div>
        
        {f'''
        <div class="section">
            <h2 class="section-title">Professional Summary</h2>
            <p>{data.summary}</p>
        </div>
        ''' if data.summary else ''}
        
        {f'''
        <div class="section">
            <h2 class="section-title">Skills</h2>
            <div class="skills">{skills_html}</div>
        </div>
        ''' if data.skills else ''}
        
        {f'''
        <div class="section">
            <h2 class="section-title">Professional Experience</h2>
            {experience_html}
        </div>
        ''' if data.experience else ''}
        
        {f'''
        <div class="section">
            <h2 class="section-title">Education</h2>
            {education_html}
        </div>
        ''' if data.education else ''}
        
        {f'''
        <div class="section">
            <h2 class="section-title">Certifications</h2>
            <p>{', '.join(data.certifications)}</p>
        </div>
        ''' if data.certifications else ''}
    </div>
</body>
</html>
"""


def generate_technical_resume(data: ResumeData) -> str:
    """Generate Technical template resume - ideal for developers."""
    
    # Group skills by category
    tech_skills = [s for s in data.skills if any(t in s.lower() for t in ['python', 'java', 'javascript', 'react', 'node', 'aws', 'docker', 'sql', 'api', 'git'])]
    soft_skills = [s for s in data.skills if s not in tech_skills]
    
    tech_skills_html = " | ".join([f'<span class="skill">{s}</span>' for s in tech_skills]) if tech_skills else ""
    soft_skills_html = ", ".join(soft_skills) if soft_skills else ""
    
    experience_html = ""
    for exp in data.experience:
        # Extract tech stack if mentioned
        tech_stack = exp.get('tech_stack', [])
        tech_stack_html = " | ".join([f'<span class="tech-item">{t}</span>' for t in tech_stack]) if tech_stack else ""
        
        experience_html += f"""
        <div class="experience-item">
            <div class="exp-title">{exp.get('title', 'Position')}</div>
            <div class="exp-company">{exp.get('company', 'Company')} | {exp.get('duration', '')}</div>
            {f'<div class="tech-stack">{tech_stack_html}</div>' if tech_stack_html else ''}
            <div class="exp-desc">{exp.get('description', '')}</div>
        </div>
        """
    
    photo_html = ""
    if data.photo_base64:
        photo_html = f'<img src="{data.photo_base64}" alt="Profile" class="profile-photo">'
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{data.full_name} - Technical Resume</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Consolas', 'Monaco', monospace; line-height: 1.6; color: #1a1a1a; background: #f5f5f5; }}
        .resume {{ max-width: 850px; margin: 0 auto; background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: #1a1a1a; color: #00ff00; padding: 30px; }}
        .header-content {{ display: flex; align-items: center; gap: 25px; }}
        .profile-photo {{ width: 100px; height: 100px; border-radius: 8px; object-fit: cover; border: 2px solid #00ff00; }}
        .name {{ font-size: 26px; font-weight: bold; color: #00ff00; }}
        .contact {{ font-size: 12px; color: #aaa; margin-top: 5px; }}
        .contact span {{ margin-right: 15px; }}
        .summary {{ background: #f0f0f0; padding: 20px 30px; border-left: 4px solid #00ff00; }}
        .summary h2 {{ font-size: 14px; color: #1a1a1a; margin-bottom: 8px; text-transform: uppercase; }}
        .content {{ padding: 25px 30px; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ font-size: 14px; font-weight: bold; text-transform: uppercase; color: #1a1a1a; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #00ff00; }}
        .skill, .tech-item {{ display: inline-block; background: #1a1a1a; color: #00ff00; padding: 4px 10px; border-radius: 3px; margin: 3px; font-size: 11px; }}
        .tech-stack {{ margin-top: 8px; }}
        .experience-item {{ margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-left: 3px solid #00ff00; }}
        .exp-title {{ font-size: 15px; font-weight: bold; color: #1a1a1a; }}
        .exp-company {{ font-size: 12px; color: #666; margin: 3px 0; }}
        .exp-desc {{ font-size: 13px; margin-top: 8px; }}
    </style>
</head>
<body>
    <div class="resume">
        <div class="header">
            <div class="header-content">
                {photo_html}
                <div>
                    <div class="name">{data.full_name or 'Your Name'}</div>
                    <div class="contact">
                        {f'📧 {data.email}' if data.email else ''}
                        {f'📱 {data.phone}' if data.phone else ''}
                        {f'📍 {data.location}' if data.location else ''}
                    </div>
                    <div class="contact">
                        {f'🔗 {data.linkedin}' if data.linkedin else ''}
                        {f'🌐 {data.portfolio}' if data.portfolio else ''}
                    </div>
                </div>
            </div>
        </div>
        
        {f'''
        <div class="summary">
            <h2>> Summary</h2>
            <p>{data.summary}</p>
        </div>
        ''' if data.summary else ''}
        
        <div class="content">
            {f'''
            <div class="section">
                <h2 class="section-title">> Technical Skills</h2>
                <div>{tech_skills_html}</div>
                {f'<div style="margin-top: 10px; color: #666;">Soft Skills: {soft_skills_html}</div>' if soft_skills_html else ''}
            </div>
            ''' if data.skills else ''}
            
            {f'''
            <div class="section">
                <h2 class="section-title">> Professional Experience</h2>
                {experience_html}
            </div>
            ''' if data.experience else ''}
            
            {f'''
            <div class="section">
                <h2 class="section-title">> Education</h2>
                {''.join(f'<div class="experience-item"><div class="exp-title">{edu.get("degree", "")}</div><div class="exp-company">{edu.get("institution", "")} | {edu.get("year", "")}</div></div>' for edu in data.education)}
            </div>
            ''' if data.education else ''}
        </div>
    </div>
</body>
</html>
"""


def generate_executive_resume(data: ResumeData) -> str:
    """Generate Executive template - for senior positions."""
    
    skills_html = ", ".join(data.skills) if data.skills else ""
    
    experience_html = ""
    for exp in data.experience:
        achievements = exp.get('achievements', [])
        achievements_html = "".join([f'<li>{a}</li>' for a in achievements]) if achievements else f'<li>{exp.get("description", "")}</li>'
        
        experience_html += f"""
        <div class="experience-item">
            <h3>{exp.get('title', 'Position')}</h3>
            <div class="company">{exp.get('company', 'Company')}</div>
            <div class="duration">{exp.get('duration', '')}</div>
            <ul class="achievements">{achievements_html}</ul>
        </div>
        """
    
    photo_html = ""
    if data.photo_base64:
        photo_html = f'<img src="{data.photo_base64}" alt="Photo" class="profile-photo">'
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{data.full_name} - Executive Resume</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Garamond', 'Georgia', serif; line-height: 1.7; color: #2c2c2c; background: #fafafa; }}
        .resume {{ max-width: 850px; margin: 0 auto; background: #fff; border: 1px solid #ddd; }}
        .header {{ background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%); color: white; padding: 40px; text-align: center; }}
        .header-content {{ display: flex; align-items: center; justify-content: center; gap: 30px; }}
        .profile-photo {{ width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 3px solid white; }}
        .name {{ font-size: 32px; font-weight: bold; letter-spacing: 1px; }}
        .title-bar {{ font-size: 16px; opacity: 0.9; margin-top: 5px; }}
        .contact {{ font-size: 13px; margin-top: 15px; opacity: 0.85; }}
        .contact span {{ margin: 0 12px; }}
        .summary {{ background: #f7f7f7; padding: 30px 40px; text-align: center; }}
        .summary p {{ font-size: 15px; max-width: 700px; margin: 0 auto; font-style: italic; }}
        .content {{ padding: 35px 40px; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ font-size: 16px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; color: #1e3a5f; margin-bottom: 18px; padding-bottom: 8px; border-bottom: 2px solid #1e3a5f; }}
        .skills {{ font-size: 14px; }}
        .experience-item {{ margin-bottom: 25px; padding-left: 15px; border-left: 3px solid #1e3a5f; }}
        .experience-item h3 {{ font-size: 17px; font-weight: bold; color: #1e3a5f; }}
        .company {{ font-size: 14px; font-weight: 600; color: #4a5568; margin: 3px 0; }}
        .duration {{ font-size: 12px; color: #718096; margin-bottom: 10px; }}
        .achievements {{ font-size: 13px; margin-left: 18px; }}
        .achievements li {{ margin-bottom: 5px; }}
    </style>
</head>
<body>
    <div class="resume">
        <div class="header">
            <div class="header-content">
                {photo_html}
                <div>
                    <div class="name">{data.full_name or 'Your Name'}</div>
                    <div class="title-bar">Senior Executive</div>
                    <div class="contact">
                        {f'{data.email} | {data.phone}' if data.email and data.phone else ''}
                        {f' | {data.location}' if data.location else ''}
                    </div>
                    <div class="contact">
                        {f'{data.linkedin}' if data.linkedin else ''}
                    </div>
                </div>
            </div>
        </div>
        
        {f'''
        <div class="summary">
            <p>"{data.summary}"</p>
        </div>
        ''' if data.summary else ''}
        
        <div class="content">
            {f'''
            <div class="section">
                <h2 class="section-title">Core Competencies</h2>
                <div class="skills">{skills_html}</div>
            </div>
            ''' if data.skills else ''}
            
            {f'''
            <div class="section">
                <h2 class="section-title">Professional Experience</h2>
                {experience_html}
            </div>
            ''' if data.experience else ''}
            
            {f'''
            <div class="section">
                <h2 class="section-title">Education</h2>
                {''.join(f'<div class="experience-item"><h3>{edu.get("degree", "")}</h3><div class="company">{edu.get("institution", "")}</div><div class="duration">{edu.get("year", "")}</div></div>' for edu in data.education)}
            </div>
            ''' if data.education else ''}
        </div>
    </div>
</body>
</html>
"""


def generate_entry_resume(data: ResumeData) -> str:
    """Generate Entry-Level template - for students and fresh graduates."""
    
    skills_html = " | ".join([f'<span class="skill">{s}</span>' for s in data.skills]) if data.skills else ""
    
    # Include projects and extracurricular for entry-level
    projects = data.experience  # Use experience field for projects
    
    experience_html = ""
    for exp in data.experience:
        experience_html += f"""
        <div class="exp-item">
            <h3>{exp.get('title', 'Position/Project')}</h3>
            <div class="org">{exp.get('company', 'Organization')} | {exp.get('duration', '')}</div>
            <p>{exp.get('description', '')}</p>
        </div>
        """
    
    projects_html = ""
    for proj in projects[:3]:  # Show up to 3 projects
        projects_html += f"""
        <div class="project-item">
            <h3>{proj.get('title', 'Project Name')}</h3>
            <div class="tech">{proj.get('tech_stack', '')}</div>
            <p>{proj.get('description', '')}</p>
        </div>
        """
    
    photo_html = ""
    if data.photo_base64:
        photo_html = f'<img src="{data.photo_base64}" alt="Photo" class="profile-photo">'
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{data.full_name} - Resume</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Verdana', 'Arial', sans-serif; line-height: 1.6; color: #333; background: #fff; }}
        .resume {{ max-width: 800px; margin: 0 auto; }}
        .header {{ background: #4a90d9; color: white; padding: 35px; display: flex; align-items: center; gap: 25px; }}
        .profile-photo {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid white; }}
        .name-section {{ flex: 1; }}
        .name {{ font-size: 28px; font-weight: bold; }}
        .tagline {{ font-size: 14px; opacity: 0.9; margin-top: 3px; }}
        .contact-row {{ font-size: 12px; margin-top: 10px; }}
        .contact-row span {{ margin-right: 15px; }}
        .summary {{ padding: 25px 35px; background: #f4f7f6; }}
        .summary h2 {{ font-size: 14px; color: #4a90d9; margin-bottom: 8px; text-transform: uppercase; }}
        .content {{ padding: 25px 35px; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ font-size: 15px; font-weight: bold; color: #4a90d9; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }}
        .skill {{ display: inline-block; background: #e8f4fd; color: #4a90d9; padding: 5px 12px; border-radius: 15px; margin: 3px; font-size: 12px; }}
        .exp-item, .project-item, .edu-item {{ margin-bottom: 15px; padding: 12px; background: #fafafa; border-radius: 5px; }}
        .exp-item h3, .project-item h3, .edu-item h3 {{ font-size: 14px; font-weight: bold; color: #333; }}
        .org, .tech {{ font-size: 12px; color: #666; font-weight: 500; margin: 3px 0; }}
        .activities {{ font-size: 13px; color: #555; }}
        .activities li {{ margin-bottom: 5px; }}
    </style>
</head>
<body>
    <div class="resume">
        <div class="header">
            {photo_html}
            <div class="name-section">
                <div class="name">{data.full_name or 'Your Name'}</div>
                <div class="tagline">Aspiring Professional | Recent Graduate</div>
                <div class="contact-row">
                    {f'✉ {data.email}' if data.email else ''}
                    {f'📱 {data.phone}' if data.phone else ''}
                    {f'📍 {data.location}' if data.location else ''}
                </div>
                <div class="contact-row">
                    {f'🔗 {data.linkedin}' if data.linkedin else ''}
                </div>
            </div>
        </div>
        
        {f'''
        <div class="summary">
            <h2>About Me</h2>
            <p>{data.summary}</p>
        </div>
        ''' if data.summary else ''}
        
        <div class="content">
            {f'''
            <div class="section">
                <h2 class="section-title">Skills</h2>
                <div>{skills_html}</div>
            </div>
            ''' if data.skills else ''}
            
            {f'''
            <div class="section">
                <h2 class="section-title">Education</h2>
                {''.join(f'<div class="edu-item"><h3>{edu.get("degree", "")}</h3><div class="org">{edu.get("institution", "")} | {edu.get("year", "")}</div>{f"<p>{edu.get('description', '')}</p>" if edu.get("description") else ""}</div>' for edu in data.education)}
            </div>
            ''' if data.education else ''}
            
            {f'''
            <div class="section">
                <h2 class="section-title">Projects / Internships</h2>
                {experience_html}
            </div>
            ''' if data.experience else ''}
        </div>
    </div>
</body>
</html>
"""


def generate_resume(template_id: str, data: ResumeData, primary_color: str = "#8b5cf6") -> str:
    """
    Generate resume in specified template format.
    
    Args:
        template_id: Template type (modern, classic, technical, executive, entry)
        data: ResumeData object with all resume information
        primary_color: Primary color for template (hex code)
    
    Returns:
        HTML string of the generated resume
    """
    generators = {
        "modern": lambda: generate_modern_resume(data, primary_color),
        "classic": lambda: generate_classic_resume(data),
        "technical": lambda: generate_technical_resume(data),
        "executive": lambda: generate_executive_resume(data),
        "entry": lambda: generate_entry_resume(data)
    }
    
    generator = generators.get(template_id, generators["modern"])
    return generator()


def convert_photo_to_base64(photo_data: bytes) -> str:
    """Convert photo bytes to base64 data URL."""
    import base64
    return f"data:image/jpeg;base64,{base64.b64encode(photo_data).decode('utf-8')}"


def parse_resume_from_text(resume_text: str) -> ResumeData:
    """
    Parse resume data from extracted text using pattern matching.
    
    Args:
        resume_text: Raw resume text
    
    Returns:
        ResumeData object with parsed information
    """
    data = ResumeData()
    
    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
    if email_match:
        data.email = email_match.group()
    
    # Extract phone
    phone_match = re.search(r'(\+?1?[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text)
    if phone_match:
        data.phone = phone_match.group()
    
    # Extract LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', resume_text, re.IGNORECASE)
    if linkedin_match:
        data.linkedin = linkedin_match.group()
    
    # Extract common section headers
    sections = {
        'summary': r'(?:professional\s+summary|summary|profile)(.*?)(?=(?:experience|education|skills|employment|$))',
        'skills': r'(?:skills|technical\s+skills|technologies)(.*?)(?=(?:experience|education|employment|$))',
        'experience': r'(?:experience|employment|work\s+history)(.*?)(?=(?:education|skills|$))',
        'education': r'(?:education|academic)(.*?)(?=(?:experience|skills|$))'
    }
    
    for section, pattern in sections.items():
        match = re.search(pattern, resume_text, re.IGNORECASE | re.DOTALL)
        if match:
            setattr(data, section, match.group(1).strip()[:500])
    
    return data

