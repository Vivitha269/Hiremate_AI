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

## 📋 Table of Contents
- [Features](#✨-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 📊 Resume Analysis
- **PDF Resume Parsing** - Extract and analyze text from PDF resumes
- **Skill Matching** - Intelligent matching between resume skills and job requirements
- **ATS Scoring** - Calculate Applicant Tracking System compatibility score
- **AI Summaries** - Generate improved professional summaries using Google Gemini
- **Cover Letters** - Create tailored cover letters for specific job applications
- **Resume Tips** - Get actionable suggestions to improve your resume

### 📄 Resume Generator
- **5 Unique Templates** - Modern, Classic, Technical, Executive, Entry-Level
- **Photo Support** - Add your photo to resumes (optional)
- **Custom Colors** - Choose from 6 accent colors
- **Live Preview** - See your resume before downloading
- **PDF Export** - Download professional resumes instantly

### 🎤 Interview Preparation
- **AI Interview Questions** - Generate personalized questions based on your resume and target job
- **Technical Questions** - Job-specific technical queries
- **Behavioral Questions** - Situational and experience-based questions
- **Answer Guidance** - Tips on how to answer each question
- **Sample Answers** - Example responses for reference

### 📚 Skills Gap Analysis
- **Missing Skills Detection** - Identify skills you need to develop
- **Learning Resources** - Get course and tutorial recommendations
- **Priority Ranking** - Know which skills to learn first
- **Gap Score** - Measure your readiness for the role

### ⚖️ Resume Comparison
- **Ideal Resume Match** - Compare your resume against the ideal
- **Keyword Analysis** - See which keywords you're missing
- **Improvement Suggestions** - Get actionable recommendations
- **Side-by-Side Comparison** - Visual breakdown of strengths and gaps

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **AI Model** | Google Gemini 2.0 Flash |
| **Frontend** | HTML5, CSS3, JavaScript |
| **PDF Processing** | PyPDF2 |
| **Rate Limiting** | SlowAPI |
| **API Documentation** | Swagger UI, ReDoc |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Google Gemini API Key (free at [AI Studio](https://aistudio.google.com/app/apikey))
- Git

### One-Command Setup
```bash
# Windows
run.bat

# Linux/Mac
bash run.sh
```

The application will start automatically at `http://127.0.0.1:8000`

---

## 🌐 Hosting & Deployment

### Option 1: Railway (Recommended - Free)
Railway offers free hosting with automatic deployments from GitHub.

1. **Connect Repository**
   - Go to [Railway.app](https://railway.app)
   - Sign up/Login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `Hiremate_AI` repository

2. **Configure Environment Variables**
   - Go to your project settings
   - Add environment variable: `GEMINI_API_KEY=your_api_key_here`

3. **Deploy**
   - Railway will automatically detect `railway.json` and deploy
   - Your app will be live at `https://your-project-name.up.railway.app`

### Option 2: Render (Free Tier Available)
Render provides free web service hosting.

1. **Connect Repository**
   - Go to [Render.com](https://render.com)
   - Sign up/Login
   - Click "New +" → "Web Service"
   - Connect your GitHub repo

2. **Configure Build Settings**
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**
   - `GEMINI_API_KEY=your_api_key_here`
   - `ENVIRONMENT=production`

### Option 3: Docker Deployment
Deploy anywhere that supports Docker.

```bash
# Build and run locally
docker-compose up --build

# Or build manually
docker build -t hiremate-ai .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key hiremate-ai
```

### Option 4: Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
heroku config:set GEMINI_API_KEY=your_api_key_here
git push heroku main
```

### Option 5: Vercel (Frontend Only)
Vercel can host the API, but file uploads may have limitations.

```bash
# Install Vercel CLI
npm i -g vercel
vercel --prod
```

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Vivitha269/Hiremate_AI.git
cd Hiremate_AI
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Google Gemini API Key
# GEMINI_API_KEY=your_api_key_here
```

### 5. Run the Application
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Visit `http://127.0.0.1:8000` in your browser

---

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_api_key_here

# Application Settings
API_TITLE=HireMate AI
API_VERSION=2.0.0
ENVIRONMENT=development

# Server Settings
HOST=127.0.0.1
PORT=8000
```

### Get Google Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key
4. Paste it in the `.env` file as `GEMINI_API_KEY`

---

## 📖 Usage

### Web Interface
Open `http://127.0.0.1:8000` in your browser to access the interactive frontend.

### API Documentation
- **Swagger UI**: `http://127.0.0.1:8000/api/docs`
- **ReDoc**: `http://127.0.0.1:8000/api/redoc`

---

## 📡 API Endpoints

### Resume Analysis
```bash
POST /api/analyze
Parameters:
  - resume_file: PDF file (multipart)
  - job_description: string
Returns: Match score, ATS score, missing skills, tips
```

### Resume Generation
```bash
POST /api/resume/generate
Body: ResumeGenerateRequest
  - template: string (modern, classic, technical, executive, entry-level)
  - resume_data: object
  - accent_color: string (hex color)
Returns: PDF resume as file download
```

### Interview Questions
```bash
POST /api/interview/questions
Body: InterviewQuestionsRequest
  - resume_text: string
  - job_description: string
  - num_questions: integer
Returns: List of AI-generated interview questions
```

### Skills Gap Analysis
```bash
POST /api/skills/gap-analysis
Body: SkillsGapAnalysisRequest
  - current_skills: list
  - required_skills: list
  - job_title: string
Returns: Gap analysis with learning resources
```

### Resume Comparison
```bash
POST /api/resume/compare
Body: ResumeComparisonRequest
  - user_resume_text: string
  - ideal_resume_text: string
Returns: Comparison metrics and suggestions
```

### Health Check
```bash
GET /api/health
Returns: Application status and version
```

---

## 📁 Project Structure

```
Hiremate_AI/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and logging setup
├── exceptions.py          # Custom exception classes
├── models.py              # Pydantic request/response models
├── gemini_service.py      # Google Gemini API integration
├── pdf_utils.py           # PDF parsing utilities
├── skill_engine.py        # Skill matching algorithms
├── resume_generator.py    # Resume PDF generation
├── index.html             # Frontend web interface
├── test_main.py           # Unit tests
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (confidential)
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
├── run.bat               # Windows startup script
├── run.sh                # Linux/Mac startup script
├── LICENSE               # MIT License
├── README.md             # This file
└── TODO.md               # Implementation roadmap
```

---

## 🧪 Testing

### Run Unit Tests
```bash
pytest test_main.py -v
```

### Test API Endpoints
Use the Swagger UI at `http://127.0.0.1:8000/api/docs` to test endpoints interactively.

---

## 🔧 Troubleshooting

### Issue: `ModuleNotFoundError`
**Solution:** Ensure virtual environment is activated and dependencies are installed
```bash
pip install -r requirements.txt
```

### Issue: `GEMINI_API_KEY not found`
**Solution:** Create `.env` file with your API key
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Issue: Port 8000 already in use
**Solution:** Use a different port
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

### Issue: PDF Upload Fails
**Solution:** Ensure PDF file is:
- Less than 5MB
- Valid PDF format
- Not password protected

### Issue: Slow Response Times
**Solution:** 
- Check internet connection (API calls to Google Gemini)
- Reduce job description length (max 10,000 chars)
- Wait for rate limiting cooldown (10 requests/minute)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on [GitHub Issues](https://github.com/Vivitha269/Hiremate_AI/issues)
- Check existing [documentation](https://github.com/Vivitha269/Hiremate_AI/wiki)

---

## 🌟 Acknowledgments

- Google Gemini API for AI capabilities
- FastAPI for the web framework
- PyPDF2 for PDF processing
- The open-source community

---

**Made with ❤️ by Vivitha**

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
- GitHub: [Vivitha](https://github.com/Vivitha269)
- LinkedIn: [Vivitha](https://www.linkedin.com/in/a-vivitha-a-vivitha-36227730a?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)

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

