@echo off
REM HireMate AI - Windows Startup Script

echo.
echo ========================================
echo    HireMate AI - Starting Application
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Run the application
echo.
echo Starting FastAPI server...
echo.
echo ========================================
echo    HireMate AI is running!
echo    Open: http://127.0.0.1:8000
echo    Docs: http://127.0.0.1:8000/api/docs
echo ========================================
echo.

python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause
