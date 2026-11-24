@echo off
chcp 65001 >nul
title Delhi Transport Platform — Quick Start
color 0A

echo =====================================================================
echo   DELHI TRANSPORT STACK HACKATHON — PROBLEM 2: CROWDEDNESS PLANNER
echo   Starting DTC Smart Occupancy System (DSOS)...
echo =====================================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

echo [1/2] Verifying Python requirements...
pip install -r requirements.txt --quiet

echo [2/2] Launching server on http://localhost:8000 ...
echo Opening application in default web browser...
start "" http://localhost:8000
python run.py
pause
