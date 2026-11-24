@echo off
chcp 65001 >nul
title Delhi Transport Platform — Hackathon Pipeline Runner
color 0B

:MENU
cls
echo =====================================================================
echo   DELHI TRANSPORT STACK HACKATHON — PROBLEM 2: CROWDEDNESS PLANNER
echo   DTC Smart Occupancy System (DSOS): High-Concurrency Transit Platform
echo =====================================================================
echo.
echo   [1] START APPLICATION (Launch Server and Open Web Browser)
echo   [2] RUN SYSTEM AUDIT (Verify Data, Model, Routing and Pins)
echo   [3] RETRAIN ML MODEL (Train Forecaster on 25.6 Lakh ETM Tickets)
echo   [4] REBUILD FRONTEND (Compile React/Vite UI Bundle)
echo   [5] FULL PIPELINE (Retrain Model + Rebuild UI + Run Audit + Start)
echo   [6] EXIT
echo.
echo =====================================================================
set /p choice="Select an option [1-6] (Default is 1): "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto START_APP
if "%choice%"=="2" goto RUN_AUDIT
if "%choice%"=="3" goto TRAIN_MODEL
if "%choice%"=="4" goto BUILD_FRONTEND
if "%choice%"=="5" goto FULL_PIPELINE
if "%choice%"=="6" goto EXIT
echo Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.
pause
goto MENU

:START_APP
cls
echo =====================================================================
echo   [OPTION 1] Launching Application Server...
echo =====================================================================
echo.
echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    goto MENU
)

echo Installing / Checking Python dependencies from requirements.txt...
pip install -r requirements.txt --quiet

echo.
echo Starting application server at http://localhost:8000 ...
echo Opening your web browser automatically in 3 seconds...
start "" http://localhost:8000
python run.py
pause
goto MENU

:RUN_AUDIT
cls
echo =====================================================================
echo   [OPTION 2] Running Automated 5-Stage System Audit...
echo =====================================================================
echo.
python scripts/run_full_audit.py
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:TRAIN_MODEL
cls
echo =====================================================================
echo   [OPTION 3] Retraining Machine Learning Forecaster...
echo =====================================================================
echo.
python scripts/train_model.py
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:BUILD_FRONTEND
cls
echo =====================================================================
echo   [OPTION 4] Rebuilding Frontend Production Bundle...
echo =====================================================================
echo.
cd frontend
call npm run build
cd ..
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:FULL_PIPELINE
cls
echo =====================================================================
echo   [OPTION 5] Executing Complete End-to-End Pipeline...
echo =====================================================================
echo.
echo STEP 1/4: Retraining Machine Learning Model...
python scripts/train_model.py
if errorlevel 1 (
    echo [ERROR] Model training failed!
    pause
    goto MENU
)

echo.
echo STEP 2/4: Rebuilding Frontend Assets...
cd frontend
call npm run build
cd ..
if errorlevel 1 (
    echo [ERROR] Frontend build failed!
    pause
    goto MENU
)

echo.
echo STEP 3/4: Running Full System Audit & Verification...
python scripts/run_full_audit.py
if errorlevel 1 (
    echo [ERROR] Audit verification encountered errors!
    pause
    goto MENU
)

echo.
echo STEP 4/4: Launching Application Server...
start "" http://localhost:8000
python run.py
pause
goto MENU

:EXIT
echo Exiting...
exit /b 0
