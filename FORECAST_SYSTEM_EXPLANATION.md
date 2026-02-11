# 📊 Inventory Forecast System - How It Works

## 🔄 Current Architecture: Manual Retraining Required

### ⚠️ Important: The forecast does NOT automatically update

**Current Behavior:**
- ❌ The model does **NOT** automatically retrain when new appointments are completed
- ❌ The forecast does **NOT** update in real-time when spare parts are used
- ✅ The model must be **manually retrained** to incorporate new data

**Why?**
- Training a machine learning model is computationally expensive
- It requires processing all historical data
- It takes 10-60 seconds to complete
- Running it automatically on every appointment would be inefficient

---

## 📈 How the Forecast System Works

### Step 1: Data Collection (Automatic)
```
When a service is completed:
┌─────────────────────────────────────┐
│ Appointment marked as "completed"   │
│ with spareParts array:              │
│   - Piston Kit: 2 units             │
│   - Brake Pads: 1 unit              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Data stored in Firestore            │
│ (appointments collection)           │
└─────────────────────────────────────┘
```

**This happens automatically** - every time you complete a service and record spare parts usage, it's saved to Firestore.

---

### Step 2: Model Training (Manual - You Must Run This)

```bash
python train_model.py
```

**What happens:**

1. **Fetch Historical Data**
   ```
   ┌─────────────────────────────────────┐
   │ Query Firestore for ALL completed  │
   │ appointments with spareParts        │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │ Extract spare parts usage:          │
   │ Nov 17: Piston Kit (1), Oil Filter (2)│
   │ Nov 18: Brake Pads (1)              │
   │ Nov 19: Piston Kit (2), Oil Filter (1)│
   │ ...                                 │
   └─────────────────────────────────────┘
   ```

2. **Aggregate Daily Usage**
   ```
   ┌─────────────────────────────────────┐
   │ Group by date and part:             │
   │                                     │
   │ Date       | Piston Kit | Oil Filter│
   │ 2025-11-17 |     1      |     2     │
   │ 2025-11-18 |     0      |     0     │
   │ 2025-11-19 |     2      |     1     │
   │ ...                                 │
   └─────────────────────────────────────┘
   ```

3. **Create Features**
   ```
   For each day, calculate:
   - day_of_week (0=Monday, 6=Sunday)
   - is_weekend (0 or 1)
   - lag_1_day_total_usage (yesterday's total)
   - lag_7_day_avg_usage (last 7 days average)
   ```

4. **Train Machine Learning Model**
   ```
   ┌─────────────────────────────────────┐
   │ Random Forest learns patterns:      │
   │                                     │
   │ "On Mondays, we typically use:     │
   │  - 3 Piston Kits                    │
   │  - 2 Oil Filters                    │
   │  - 1 Brake Pad"                     │
   │                                     │
   │ "When usage was high yesterday,    │
   │  tomorrow will likely be high too"  │
   └─────────────────────────────────────┘
   ```

5. **Save Model**
   ```
   ┌─────────────────────────────────────┐
   │ Save to disk:                       │
   │ - inventory_forecast_model.joblib   │
   │ - predicted_parts_list.pkl          │
   └─────────────────────────────────────┘
   ```

---

### Step 3: API Service (Runs Continuously)

```bash
python python_api_service.py
```

**What happens:**

1. **Load Model on Startup**
   ```
   ┌─────────────────────────────────────┐
   │ Load saved model from disk          │
   │ (trained in Step 2)                 │
   └─────────────────────────────────────┘
   ```

2. **Wait for Forecast Requests**
   ```
   ┌─────────────────────────────────────┐
   │ API listens on http://localhost:5000│
   │                                     │
   │ Endpoint: POST /forecast_restock_demand│
   └─────────────────────────────────────┘
   ```

---

### Step 4: Making Predictions (When Requested)

**When your Flutter app requests a forecast:**

```
Flutter App Request:
{
  "forecast_days": 7,
  "current_date": "2025-11-26"
}
```

**API Processing:**

1. **For each day (1-7):**
   ```
   Day 1 (Nov 26):
   ├─ Calculate features:
   │  ├─ day_of_week = 2 (Wednesday)
   │  ├─ is_weekend = 0
   │  ├─ lag_1_day_total_usage = 45 (from yesterday)
   │  └─ lag_7_day_avg_usage = 42 (last 7 days average)
   │
   ├─ Run model prediction:
   │  └─ Model predicts: Piston Kit (3), Oil Filter (2), ...
   │
   └─ Store prediction
   ```

2. **Use Day 1 prediction for Day 2:**
   ```
   Day 2 (Nov 27):
   ├─ Calculate features:
   │  ├─ day_of_week = 3 (Thursday)
   │  ├─ is_weekend = 0
   │  ├─ lag_1_day_total_usage = 45 (from Day 1 prediction)
   │  └─ lag_7_day_avg_usage = 43 (updated average)
   │
   └─ Predict Day 2...
   ```

3. **Repeat for all 7 days**

4. **Sum up totals:**
   ```
   ┌─────────────────────────────────────┐
   │ Total for 7 days:                   │
   │ - Piston Kit: 21 units              │
   │ - Oil Filter: 14 units              │
   │ - Brake Pads: 7 units               │
   └─────────────────────────────────────┘
   ```

5. **Return to Flutter app:**
   ```json
   {
     "status": "success",
     "forecast_period_days": 7,
     "total_restock_demand": {
       "Piston Kit": 21,
       "Oil Filter": 14,
       "Brake Pads": 7
     }
   }
   ```

---

## 🔄 Update Cycle

### Current System (Manual):

```
┌─────────────────────────────────────────┐
│ 1. New appointments completed           │
│    (Data saved to Firestore)            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 2. YOU manually run:                    │
│    python train_model.py                │
│    (Every week/month)                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 3. Model retrained with new data        │
│    (Takes 10-60 seconds)                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 4. Restart API service:                 │
│    python python_api_service.py         │
│    (Loads new model)                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 5. Forecasts now use updated model      │
└─────────────────────────────────────────┘
```

### Recommended Schedule:

- **Weekly**: Retrain model every Sunday night
- **Monthly**: Retrain model on the 1st of each month
- **After major changes**: Retrain if business patterns change significantly

---

## 🤖 How to Enable Automatic Updates (Optional)

If you want the model to automatically retrain, you have several options:

### Option 1: Scheduled Task (Windows Task Scheduler)

1. Create a batch file `retrain_model.bat`:
   ```batch
   @echo off
   cd D:\Local_Downloads\MotorQueue\lorenz
   call venv\Scripts\activate.bat
   python train_model.py
   ```

2. Schedule it in Windows Task Scheduler:
   - Run weekly on Sundays at 2 AM
   - Automatically retrains the model

### Option 2: Cron Job (Linux/Mac)

```bash
# Run every Sunday at 2 AM
0 2 * * 0 cd /path/to/lorenz && python train_model.py
```

### Option 3: Cloud Function (Firebase/Google Cloud)

Create a Cloud Function that:
- Triggers when appointments are completed
- Waits for a batch (e.g., 10 new appointments)
- Retrains the model automatically
- Updates the API service

### Option 4: Background Service

Create a Python service that:
- Monitors Firestore for new completed appointments
- Retrains model when threshold is reached (e.g., 10 new appointments)
- Automatically reloads the API service

---

## 📊 What the Model Learns

The Random Forest model learns patterns like:

1. **Day of Week Patterns:**
   - "Mondays typically have 30% more usage than Fridays"
   - "Weekends have 50% less usage"

2. **Recent Trends:**
   - "If usage was high yesterday, it's likely high today"
   - "If the 7-day average is increasing, expect continued growth"

3. **Seasonal Patterns:**
   - "November has more brake pad usage (winter prep)"
   - "Summer months have more air filter usage"

4. **Part Correlations:**
   - "When Piston Kits are used, Oil Filters are often used too"
   - "Brake Pads and Brake Fluid are frequently used together"

---

## 🎯 Example Timeline

### Week 1 (Initial Setup):
```
Day 1: Train model with 10 days of historical data
Day 2-7: Use model for forecasts
```

### Week 2:
```
Day 8-14: More appointments completed
Day 15: Retrain model (now has 17 days of data)
Day 16-21: Use updated model for forecasts
```

### Week 3:
```
Day 22-28: Even more appointments
Day 29: Retrain model (now has 24 days of data)
Day 30+: Use updated model for forecasts
```

**As time goes on:**
- More data = Better predictions
- Model learns more patterns
- Forecasts become more accurate

---

## ⚡ Performance Characteristics

| Operation | Time | Frequency |
|-----------|------|-----------|
| **Training** | 10-60 seconds | Weekly/Monthly |
| **Forecast Request** | 100-500ms | On-demand |
| **API Startup** | 2-5 seconds | Once (when started) |

---

## 🔍 Key Points to Remember

1. **Data Collection**: ✅ Automatic (happens when appointments are completed)
2. **Model Training**: ❌ Manual (you must run `train_model.py`)
3. **Forecast Generation**: ✅ Automatic (happens when API is called)
4. **Model Updates**: ❌ Manual (retrain to incorporate new data)

---

## 💡 Best Practices

1. **Retrain Regularly**: 
   - Weekly for active businesses
   - Monthly for slower businesses

2. **Monitor Accuracy**:
   - Compare predictions vs actual usage
   - Retrain more often if predictions are off

3. **Keep API Running**:
   - Start API service once
   - Keep it running in background
   - Only restart when model is retrained

4. **Data Quality**:
   - Ensure all completed appointments have spareParts data
   - Verify quantities are accurate
   - Remove test/dummy appointments

---

## 🚀 Summary

**The forecast system works in 3 stages:**

1. **Data Collection** (Automatic) ✅
   - Every completed appointment with spare parts is saved to Firestore

2. **Model Training** (Manual) ⚠️
   - You run `python train_model.py` to retrain with new data
   - Should be done weekly/monthly

3. **Forecast Generation** (Automatic) ✅
   - API service uses the trained model to make predictions
   - Happens instantly when your Flutter app requests a forecast

**The forecast does NOT automatically update** - you need to retrain the model periodically to incorporate new appointment data. This is by design for performance and efficiency reasons.

