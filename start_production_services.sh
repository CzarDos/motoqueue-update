#!/bin/bash
# Production Service Startup Script (Linux/Mac)
# Starts both the API service and auto-retrain service

echo "======================================================================"
echo "Starting Inventory Forecast Production Services"
echo "======================================================================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Check if model exists
if [ ! -f "inventory_forecast_model.joblib" ]; then
    echo "WARNING: No model found. Training initial model..."
    python train_model.py
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to train initial model. Exiting."
        exit 1
    fi
fi

echo ""
echo "Starting services..."
echo ""

# Start API service in background
python python_api_service.py &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Start auto-retrain service in background
python auto_retrain_service.py &
RETRAIN_PID=$!

echo ""
echo "======================================================================"
echo "Services started!"
echo ""
echo "- API Service: http://localhost:5000 (PID: $API_PID)"
echo "- Auto-Retrain Service: Monitoring for new appointments (PID: $RETRAIN_PID)"
echo ""
echo "To stop services, run: kill $API_PID $RETRAIN_PID"
echo "======================================================================"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping services...'; kill $API_PID $RETRAIN_PID; exit" INT TERM
wait

