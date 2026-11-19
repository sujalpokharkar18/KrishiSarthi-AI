@echo off
title Krishi Sarthi AI - Backend Server
echo ====================================================
echo Starting Krishi Sarthi AI Backend Server
echo Location: %~dp0Python_backend
echo ====================================================

cd /d "%~dp0Python_backend"

echo.
echo Starting FastAPI server on port 8000...
start "KrishiSarthi FastAPI" python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

timeout /t 3 /nobreak >nul

echo.
echo Starting Cloudflare Tunnel for mobile access...
start "Cloudflare Tunnel" cloudflared.exe tunnel --protocol http2 --url http://localhost:8000

echo.
echo Backend is starting up!
echo - FastAPI documentation: http://localhost:8000/docs
echo - Check Cloudflare console window for public HTTPS URL
echo.
pause
