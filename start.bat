@echo off
REM =============================================================================
REM CALLBOT JULIE - COMPLETE SETUP & START SCRIPT
REM =============================================================================
REM Run: start.bat
REM =============================================================================

echo.
echo =============================================
echo        CALLBOT JULIE - AI DREAMERS
echo      Complete Setup and Launch Script
echo =============================================
echo.

set PROJECT_ROOT=%~dp0

REM =============================================================================
REM STEP 1: Check Python Virtual Environment
REM =============================================================================
echo [STEP 1/6] Checking Python virtual environment...
if not exist "%PROJECT_ROOT%venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment found.
)
echo.

REM =============================================================================
REM STEP 2: Install Python Dependencies
REM =============================================================================
echo [STEP 2/6] Installing Python dependencies...
call "%PROJECT_ROOT%venv\Scripts\activate.bat"
pip install -r "%PROJECT_ROOT%requirements.txt" --quiet
pip install -r "%PROJECT_ROOT%Dashboard\backend\requirements.txt" --quiet
echo Python dependencies installed.
echo.

REM =============================================================================
REM STEP 3: Install Node.js Dependencies
REM =============================================================================
echo [STEP 3/6] Installing Node.js dependencies...
cd /d "%PROJECT_ROOT%Dashboard"
if not exist "node_modules" (
    echo Running npm install...
    npm install
) else (
    echo Node modules found.
)
cd /d "%PROJECT_ROOT%"
echo Node.js dependencies ready.
echo.

REM =============================================================================
REM STEP 4: Start Callbot Server (Twilio)
REM =============================================================================
echo [STEP 4/6] Starting Twilio Server (port 3000)...
start "Callbot Server - Port 3000" cmd /k "cd /d %PROJECT_ROOT% && venv\Scripts\activate && python app/twilio_server.py"
timeout /t 3 /nobreak > nul
echo.

REM =============================================================================
REM STEP 5: Start Dashboard Backend
REM =============================================================================
echo [STEP 5/6] Starting Dashboard API (port 3001)...
start "Dashboard Backend - Port 3001" cmd /k "cd /d %PROJECT_ROOT%Dashboard\backend && %PROJECT_ROOT%venv\Scripts\activate && uvicorn app.main:app --reload --port 3001"
timeout /t 2 /nobreak > nul
echo.

REM =============================================================================
REM STEP 6: Start Dashboard Frontend
REM =============================================================================
echo [STEP 6/6] Starting Dashboard UI (port 5173)...
start "Dashboard Frontend - Port 5173" cmd /k "cd /d %PROJECT_ROOT%Dashboard && npm run dev"
timeout /t 2 /nobreak > nul
echo.

REM =============================================================================
REM COMPLETE
REM =============================================================================
echo.
echo =============================================
echo         ALL SERVICES STARTED!
echo =============================================
echo.
echo  Services Running:
echo  -----------------------------------------
echo  [1] Callbot Server:  http://localhost:3000
echo  [2] Dashboard API:   http://localhost:3001
echo  [3] Dashboard UI:    http://localhost:5173
echo  -----------------------------------------
echo.
echo  Next Steps:
echo  1. Run 'ngrok http 3000' in a new terminal
echo  2. Copy the ngrok HTTPS URL
echo  3. Configure it in Twilio Console as webhook
echo.
echo =============================================
echo.

set /p NGROK="Start ngrok now? (Y/N): "
if /i "%NGROK%"=="Y" (
    echo Starting ngrok...
    start "ngrok" cmd /k "ngrok http 3000"
)

echo.
echo Done! Press any key to exit...
pause > nul
