"""
Automatic Model Retraining Service
===================================
This service monitors Firestore for new completed appointments and
automatically retrains the model when a threshold is reached.

Features:
- Monitors Firestore for new completed appointments
- Retrains model when threshold is met (e.g., 10 new appointments)
- Can also retrain on a schedule (daily/weekly)
- Automatically reloads the model in the API service
- Production-ready with error handling and logging
"""

import sys
import os
import time
import signal
from datetime import datetime, timedelta
from threading import Thread, Event
import subprocess

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

import firebase_admin
from firebase_admin import credentials, firestore
import joblib
import pickle

# ============================================================================
# CONFIGURATION
# ============================================================================

FIREBASE_CREDENTIALS_PATH = 'firebase_credentials.json'
MODEL_PATH = 'inventory_forecast_model.joblib'
PARTS_LIST_PATH = 'predicted_parts_list.pkl'

# Retraining thresholds
NEW_APPOINTMENTS_THRESHOLD = 10  # Retrain after 10 new completed appointments
SCHEDULED_RETRAIN_HOURS = 24     # Retrain every 24 hours (daily)
CHECK_INTERVAL_SECONDS = 300     # Check for new appointments every 5 minutes

# Training script path
TRAIN_SCRIPT_PATH = 'train_model.py'

# API reload signal file (used to notify API to reload model)
RELOAD_SIGNAL_FILE = 'model_reload_signal.txt'

# ============================================================================
# GLOBAL STATE
# ============================================================================

stop_event = Event()
last_retrain_time = None
last_appointment_count = 0
db = None

# ============================================================================
# FIREBASE INITIALIZATION
# ============================================================================

def initialize_firebase():
    """Initialize Firebase connection."""
    global db
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✓ Firebase initialized for auto-retrain service")
        return True
    except Exception as e:
        print(f"✗ Error initializing Firebase: {e}")
        return False

# ============================================================================
# MODEL RETRAINING
# ============================================================================

def retrain_model():
    """
    Retrain the model by running the training script.
    
    Returns:
        bool: True if retraining succeeded, False otherwise
    """
    try:
        print("\n" + "="*70)
        print("AUTO-RETRAINING MODEL")
        print("="*70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run training script
        result = subprocess.run(
            [sys.executable, TRAIN_SCRIPT_PATH],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print("✓ Model retraining completed successfully")
            print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Signal API to reload model
            signal_api_reload()
            
            return True
        else:
            print(f"✗ Model retraining failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Model retraining timed out (exceeded 5 minutes)")
        return False
    except Exception as e:
        print(f"✗ Error during model retraining: {e}")
        return False

def signal_api_reload():
    """
    Signal the API service to reload the model.
    Creates a signal file that the API service monitors.
    """
    try:
        with open(RELOAD_SIGNAL_FILE, 'w') as f:
            f.write(f"reload_{datetime.now().isoformat()}")
        print("✓ API reload signal sent")
    except Exception as e:
        print(f"⚠ Could not create reload signal: {e}")

# ============================================================================
# MONITORING FUNCTIONS
# ============================================================================

def count_completed_appointments_with_parts():
    """
    Count the number of completed appointments with spare parts.
    
    Returns:
        int: Number of completed appointments with spare parts
    """
    try:
        appointments_ref = db.collection('appointments')
        appointments_docs = appointments_ref.stream()
        
        count = 0
        for doc in appointments_docs:
            appointment = doc.to_dict()
            status = appointment.get('status', '').lower()
            spare_parts = appointment.get('spareParts', [])
            
            if 'complete' in status and spare_parts:
                if isinstance(spare_parts, list) and len(spare_parts) > 0:
                    count += 1
        
        return count
    except Exception as e:
        print(f"⚠ Error counting appointments: {e}")
        return 0

def should_retrain_by_threshold():
    """
    Check if we should retrain based on new appointment threshold.
    
    Returns:
        bool: True if threshold is met
    """
    global last_appointment_count
    
    try:
        current_count = count_completed_appointments_with_parts()
        
        if last_appointment_count == 0:
            # First run - initialize
            last_appointment_count = current_count
            return False
        
        new_appointments = current_count - last_appointment_count
        
        if new_appointments >= NEW_APPOINTMENTS_THRESHOLD:
            print(f"\n📊 Threshold met: {new_appointments} new appointments (threshold: {NEW_APPOINTMENTS_THRESHOLD})")
            last_appointment_count = current_count
            return True
        
        return False
    except Exception as e:
        print(f"⚠ Error checking threshold: {e}")
        return False

def should_retrain_by_schedule():
    """
    Check if we should retrain based on scheduled time.
    
    Returns:
        bool: True if scheduled time has passed
    """
    global last_retrain_time
    
    if last_retrain_time is None:
        # First run - don't retrain immediately
        last_retrain_time = datetime.now()
        return False
    
    time_since_last_retrain = datetime.now() - last_retrain_time
    
    if time_since_last_retrain >= timedelta(hours=SCHEDULED_RETRAIN_HOURS):
        print(f"\n⏰ Scheduled retrain: {time_since_last_retrain} since last retrain")
        return True
    
    return False

# ============================================================================
# MAIN MONITORING LOOP
# ============================================================================

def monitoring_loop():
    """Main loop that monitors for retraining conditions."""
    global last_retrain_time
    
    print("="*70)
    print("AUTOMATIC MODEL RETRAINING SERVICE")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration:")
    print(f"  - New appointments threshold: {NEW_APPOINTMENTS_THRESHOLD}")
    print(f"  - Scheduled retrain interval: {SCHEDULED_RETRAIN_HOURS} hours")
    print(f"  - Check interval: {CHECK_INTERVAL_SECONDS} seconds")
    print("="*70)
    print("\n🔄 Monitoring for retraining conditions...")
    print("   (Press Ctrl+C to stop)\n")
    
    # Initialize appointment count
    last_appointment_count = count_completed_appointments_with_parts()
    print(f"📊 Initial appointment count: {last_appointment_count}")
    
    while not stop_event.is_set():
        try:
            # Check if we should retrain
            retrain_needed = False
            reason = ""
            
            if should_retrain_by_threshold():
                retrain_needed = True
                reason = "new appointments threshold"
            elif should_retrain_by_schedule():
                retrain_needed = True
                reason = "scheduled interval"
            
            if retrain_needed:
                print(f"\n🔄 Retraining triggered: {reason}")
                success = retrain_model()
                
                if success:
                    last_retrain_time = datetime.now()
                    print(f"✓ Next scheduled retrain: {last_retrain_time + timedelta(hours=SCHEDULED_RETRAIN_HOURS)}")
                else:
                    print("⚠ Retraining failed, will retry on next check")
            
            # Wait for next check
            stop_event.wait(CHECK_INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            print("\n\n⚠ Interrupted by user")
            break
        except Exception as e:
            print(f"\n⚠ Error in monitoring loop: {e}")
            print("   Continuing monitoring...")
            stop_event.wait(CHECK_INTERVAL_SECONDS)
    
    print("\n" + "="*70)
    print("Auto-retrain service stopped")
    print("="*70)

# ============================================================================
# SIGNAL HANDLERS
# ============================================================================

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n\n⚠ Shutdown signal received, stopping service...")
    stop_event.set()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize Firebase
    if not initialize_firebase():
        print("✗ Failed to initialize Firebase. Exiting.")
        return
    
    # Check if model exists (first run)
    if not os.path.exists(MODEL_PATH):
        print("⚠ No existing model found. Training initial model...")
        if retrain_model():
            print("✓ Initial model trained successfully")
        else:
            print("✗ Failed to train initial model. Exiting.")
            return
    
    # Start monitoring
    try:
        monitoring_loop()
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

