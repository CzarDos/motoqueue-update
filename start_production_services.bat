@echo off
REM Production Service Startup Script
REM Starts both the API service and auto-retrain service

echo ======================================================================
echo Starting Inventory Forecast Production Services
echo ======================================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if model exists
if not exist inventory_forecast_model.joblib (
    echo WARNING: No model found. Training initial model...
    python train_model.py
    if errorlevel 1 (
        echo ERROR: Failed to train initial model. Exiting.
        pause
        exit /b 1
    )
)

echo.
echo Starting services...
echo.

REM Start API service in a new window
start "Inventory Forecast API" cmd /k "venv\Scripts\activate.bat && python python_api_service.py"

REM Wait a moment for API to start
timeout /t 3 /nobreak >nul

REM Start auto-retrain service in a new window
start "Auto-Retrain Service" cmd /k "venv\Scripts\activate.bat && python auto_retrain_service.py"

echo.
echo ======================================================================
echo Services started!
echo.
echo - API Service: http://localhost:5057
echo - Auto-Retrain Service: Monitoring for new appointments
echo.
echo Both services are running in separate windows.
echo Close those windows to stop the services.
echo ======================================================================
echo.
pause

