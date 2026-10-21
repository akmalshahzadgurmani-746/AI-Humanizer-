@echo off
title ScholarStyle App Launcher
echo =======================================================
echo     ScholarStyle - AI Academic Rewriter Launcher
echo =======================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python.
    pause
    exit /b
)

:: Check for Node / NPM
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js/NPM is not installed or not in PATH. Please install Node.js.
    pause
    exit /b
)

echo [1/3] Checking and installing Python dependencies...
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some python dependencies failed to install. Continuing...
)

echo.
echo [2/3] Starting backend server (FastAPI)...
:: Starts FastAPI in a new CMD window
start "ScholarStyle Backend" cmd /c "cd backend && python run.py"

echo.
echo [3/3] Starting frontend server (Vite)...
:: Starts Vite React in a new CMD window
start "ScholarStyle Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo =======================================================
echo  ScholarStyle is launching!
echo  - Backend running at: http://127.0.0.1:8000
echo  - Frontend running at: http://localhost:5173 (opening in browser...)
echo =======================================================
echo.

:: Wait 3 seconds for servers to initialize
timeout /t 3 /nobreak >nul

:: Open browser
start http://localhost:5173

echo Process complete. Keep the backend and frontend command windows open.
pause
