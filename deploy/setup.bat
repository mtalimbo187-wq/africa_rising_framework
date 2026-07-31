@echo off
REM Africa Rising Framework Setup (Windows)

echo ======================================
echo Africa Rising Framework Setup
echo ======================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if errorlevel 1 (
    echo Error: Python not installed or not in PATH
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

REM Create directory structure
echo Creating directory structure...
if not exist "output\logs" mkdir output\logs
if not exist "output\cache" mkdir output\cache
if not exist "output\projects" mkdir output\projects
if not exist "cache\narration" mkdir cache\narration
if not exist "cache\visuals" mkdir cache\visuals
if not exist "cache\captions" mkdir cache\captions
if not exist "cache\assets" mkdir cache\assets
if not exist "prompts" mkdir prompts

REM Initialize prompt library
echo Initializing prompt library...
python << EOF
from core.prompt_manager import initialize_prompt_library
initialize_prompt_library()
print("Prompts initialized")
EOF

REM Check FFmpeg installation
echo Checking FFmpeg...
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo Error: FFmpeg not installed. Install from https://ffmpeg.org/download.html
    exit /b 1
)
ffmpeg -version | findstr /R "version"

REM Check Whisper installation
echo Checking Whisper...
where whisper >nul 2>nul
if errorlevel 1 (
    echo Installing Whisper...
    pip install openai-whisper
)

REM Setup environment variables
echo Setting up environment variables...
if not exist ".env" (
    (
        echo # Africa Rising Framework Configuration
        echo set ANTHROPIC_API_KEY=your_key_here
        echo set ELEVENLABS_API_KEY=your_key_here
        echo set PEXELS_API_KEY=your_key_here
        echo set TAVILY_API_KEY=your_key_here
        echo set GROK_API_KEY=your_key_here
        echo set GOOGLE_API_KEY=your_key_here
        echo set RUNWAY_API_KEY=your_key_here
    ) > .env
    echo Created .env file - update with your API keys
) else (
    echo .env already exists
)

REM Test basic imports
echo Testing imports...
python << EOF
try:
    from agents.base_agent import BaseAgent
    from core.schemas import Shot, Asset, Timeline
    from core.prompt_manager import PromptManager
    from core.license_manager import LicenseManager
    from core.advanced_qa import AdvancedQAChecker
    from core.observability import ProductionLogger
    print("✓ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
EOF

REM Final summary
echo.
echo ======================================
echo Setup complete!
echo ======================================
echo.
echo Next steps:
echo 1. Update .env with your API keys
echo 2. Run: python pipeline.py --help
echo 3. Check config.yaml for settings
echo.
echo Documentation:
echo - README.md - Overview
echo - ARCHITECTURE.md - System design
echo - QUICKSTART.md - Getting started
echo.
pause
