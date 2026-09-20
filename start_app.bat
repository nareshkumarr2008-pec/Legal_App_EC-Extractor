@echo off
title PlotChoice OCR & Verification Web Server
echo ==================================================
echo Starting PlotChoice OCR & Verification Web Server...
echo Web UI: http://localhost:8000
echo ==================================================
:: Free port 8000 if previously left hanging
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING 2^>nul') do (
    echo Freeing port 8000 from stale process PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

set PYTHONPATH=%~dp0
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0run.py"
) else (
    py "%~dp0run.py"
)
pause

