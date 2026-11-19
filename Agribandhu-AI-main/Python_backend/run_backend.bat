@echo off
title KrishiSarthi AI Backend Server
echo ======================================================
echo Starting KrishiSarthi AI FastAPI Backend on Port 8000...
echo Host: 0.0.0.0 (Accessible locally and via Wi-Fi)
echo Interactive API Docs: http://localhost:8000/docs
echo ======================================================
echo.

cd /d "%~dp0"
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
pause
