# Inventory Forecasting System

A complete end-to-end predictive inventory system for forecasting spare parts demand and informing restocking decisions.

## 📋 System Overview

This system consists of three main components:

1. **Python Training Script** (`train_model.py`) - Trains a machine learning model on your completed appointments
2. **Python API Service** (`python_api_service.py`) - Serves predictions via REST API
3. **Dart Client** (`dart_prediction_client.dart`) - Client-side integration for Flutter/Dart applications

### How It Works

1. **Data Collection**: Completed appointments with `spareParts` usage are fetched from your Firestore database
2. **Aggregation**: Spare parts usage is aggregated by day to show daily demand patterns
3. **Feature Engineering**: Time-based features (day of week, lagged usage) are created
4. **Model Training**: A Multi-Output Random Forest Regressor learns to predict daily demand for all parts
5. **API Service**: The trained model is served via a Flask REST API
6. **Forecasting**: Client applications request forecasts for any number of days
7. **Restock Planning**: The API returns total quantities needed for each part

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Firebase project with historical service data
- Dart/Flutter environment (for client integration)

### 1. Installation

```bash
# Clone or navigate to the project directory
cd inventory-forecast

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Firebase Configuration

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key" to download your service account JSON file
3. Save it as `firebase_credentials.json` in the project root
4. Verify your Firestore collections:
   - `appointments` collection exists with completed service records
   - `spare_parts` collection exists with your parts inventory
   - Completed appointments have a `spareParts` array with usage data

### 3. Data Structure Requirements

#### Firestore Collections Structure

The system uses your existing **Firestore** collections:

**`appointments` collection** - Completed service appointments:

```json
{
  "plateNumber": "HDIA-4627",
  "reference": "MO-2025117-1763332528651",
  "service": "Performance & Customization",
  "status": "completed", // Must contain "complete" to be included
  "date": "2025-11-20", // Or appointmentDate, completedDate, timestamp
  "spareParts": [
    {
      "id": "17RCHlM2wWBXYkcAExc",
      "name": "Piston Kit",
      "price": 1500,
      "quantity": 1,
      "sku": "ENG-001"
    },
    {
      "id": "vGMmgHkfKqPnxmKAlex",
      "name": "Brake Pads (Front)",
      "price": 450,
      "quantity": 1,
      "sku": "BRK-001"
    }
  ]
}
```

**`spare_parts` collection** - Your inventory parts catalog:

```json
{
  "name": "Piston Kit",
  "price": 1500,
  "quantity": 10,
  "sku": "ENG-001"
}
```

The training script will:

- Fetch all completed appointments from `appointments` collection
- Extract spare parts usage from the `spareParts` array
- Aggregate daily usage for each part
- Train the model on this historical usage data

### 4. Train the Model

```bash
python train_model.py
```

This will:

- Fetch data from Firebase
- Aggregate and engineer features
- Train the Random Forest model
- Save the model to `inventory_forecast_model.joblib`
- Save the parts list to `predicted_parts_list.pkl`

### 5. Start the API Service

```bash
python python_api_service.py
```

The API will start on `http://localhost:5000`

#### Available Endpoints

- `POST /forecast_restock_demand` - Get inventory forecast
- `GET /health` - Health check
- `GET /parts` - List active parts

### 6. Test the API

```bash
curl -X POST http://localhost:5000/forecast_restock_demand \
  -H "Content-Type: application/json" \
  -d '{"forecast_days": 7, "current_date": "2025-11-26"}'
```

Expected response:

```json
{
  "status": "success",
  "forecast_period_days": 7,
  "start_date": "2025-11-26",
  "end_date": "2025-12-02",
  "total_restock_demand": {
    "Carburetor": 105,
    "Engine Gaskets": 30,
    "Oil Filter": 85
  },
  "daily_breakdown": [...]
}
```

### 7. Integrate Dart Client

Add the `dart_prediction_client.dart` file to your Flutter/Dart project:

```dart
import 'dart_prediction_client.dart';

// Fetch 7-day forecast
final forecast = await fetchRestockForecast(forecastDays: 7);

if (forecast != null) {
  print('Forecast period: ${forecast.forecastPeriodDays} days');

  forecast.totalRestockDemand.forEach((part, quantity) {
    print('$part: $quantity units needed');
  });
}
```

#### Update API URL

In `dart_prediction_client.dart`, update the base URL:

```dart
const String API_BASE_URL = 'http://your-server-ip:5000';
```

## 📊 Model Features

### Input Features

The model uses these features to predict demand:

1. **day_of_week** - Integer 0-6 (Monday=0, Sunday=6)
2. **is_weekend** - Binary (1 if Saturday/Sunday, 0 otherwise)
3. **lag_1_day_total_usage** - Total usage from previous day
4. **lag_7_day_avg_usage** - Average daily usage over last 7 days

### Output Targets

The model predicts daily demand quantities for each active part simultaneously (multi-output regression).

### Model Type

- **Algorithm**: Multi-Output Random Forest Regressor
- **Estimators**: 100 trees
- **Max Depth**: 15
- **Min Samples Split**: 5

## 🔧 Configuration

### Python Training Script

Edit `train_model.py` to customize:

```python
# Firebase paths
HISTORICAL_DATA_PATH = '/historical_service_data'
ACTIVE_PARTS_PATH = '/inventory/active_parts_names'

# Model hyperparameters
N_ESTIMATORS = 100
MAX_DEPTH = 15
MIN_SAMPLES_SPLIT = 5
```

### API Service

Edit `python_api_service.py` to customize:

```python
# Server configuration
app.run(
    host='0.0.0.0',  # Listen on all interfaces
    port=5000,        # Port number
    debug=False       # Set to True for development
)
```

### Dart Client

Edit `dart_prediction_client.dart` to customize:

```dart
// API configuration
const String API_BASE_URL = 'http://localhost:5000';
const Duration REQUEST_TIMEOUT = Duration(seconds: 30);

// Retry configuration
const int MAX_RETRY_ATTEMPTS = 4;
const int INITIAL_BACKOFF_MS = 500;
```

## 🎯 API Usage Examples

### Request Forecast

```bash
POST /forecast_restock_demand
Content-Type: application/json

{
  "forecast_days": 7,
  "current_date": "2025-11-26"
}
```

### Response

```json
{
  "status": "success",
  "forecast_period_days": 7,
  "start_date": "2025-11-26",
  "end_date": "2025-12-02",
  "total_restock_demand": {
    "Carburetor": 105,
    "Engine Gaskets": 30,
    "Oil Filter": 85,
    "Spark Plug": 140,
    "Air Filter": 65
  },
  "daily_breakdown": [
    {
      "date": "2025-11-26",
      "total_usage": 45.5,
      "parts": {
        "Carburetor": 15,
        "Engine Gaskets": 4,
        "Oil Filter": 12,
        "Spark Plug": 20,
        "Air Filter": 9
      }
    }
    // ... more daily predictions
  ],
  "timestamp": "2025-11-26T10:30:00.000Z"
}
```

## 🔒 Production Deployment

### Using Gunicorn (Linux/macOS)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 python_api_service:app
```

### Using Waitress (Windows/Cross-platform)

Create `server.py`:

```python
from waitress import serve
from python_api_service import app

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
```

Run:

```bash
python server.py
```

### Environment Variables

Set these for production:

```bash
export FLASK_ENV=production
export FIREBASE_CREDENTIALS=/path/to/credentials.json
```

### Security Considerations

1. **API Authentication**: Add token-based authentication
2. **HTTPS**: Use SSL/TLS in production
3. **Rate Limiting**: Implement request rate limiting
4. **Input Validation**: Validate all input parameters
5. **Firebase Security**: Use least-privilege service account

## 📈 Performance Tuning

### Model Retraining

Retrain the model periodically with new data:

```bash
# Recommended: Weekly or monthly
python train_model.py
```

### Caching

The API service includes an in-memory cache for recent historical data. For production, consider:

- Redis for distributed caching
- Database connection pooling
- Response caching for common requests

### Scaling

- **Horizontal Scaling**: Run multiple API service instances behind a load balancer
- **Async Processing**: Use Celery for background model training
- **Database Optimization**: Index Firebase queries for faster data retrieval

## 🐛 Troubleshooting

### Model Not Found Error

```
Error: Model files not found. Please run train_model.py first.
```

**Solution**: Run the training script to generate model files.

### Firebase Connection Error

```
Error initializing Firebase: Could not load credentials
```

**Solution**: Ensure `firebase_credentials.json` exists and contains valid credentials.

### Dart Client Network Error

```
Network error: SocketException
```

**Solutions**:

- Verify API service is running
- Check firewall settings
- Update API_BASE_URL to correct address
- Ensure network connectivity

### Low Model Accuracy

**Solutions**:

- Increase training data volume
- Tune hyperparameters (N_ESTIMATORS, MAX_DEPTH)
- Add more features (seasonality, holidays, etc.)
- Check data quality and consistency

## 📝 License

This project is provided as-is for inventory management purposes.

## 🤝 Support

For issues or questions:

1. Check the troubleshooting section
2. Review the code comments for detailed documentation
3. Verify Firebase data structure matches requirements

## 🔄 Version History

- **v1.0.0** - Initial release with basic forecasting functionality
  - Multi-output Random Forest model
  - Flask REST API
  - Dart client with exponential backoff
  - Firebase integration

---

**Note**: Remember to update the Firebase URL and API base URL in the configuration files before deployment.
