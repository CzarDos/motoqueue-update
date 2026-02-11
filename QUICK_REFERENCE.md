# 🚀 Quick Reference Guide

## 📁 Directory Structure

```
D:\Local_Downloads\MotorQueue\lorenz\          ← Python ML files here
├── train_model.py                              ← Train the model
├── python_api_service.py                       ← API service
├── test_firebase_connection.py                 ← Test Firebase
├── requirements.txt                            ← Python dependencies
├── firebase_credentials.json                   ← ADD THIS FILE HERE
│
└── lorenz_app\                                 ← Flutter app here
    ├── lib\
    │   └── services\
    │       └── dart_prediction_client.dart     ← Move Dart client here
    ├── pubspec.yaml                            ← Flutter dependencies
    └── ...
```

## ⚡ Common Commands

### Python ML System (Run from `D:\Local_Downloads\MotorQueue\lorenz\`)

```powershell
# Navigate to the ML directory
cd D:\Local_Downloads\MotorQueue\lorenz

# Test Firebase connection (do this first!)
python test_firebase_connection.py

# Train the model (after Firebase test succeeds)
python train_model.py

# Start the API service (after training)
python python_api_service.py
```

### Flutter App (Run from `D:\Local_Downloads\MotorQueue\lorenz\lorenz_app\`)

```powershell
# Navigate to Flutter app directory
cd D:\Local_Downloads\MotorQueue\lorenz\lorenz_app

# Get Flutter dependencies
flutter pub get

# Run the app
flutter run
```

## 🔄 Typical Workflow

### Initial Setup (One-time):
1. **Get Firebase credentials**
   - Download from Firebase Console
   - Save as `firebase_credentials.json` in `D:\Local_Downloads\MotorQueue\lorenz\`

2. **Install Python packages**
   ```powershell
   cd D:\Local_Downloads\MotorQueue\lorenz
   pip install -r requirements.txt
   ```

3. **Test connection**
   ```powershell
   python test_firebase_connection.py
   ```

4. **Train model**
   ```powershell
   python train_model.py
   ```

### Daily Use:
1. **Start API service**
   ```powershell
   cd D:\Local_Downloads\MotorQueue\lorenz
   python python_api_service.py
   ```
   (Keep this running in the background)

2. **Use Flutter app**
   - Your app calls the API automatically
   - Admin can click "Forecast Demand" button

### Weekly Maintenance:
1. **Retrain model with new data**
   ```powershell
   cd D:\Local_Downloads\MotorQueue\lorenz
   python train_model.py
   ```

2. **Restart API** (Ctrl+C to stop, then start again)
   ```powershell
   python python_api_service.py
   ```

## ⚠️ Common Mistakes

### ❌ Wrong: Installing Python packages in Flutter directory
```powershell
cd lorenz_app
pip install -r requirements.txt  # ❌ WRONG - requirements.txt not here
```

### ✅ Right: Installing Python packages in ML directory
```powershell
cd D:\Local_Downloads\MotorQueue\lorenz
pip install -r requirements.txt  # ✅ CORRECT
```

### ❌ Wrong: Running Python scripts from Flutter directory
```powershell
cd lorenz_app
python train_model.py  # ❌ WRONG - file not here
```

### ✅ Right: Running Python scripts from ML directory
```powershell
cd D:\Local_Downloads\MotorQueue\lorenz
python train_model.py  # ✅ CORRECT
```

## 📝 File Checklist

Before training the model, ensure you have:

- [ ] ✅ `requirements.txt` installed (you just did this!)
- [ ] ⚠️ `firebase_credentials.json` downloaded and placed in correct location
- [ ] ⚠️ Firestore has completed appointments with spare parts data

## 🎯 Next Steps (In Order)

1. **Download Firebase credentials** (if not done yet)
   - Go to Firebase Console → Project Settings → Service Accounts
   - Click "Generate New Private Key"
   - Save as `firebase_credentials.json` in `D:\Local_Downloads\MotorQueue\lorenz\`

2. **Test Firebase connection**
   ```powershell
   cd D:\Local_Downloads\MotorQueue\lorenz
   python test_firebase_connection.py
   ```

3. **Train the model** (if test passes)
   ```powershell
   python train_model.py
   ```

4. **Start API service** (if training succeeds)
   ```powershell
   python python_api_service.py
   ```

5. **Integrate Dart client into Flutter app**
   - Copy `dart_prediction_client.dart` to `lorenz_app/lib/services/`
   - Add to admin dashboard

## 🆘 Troubleshooting

### "No such file or directory: requirements.txt"
**Problem**: You're in the wrong directory
**Solution**: 
```powershell
cd D:\Local_Downloads\MotorQueue\lorenz
```

### "Module not found" errors
**Problem**: Python packages not installed
**Solution**: 
```powershell
cd D:\Local_Downloads\MotorQueue\lorenz
pip install -r requirements.txt
```

### "firebase_credentials.json not found"
**Problem**: Firebase credentials not downloaded
**Solution**: Download from Firebase Console and place in `lorenz\` directory

### API not responding from Flutter app
**Problem**: API service not running
**Solution**: 
```powershell
cd D:\Local_Downloads\MotorQueue\lorenz
python python_api_service.py
```

## 📊 Status Check

✅ **Completed:**
- Python dependencies installed
- All ML files created
- Documentation ready

⚠️ **Remaining:**
- Download `firebase_credentials.json`
- Test Firebase connection
- Train the model
- Start API service
- Integrate Dart client into Flutter app

---

**Keep this file handy for quick reference!** 🌟

