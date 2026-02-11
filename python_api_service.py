"""
Inventory Forecast API Service
===============================
Flask-based REST API that serves inventory forecasting predictions.

This service loads a pre-trained model and provides an endpoint to forecast
total restock demand for all active parts over a specified number of days.

Endpoint: POST /forecast_restock_demand
"""

import sys

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pickle
import numpy as np
from datetime import datetime, timedelta
import traceback
import os
import threading
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Model paths
MODEL_PATH = 'inventory_forecast_model.joblib'
PARTS_LIST_PATH = 'predicted_parts_list.pkl'
RELOAD_SIGNAL_FILE = 'model_reload_signal.txt'  # Signal file from auto-retrain service

# Global variables for model and parts list
model = None
active_parts = []
feature_columns = ['day_of_week', 'is_weekend', 'lag_1_day_total_usage', 'lag_7_day_avg_usage']
model_lock = threading.Lock()  # Lock for thread-safe model reloading
last_reload_check = 0  # Track last time we checked for reload signal

# In-memory cache for recent historical data
# In production, this should be replaced with actual database queries
historical_cache = {
    'recent_daily_totals': [],  # List of recent daily total usage values
    'last_updated': None
}

# ============================================================================
# MODEL LOADING
# ============================================================================

def load_model_artifacts():
    """
    Load the trained model and active parts list from disk.
    
    This function is called once at startup and can be called to reload the model.
    """
    global model, active_parts
    
    with model_lock:  # Thread-safe model loading
        try:
            # Load model
            model = joblib.load(MODEL_PATH)
            print(f"✓ Model loaded from: {MODEL_PATH}")
            
            # Load active parts list
            with open(PARTS_LIST_PATH, 'rb') as f:
                active_parts = pickle.load(f)
            print(f"✓ Active parts loaded: {len(active_parts)} parts")
            print(f"  Parts: {', '.join(active_parts[:5])}{'...' if len(active_parts) > 5 else ''}")
            
            return True
        
        except FileNotFoundError as e:
            print(f"✗ Error: Model files not found. Please run train_model.py first.")
            print(f"  Missing file: {e.filename}")
            return False
        
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            traceback.print_exc()
            return False

# ============================================================================
# FEATURE CALCULATION
# ============================================================================

def calculate_features_for_date(target_date, lag_1_usage, lag_7_avg_usage):
    """
    Calculate input features for a given date.
    
    Args:
        target_date (datetime.date): The date to predict for
        lag_1_usage (float): Total usage from previous day
        lag_7_avg_usage (float): Average usage over last 7 days
        
    Returns:
        np.array: Feature vector [day_of_week, is_weekend, lag_1_day_total_usage, lag_7_day_avg_usage]
    """
    # Convert to datetime if needed
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    elif isinstance(target_date, datetime):
        target_date = target_date.date()
    
    # Calculate time-based features
    day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
    is_weekend = 1 if day_of_week >= 5 else 0
    
    # Assemble feature vector
    features = np.array([
        day_of_week,
        is_weekend,
        lag_1_usage,
        lag_7_avg_usage
    ]).reshape(1, -1)
    
    return features

def initialize_historical_cache():
    """
    Initialize the historical cache with baseline values.
    
    In a production system, this would query the actual database for recent data.
    For this implementation, we use reasonable default values based on typical usage.
    
    NOTE: In production, replace this with actual database queries to get
    the most recent 7 days of historical data.
    """
    global historical_cache
    
    # Default baseline: assume moderate usage if no history available
    # In production, query Firebase or your database for actual recent data
    baseline_daily_usage = 50.0  # Default baseline value
    
    # Initialize with 7 days of baseline data
    historical_cache['recent_daily_totals'] = [baseline_daily_usage] * 7
    historical_cache['last_updated'] = datetime.now()
    
    print(f"⚠ Historical cache initialized with baseline values")
    print(f"  NOTE: For production, implement actual database queries")

# ============================================================================
# FORECASTING LOGIC
# ============================================================================

def forecast_iterative(forecast_days, start_date):
    """
    Perform iterative multi-day forecasting.
    
    This function predicts demand day-by-day, using each prediction to inform
    the next day's features.
    
    Args:
        forecast_days (int): Number of days to forecast
        start_date (str): Starting date in 'YYYY-MM-DD' format
        
    Returns:
        dict: Total restock demand per part over the forecast period
    """
    # Parse start date
    current_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    # Initialize historical data cache if needed
    if not historical_cache['recent_daily_totals']:
        initialize_historical_cache()
    
    # Get recent history for lag calculations
    recent_totals = historical_cache['recent_daily_totals'].copy()
    
    # Accumulator for total predicted quantities per part
    total_predictions = {part: 0.0 for part in active_parts}
    daily_predictions = []
    
    # Iteratively predict for each day
    for day_offset in range(forecast_days):
        prediction_date = current_date + timedelta(days=day_offset)
        
        # Calculate lag features from recent history
        lag_1_usage = recent_totals[-1] if recent_totals else 50.0
        lag_7_avg_usage = np.mean(recent_totals[-7:]) if len(recent_totals) >= 7 else lag_1_usage
        
        # Calculate features for this date
        features = calculate_features_for_date(prediction_date, lag_1_usage, lag_7_avg_usage)
        
        # Make prediction
        prediction = model.predict(features)[0]  # Returns array of quantities for each part
        
        # Ensure non-negative predictions
        prediction = np.maximum(prediction, 0)
        
        # Store daily prediction
        daily_total = prediction.sum()
        daily_predictions.append({
            'date': prediction_date.strftime('%Y-%m-%d'),
            'total_usage': float(daily_total),
            'parts': {part: float(qty) for part, qty in zip(active_parts, prediction)}
        })
        
        # Accumulate totals
        for i, part in enumerate(active_parts):
            total_predictions[part] += float(prediction[i])
        
        # Update recent_totals for next iteration
        recent_totals.append(daily_total)
        if len(recent_totals) > 30:  # Keep last 30 days only
            recent_totals.pop(0)
    
    # Round to whole numbers (can't restock fractional parts)
    total_predictions = {part: int(round(qty)) for part, qty in total_predictions.items()}
    
    return total_predictions, daily_predictions

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/forecast_restock_demand', methods=['POST'])
def forecast_restock_demand():
    """
    Main forecasting endpoint.
    
    Expected JSON Input:
    {
        "forecast_days": 7,
        "current_date": "2025-11-26"
    }
    
    Returns JSON:
    {
        "status": "success",
        "forecast_period_days": 7,
        "total_restock_demand": {
            "Carburetor": 105,
            "Engine Gaskets": 30,
            ...
        },
        "daily_breakdown": [...]  // Optional: daily predictions
    }
    """
    try:
        # Parse request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        # Extract parameters with defaults
        forecast_days = data.get('forecast_days', 7)
        current_date = data.get('current_date', datetime.now().strftime('%Y-%m-%d'))
        
        # Validate inputs
        if not isinstance(forecast_days, int) or forecast_days < 1:
            return jsonify({
                'status': 'error',
                'message': 'forecast_days must be a positive integer'
            }), 400
        
        if forecast_days > 90:
            return jsonify({
                'status': 'error',
                'message': 'forecast_days cannot exceed 90 days'
            }), 400
        
        # Validate date format
        try:
            datetime.strptime(current_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'current_date must be in YYYY-MM-DD format'
            }), 400
        
        # Check if model is loaded
        if model is None:
            return jsonify({
                'status': 'error',
                'message': 'Model not loaded. Please ensure model files exist.'
            }), 500
        
        # Perform forecasting
        total_demand, daily_breakdown = forecast_iterative(forecast_days, current_date)
        
        # Build response
        response = {
            'status': 'success',
            'forecast_period_days': forecast_days,
            'start_date': current_date,
            'end_date': (datetime.strptime(current_date, '%Y-%m-%d') + timedelta(days=forecast_days-1)).strftime('%Y-%m-%d'),
            'total_restock_demand': total_demand,
            'daily_breakdown': daily_breakdown,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"✗ Error in forecast_restock_demand: {e}")
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify service is running.
    """
    model_loaded = model is not None
    parts_loaded = len(active_parts) > 0
    
    return jsonify({
        'status': 'healthy' if (model_loaded and parts_loaded) else 'degraded',
        'model_loaded': model_loaded,
        'parts_loaded': parts_loaded,
        'num_parts': len(active_parts),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/parts', methods=['GET'])
def get_active_parts():
    """
    Endpoint to retrieve the list of active parts.
    """
    return jsonify({
        'status': 'success',
        'parts': active_parts,
        'count': len(active_parts)
    }), 200

# ============================================================================
# AUTO-RELOAD MONITORING
# ============================================================================

def check_and_reload_model():
    """
    Check for reload signal and reload model if needed.
    This runs in a background thread.
    """
    global last_reload_check
    
    # Initialize last_reload_check if model exists
    if os.path.exists(MODEL_PATH):
        last_reload_check = os.path.getmtime(MODEL_PATH)
    
    while True:
        try:
            time.sleep(10)  # Check every 10 seconds
            
            # Check if reload signal file exists
            if os.path.exists(RELOAD_SIGNAL_FILE):
                try:
                    # Read the signal file
                    with open(RELOAD_SIGNAL_FILE, 'r') as f:
                        signal_content = f.read().strip()
                    
                    # Check if model files are newer than last check
                    if os.path.exists(MODEL_PATH):
                        model_mtime = os.path.getmtime(MODEL_PATH)
                        
                        if model_mtime > last_reload_check:
                            print("\n" + "="*70)
                            print("🔄 AUTO-RELOADING MODEL")
                            print("="*70)
                            print(f"Signal detected: {signal_content}")
                            print(f"Model file modified: {datetime.fromtimestamp(model_mtime)}")
                            
                            # Reload model
                            if load_model_artifacts():
                                print("✓ Model reloaded successfully")
                                last_reload_check = model_mtime
                                
                                # Delete signal file
                                try:
                                    os.remove(RELOAD_SIGNAL_FILE)
                                except:
                                    pass
                            else:
                                print("✗ Model reload failed")
                            
                            print("="*70 + "\n")
                
                except Exception as e:
                    print(f"⚠ Error checking reload signal: {e}")
        
        except Exception as e:
            print(f"⚠ Error in reload monitor: {e}")
            time.sleep(30)  # Wait longer on error

def start_reload_monitor():
    """Start the background thread that monitors for model reload signals."""
    monitor_thread = threading.Thread(target=check_and_reload_model, daemon=True)
    monitor_thread.start()
    print("✓ Auto-reload monitor started (checks every 10 seconds)")

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

def initialize_app():
    """
    Initialize the application by loading model artifacts.
    """
    print("="*70)
    print("INVENTORY FORECAST API SERVICE")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    success = load_model_artifacts()
    
    if not success:
        print("\n⚠ WARNING: Model not loaded. API will return errors until model is trained.")
        print("   Please run train_model.py first.")
    else:
        print("\n✓ API service initialized successfully")
        print("="*70)
        print("Available endpoints:")
        print("  POST /forecast_restock_demand - Get inventory forecast")
        print("  GET  /health                  - Health check")
        print("  GET  /parts                   - List active parts")
        print("="*70)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    # Initialize on startup
    initialize_app()
    
    # Start auto-reload monitor
    start_reload_monitor()
    
    # Run Flask app
    print("\n🚀 Starting Flask server...")
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=5057,        # Default port
        debug=False,      # Set to False in production
        threaded=True
    )

