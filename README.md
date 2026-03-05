# 🎯 HireMate AI

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-00a393?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-8E8E8E?style=for-the-badge&logo=google" alt="Gemini">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge">
</p>

> 🚀 AI-powered resume analyzer that helps job seekers land their dream jobs

HireMate AI is a smart resume analysis tool that matches your resume against job descriptions, calculates ATS compatibility scores, generates AI-powered professional summaries, tailored cover letters, and provides comprehensive interview preparation tools.

---

## ✨ Features

### 📊 Resume Analysis
- **PDF Resume Parsing** - Extract and analyze text from PDF resumes
- **Skill Matching** - Intelligent matching between resume skills and job requirements
- **ATS Scoring** - Calculate Applicant Tracking System compatibility score
- **AI Summaries** - Generate improved professional summaries using Google Gemini
- **Cover Letters** - Create tailored cover letters for specific job applications
- **Resume Tips** - Get actionable suggestions to improve your resume

### 📄 Resume Generator (NEW!)
- **5 Unique Templates** - Modern, Classic, Technical, Executive, Entry-Level
- **Photo Support** - Add your photo to resumes (optional)
- **Custom Colors** - Choose from 6 accent colors
- **Live Preview** - See your resume before downloading
- **PDF Export** - Download professional resumes instantly

### 🎤 Interview Preparation (NEW!)
- **AI Interview Questions** - Generate personalized questions based on your resume and target job
- **Technical Questions** - Job-specific technical queries
- **Behavioral Questions** - Situational and experience-based questions
- **Answer Guidance** - Tips on how to answer each question
- **Sample Answers** - Example responses for reference

### 📚 Skills Gap Analysis (NEW!)
- **Missing Skills Detection** - Identify skills you need to develop
- **Learning Resources** - Get course and tutorial recommendations
- **Priority Ranking** - Know which skills to learn first
- **Gap Score** - Measure your readiness for the role

### ⚖️ Resume Comparison (NEW!)
- **Ideal Resume Match** - Compare your resume against the ideal
- **Keyword Analysis** - See which keywords you're missing
- **Improvement Suggestions** - Get actionable recommendations
- **Side-by-Side Comparison** - Visual breakdown of strengths and gaps

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Backend** | Python, FastAPI |
| **AI/ML** | Google Gemini 2.0 Flash |
| **PDF Processing** | PyPDF2 |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Visualization** | Chart.js |
| **PDF Generation** | jsPDF |
| **API Documentation** | Swagger UI, ReDoc |

---

## 📋 Prerequisites

- Python 3.11 or higher
- Google Gemini API Key
- Modern web browser

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/hiremate-ai.git
cd hiremate-ai
```

### 2. Create virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file and add your API key:

```bash
copy .env.example .env
```

Edit `.env` and add your Google Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

> 🔑 Get your free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### 5. Run the application

```bash
python main.py
```

The application will be available at `http://localhost:8000`

---

## 📖 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve the web UI |
| `/api/health` | GET | Health check endpoint |
| `/api/analyze` | POST | Analyze resume against job |

### Analyze Endpoint

```bash
POST /api/analyze
Content-Type: multipart/form-data

Parameters:
- resume_file: PDF file (max 5MB)
- job_description: Text string

Response:
{
  "match_score": 85.5,
  "ats_score": 78.0,
  "matched_skills": [...],
  "missing_skills": ["python", "react"],
  "improved_summary": "...",
  "cover_letter": "...",
  "resume_tips": [...]
}
```

---

## 🎨 Project Structure

```
hiremate-ai/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration and settings
├── models.py            # Pydantic data models
├── exceptions.py        # Custom exception classes
├── skill_engine.py     # Skill matching algorithm
├── gemini_service.py    # Google Gemini AI integration
├── pdf_utils.py         # PDF text extraction
├── index.html           # Frontend web interface
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

---

## 💡 Usage

1. **Open the web app** - Navigate to http://localhost:8000
2. **Upload your resume** - Drag & drop or click to select a PDF
3. **Paste job description** - Copy and paste the job requirements
4. **Click Analyze** - Get instant feedback on your match
5. **Review results** - Check your match score, missing skills, and AI suggestions
6. **Download report** - Export your analysis as PDF

---

## 🔧 Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_FILE_SIZE_MB` | 5 | Maximum resume file size |
| `RATE_LIMIT_PER_MINUTE` | 10 | API rate limit |
| `GEMINI_MODEL` | gemini-2.0-flash | AI model to use |
| `MAX_TOKENS_SUMMARY` | 500 | Max tokens for summary |
| `MAX_TOKENS_COVER_LETTER` | 1000 | Max tokens for cover letter |

---

## 🐳 Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY .env.example .env

EXPOSE 8000

CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t hiremate-ai .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key hiremate-ai
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgments

- [Google Gemini API](https://deepmind.google/technologies/gemini) for AI capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the amazing framework
- [Chart.js](https://www.chartjs.org/) for visualizations
- All contributors and testers

---

<p align="center">
  Made with ❤️ for job seekers everywhere
</p>

