@echo off
title FlowCare AI Launcher — Sanjeevani Multispeciality Hospital
echo ======================================================================
echo  FlowCare AI — Hospital Operations Intelligence & Bottleneck Resolution
echo  Challenge: Cypher 2026 - The Blocked Bed
echo ======================================================================
echo.
echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "FlowCare AI Backend (Port 8000)" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\activate && uvicorn main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 2 >nul

echo Starting Vite Frontend on http://localhost:5173 ...
start "FlowCare AI Frontend (Port 5173)" cmd /k "cd /d "%~dp0frontend" && pnpm dev"

timeout /t 2 >nul

echo Opening FlowCare AI Command Center in your browser...
start http://localhost:5173

echo.
echo ======================================================================
echo  FlowCare AI is LIVE!
echo  Frontend URL: http://localhost:5173
echo  Backend URL:  http://127.0.0.1:8000/docs
echo ======================================================================
