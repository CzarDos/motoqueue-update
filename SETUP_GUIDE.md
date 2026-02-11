# Quick Setup Guide for MotorQueue Inventory Forecasting

This guide will help you set up the inventory forecasting system using your existing Firestore database.

## 📊 Your Current Data Structure

Based on your Firestore database, you already have:

✅ **`appointments` collection** with completed services containing:

- `plateNumber`
- `reference`
- `service`
- `status` (e.g., "completed")
- `date` or similar timestamp field
- `spareParts` array with:
  - `id`
  - `name`
  - `quantity`
  - `price`
  - `sku`

✅ **`spare_parts` collection** with your inventory parts

## 🚀 Setup Steps

### Step 1: Get Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your **lorenz-app** project
3. Click the ⚙️ gear icon → **Project Settings**
4. Go to the **Service Accounts** tab
5. Click **Generate New Private Key**
6. Save the downloaded JSON file as `firebase_credentials.json` in this folder

```
D:\Local_Downloads\MotorQueue\lorenz\
├── firebase_credentials.json  ← Place it here
├── train_model.py
├── python_api_service.py
└── dart_prediction_client.dart
```

### Step 2: Install Python Dependencies

Open PowerShell in this directory and run:

```powershell
# Create a virtual environment (recommended)
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 3: Train the Model

```powershell
python train_model.py
```

**What happens:**

- ✅ Connects to your Firestore database
- ✅ Fetches all completed appointments
- ✅ Extracts spare parts usage from each appointment
- ✅ Aggregates usage by day (e.g., "On Nov 20, 2025: 5 Piston Kits, 3 Brake Pads used")
- ✅ Trains a machine learning model to predict future demand
- ✅ Saves the model to `inventory_forecast_model.joblib`

**Expected output:**

```
======================================================================
INVENTORY FORECAST MODEL TRAINING
Using Firestore Appointments Data
======================================================================
✓ Firebase initialized successfully
✓ Fetched 15 active parts from spare_parts collection
✓ Fetched 145 spare parts usage records from 38 completed appointments
✓ Aggregated to 60 daily records
✓ Model training complete
✓ TRAINING COMPLETED SUCCESSFULLY
```

### Step 4: Start the API Service

```powershell
python python_api_service.py
```

The API will start at `http://localhost:5000`

**Test it with curl:**

```powershell
curl -X POST http://localhost:5000/forecast_restock_demand `
  -H "Content-Type: application/json" `
  -d '{\"forecast_days\": 7, \"current_date\": \"2025-11-26\"}'
```

### Step 5: Integrate with Your Flutter App

1. Copy `dart_prediction_client.dart` to your Flutter project:

   ```
   lorenz_app\lib\services\dart_prediction_client.dart
   ```

2. Make sure `http` package is in your `pubspec.yaml`:

   ```yaml
   dependencies:
     http: ^1.1.0
   ```

3. Update the API URL in the Dart file:

   ```dart
   const String API_BASE_URL = 'http://localhost:5000';
   // For production, use your server IP: 'http://192.168.1.100:5000'
   ```

4. Use it in your admin dashboard:

   ```dart
   import 'package:lorenz_app/services/dart_prediction_client.dart';

   // In your inventory management page
   Future<void> _fetchForecast() async {
     final forecast = await fetchRestockForecast(forecastDays: 7);

     if (forecast != null) {
       setState(() {
         // Update UI with forecast data
         forecast.totalRestockDemand.forEach((part, quantity) {
           print('$part: Need to restock $quantity units');
         });
       });
     }
   }
   ```

## 📱 Example Integration in Admin Dashboard

Add a "Forecast Demand" button to your admin dashboard:

```dart
ElevatedButton.icon(
  icon: Icon(Icons.analytics),
  label: Text('Forecast 7-Day Demand'),
  onPressed: () async {
    // Show loading dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => Center(
        child: CircularProgressIndicator(),
      ),
    );

    // Fetch forecast
    final forecast = await fetchRestockForecast(forecastDays: 7);

    // Hide loading dialog
    Navigator.pop(context);

    if (forecast != null) {
      // Show forecast results in a dialog
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('7-Day Restock Forecast'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: forecast.totalRestockDemand.entries.map((entry) {
                return ListTile(
                  title: Text(entry.key),
                  trailing: Text(
                    '${entry.value} units',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: entry.value > 10 ? Colors.red : Colors.green,
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('Close'),
            ),
          ],
        ),
      );
    } else {
      // Show error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to fetch forecast')),
      );
    }
  },
)
```

## 🔄 Updating the Model

As you get more completed appointments, you should retrain the model periodically:

```powershell
# Every week or month, run:
python train_model.py
```

This will:

- Fetch the latest completed appointments
- Retrain the model with updated data
- Improve prediction accuracy over time

**You don't need to restart the API** - just restart it to load the new model:

```powershell
# Press Ctrl+C to stop the API
# Then restart it:
python python_api_service.py
```

## 🎯 Understanding the Predictions

The model predicts how many of each part you'll need based on:

1. **Day of the week** - More services on weekdays vs weekends
2. **Recent usage** - Higher recent usage suggests higher future demand
3. **Historical patterns** - Learns from past appointment trends

### Example Output:

```json
{
  "total_restock_demand": {
    "Piston Kit": 12, // Need 12 over next 7 days
    "Brake Pads (Front)": 8, // Need 8 over next 7 days
    "Oil Filter": 20 // Need 20 over next 7 days
  }
}
```

## ⚠️ Important Notes

1. **Minimum Data**: The model works best with at least 30 days of completed appointments. If you have less, predictions may be less accurate initially.

2. **Status Field**: The script looks for appointments where `status` contains "complete" (case-insensitive). Make sure your completed appointments are marked correctly.

3. **Date Field**: The script checks multiple field names for dates: `date`, `appointmentDate`, `completedDate`, `timestamp`, `createdAt`. It will use the first one it finds.

4. **Network Access**: Your Flutter app needs to be able to reach the Python API server. For testing on the same machine, use `http://localhost:5000`. For testing on different devices, use your computer's IP address.

5. **Production Deployment**: For production, consider:
   - Deploying the API to a cloud server (Google Cloud Run, AWS, etc.)
   - Adding authentication to the API
   - Using HTTPS instead of HTTP
   - Setting up automatic model retraining

## 🆘 Troubleshooting

### "No completed appointments found"

- Check that your appointments have `status` containing "complete"
- Verify the `spareParts` array exists and is not empty
- Ensure appointments have a date/timestamp field

### "Firebase initialization error"

- Verify `firebase_credentials.json` is in the correct location
- Check that the service account has Firestore read permissions

### "Connection refused" from Dart client

- Make sure the Python API is running
- Check the API_BASE_URL matches your server address
- For Android emulator, use `http://10.0.2.2:5000` instead of `localhost`

### "Module not found" errors

- Make sure you activated the virtual environment: `.\venv\Scripts\activate`
- Reinstall packages: `pip install -r requirements.txt`

## 📞 Next Steps

1. ✅ Set up Firebase credentials
2. ✅ Train the model with your historical data
3. ✅ Test the API locally
4. ✅ Integrate into your Flutter admin dashboard
5. ✅ Monitor predictions and retrain periodically

Your inventory forecasting system is ready to help optimize your spare parts stocking! 🎉
