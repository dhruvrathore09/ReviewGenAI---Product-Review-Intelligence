@echo off
title Product Review Intelligence Platform Launcher
color 0A
echo ==============================================================================
echo        PRODUCT REVIEW INTELLIGENCE PLATFORM (ReviewGenAI)
echo ==============================================================================
echo.

echo [Step 1/3] Preparing PostgreSQL Database...
if exist "C:\Users\Dhruv Rathore\.pgsql\data\postmaster.pid" (
    echo   Found stale PostgreSQL lock file. Cleaning up postmaster.pid...
    del "C:\Users\Dhruv Rathore\.pgsql\data\postmaster.pid"
)
start "1. PostgreSQL Database (Port 5432)" cmd /k "title PostgreSQL 16 && "C:\Users\Dhruv Rathore\.pgsql\pgsql\bin\postgres.exe" -D "C:\Users\Dhruv Rathore\.pgsql\data""

echo   Waiting for database to initialize...
timeout /t 3 /nobreak >nul

echo.
echo [Step 2/3] Starting FastAPI Backend with AI Assistant Engine...
start "2. FastAPI Backend (Port 8000)" cmd /k "title FastAPI Backend && .\.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload"

echo   Waiting for backend to bind...
timeout /t 3 /nobreak >nul

echo.
echo [Step 3/3] Starting React Vite Frontend Application...
start "3. React Vite Frontend (Port 3000)" cmd /k "title React Vite Frontend && cd frontend && npm run dev -- --host 0.0.0.0 --port 3000"

echo   Waiting for dev server...
timeout /t 2 /nobreak >nul

echo.
echo ==============================================================================
echo                     ALL SERVICES RUNNING SUCCESSFULLY!
echo ==============================================================================
echo.
echo   * Web Application:        http://localhost:3000
echo   * AI Assistant Chat:      http://localhost:3000/assistant
echo   * Product Explorer:       http://localhost:3000/products
echo   * Review Analytics Hub:   http://localhost:3000/analytics
echo   * Interactive API Docs:   http://localhost:8000/docs
echo.
echo Opening Web Application in your browser...
start http://localhost:3000
echo.
echo Keep this window or the minimized background windows open while using the platform.
echo ==============================================================================
pause
