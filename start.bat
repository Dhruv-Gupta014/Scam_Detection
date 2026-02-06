@echo off
REM Quick start script for Agentic Honey-Pot API on Windows

echo ================================
echo Agentic Honey-Pot API - Quick Start (Windows)
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    exit /b 1
)

echo Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist .env (
    echo.
    echo Creating .env file...
    (
        echo API_PORT=5000
        echo API_KEY=scam-detection-key-2026
        echo DEBUG=False
    ) > .env
)

REM Start the application
echo.
echo ================================
echo Starting API Server...
echo ================================
echo.
echo API will be available at: http://localhost:5000
echo API Key: scam-detection-key-2026
echo.
echo Test the API with:
echo   curl http://localhost:5000/health
echo.
echo Run test suite with:
echo   python test_api.py
echo.

python app.py

pause
