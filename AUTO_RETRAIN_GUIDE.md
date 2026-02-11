# 🤖 Automatic Model Retraining Guide

## Overview

The automatic retraining system eliminates the need for manual model training. It monitors your Firestore database and automatically retrains the model when new data is available.

## 🎯 How It Works

### Two Services Work Together:

1. **API Service** (`python_api_service.py`)

   - Serves forecast requests
   - Automatically reloads model when retrained

2. **Auto-Retrain Service** (`auto_retrain_service.py`)
   - Monitors Firestore for new completed appointments
   - Retrains model when threshold is met
   - Signals API to reload the new model

### Retraining Triggers:

The model automatically retrains when **either** condition is met:

1. **New Appointments Threshold**: After 10 new completed appointments with spare parts
2. **Scheduled Interval**: Every 24 hours (daily)

## 🚀 Quick Start

### Option 1: Use Startup Scripts (Recommended)

**Windows:**

```batch
start_production_services.bat
```

**Linux/Mac:**

```bash
chmod +x start_production_services.sh
./start_production_services.sh
```

This starts both services automatically!

### Option 2: Manual Start

**Terminal 1 - API Service:**

```bash
python python_api_service.py
```

**Terminal 2 - Auto-Retrain Service:**

```bash
python auto_retrain_service.py
```

## ⚙️ Configuration

Edit `auto_retrain_service.py` to customize:

```python
# Retraining thresholds
NEW_APPOINTMENTS_THRESHOLD = 10  # Retrain after 10 new appointments
SCHEDULED_RETRAIN_HOURS = 24     # Retrain every 24 hours
CHECK_INTERVAL_SECONDS = 300     # Check every 5 minutes
```

### Recommended Settings:

| Business Size                      | Threshold       | Schedule       |
| ---------------------------------- | --------------- | -------------- |
| **Small** (1-5 appointments/day)   | 10 appointments | Daily          |
| **Medium** (5-20 appointments/day) | 15 appointments | Daily          |
| **Large** (20+ appointments/day)   | 20 appointments | Every 12 hours |

## 📊 How It Monitors

```
┌─────────────────────────────────────┐
│ Auto-Retrain Service                │
│                                     │
│ Every 5 minutes:                    │
│ 1. Check Firestore for new          │
│    completed appointments           │
│ 2. Count new appointments since     │
│    last retrain                     │
│ 3. Check if threshold met           │
│ 4. Check if scheduled time passed   │
│                                     │
│ If either condition met:            │
│ → Run train_model.py                │
│ → Signal API to reload              │
└─────────────────────────────────────┘
```

## 🔄 Automatic Model Reload

When the model is retrained:

1. **Auto-Retrain Service** creates a signal file
2. **API Service** detects the signal (checks every 10 seconds)
3. **API Service** reloads the new model automatically
4. **No downtime** - forecasts continue working during reload

## 📈 Example Timeline

### Day 1:

```
09:00 - Services start
09:00 - Initial model loaded (10 days of data)
10:30 - 3 new appointments completed
11:45 - 5 more appointments completed
14:20 - 2 more appointments (total: 10 new)
14:20 - ⚡ AUTO-RETRAIN TRIGGERED
14:21 - Model retrained (now 20 days of data)
14:21 - API automatically reloads new model
```

### Day 2:

```
09:00 - Scheduled retrain (24 hours passed)
09:00 - ⚡ AUTO-RETRAIN TRIGGERED
09:01 - Model retrained with all new data
09:01 - API automatically reloads new model
```

## 🛠️ Production Deployment

### Windows Service (Production)

Create a Windows Service using NSSM (Non-Sucking Service Manager):

1. Download NSSM: https://nssm.cc/download
2. Install API service:

   ```batch
   nssm install InventoryForecastAPI "C:\Python39\python.exe" "D:\path\to\python_api_service.py"
   nssm set InventoryForecastAPI AppDirectory "D:\path\to\lorenz"
   nssm start InventoryForecastAPI
   ```

3. Install Auto-Retrain service:
   ```batch
   nssm install AutoRetrainService "C:\Python39\python.exe" "D:\path\to\auto_retrain_service.py"
   nssm set AutoRetrainService AppDirectory "D:\path\to\lorenz"
   nssm start AutoRetrainService
   ```

### Linux Systemd (Production)

Create service files:

**`/etc/systemd/system/inventory-api.service`:**

```ini
[Unit]
Description=Inventory Forecast API Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/lorenz
Environment="PATH=/path/to/lorenz/venv/bin"
ExecStart=/path/to/lorenz/venv/bin/python python_api_service.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/auto-retrain.service`:**

```ini
[Unit]
Description=Auto-Retrain Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/lorenz
Environment="PATH=/path/to/lorenz/venv/bin"
ExecStart=/path/to/lorenz/venv/bin/python auto_retrain_service.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl enable inventory-api
sudo systemctl enable auto-retrain
sudo systemctl start inventory-api
sudo systemctl start auto-retrain
```

## 🔍 Monitoring & Logs

### Check Service Status:

**API Service:**

```bash
curl http://localhost:5000/health
```

**Auto-Retrain Service:**

- Check console output for retraining events
- Look for "AUTO-RETRAINING MODEL" messages

### Log Files (Optional):

Add logging to files:

```python
import logging

logging.basicConfig(
    filename='auto_retrain.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## ⚠️ Troubleshooting

### Model Not Retraining

1. **Check if service is running:**

   ```bash
   # Windows
   tasklist | findstr python

   # Linux
   ps aux | grep python
   ```

2. **Check Firestore connection:**

   - Verify `firebase_credentials.json` exists
   - Check service account permissions

3. **Check threshold settings:**
   - Verify `NEW_APPOINTMENTS_THRESHOLD` is appropriate
   - Check if appointments have `spareParts` data

### API Not Reloading Model

1. **Check signal file:**

   - Look for `model_reload_signal.txt` in the directory
   - If it exists, API should reload within 10 seconds

2. **Check API logs:**

   - Look for "AUTO-RELOADING MODEL" messages
   - Verify model file was updated

3. **Manual reload:**
   - Restart API service if needed

### High CPU Usage

If retraining happens too frequently:

1. **Increase threshold:**

   ```python
   NEW_APPOINTMENTS_THRESHOLD = 20  # Instead of 10
   ```

2. **Increase check interval:**
   ```python
   CHECK_INTERVAL_SECONDS = 600  # Check every 10 minutes
   ```

## 📊 Performance Impact

| Operation        | Impact                       | Frequency          |
| ---------------- | ---------------------------- | ------------------ |
| **Monitoring**   | Minimal (checks every 5 min) | Continuous         |
| **Retraining**   | High (10-60 seconds)         | When threshold met |
| **Model Reload** | Minimal (< 1 second)         | After retraining   |

## ✅ Benefits

1. **Zero Manual Intervention** - Fully automatic
2. **Always Up-to-Date** - Model learns from new data
3. **Production Ready** - Suitable for company deployment
4. **Self-Healing** - Automatically recovers from errors
5. **Scalable** - Works for any business size

## 🎯 Summary

With automatic retraining:

- ✅ Model updates automatically when new data arrives
- ✅ No manual training required
- ✅ API automatically uses the latest model
- ✅ Production-ready for company deployment
- ✅ Configurable thresholds and schedules

**Just start both services and forget about it!** 🚀
