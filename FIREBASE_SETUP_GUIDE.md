# 🔥 Firebase Setup Guide - Lorenz Motorcycle Service App

Complete guide to reset and integrate Firebase from scratch.

---

## ✅ **COMPLETED STEPS**

### Step 1: Removed Old Firebase Configuration ✓
- Backed up old config files to `lorenz_app/backup/`
- Deleted `google-services.json` and `firebase_options.dart`

### Step 2: Enhanced Authentication Service ✓
- Updated `lib/services/auth_service.dart` with:
  - User profile creation in Firestore
  - Sign up with email, password, phone number, and full name
  - Sign in with email and password
  - User-friendly error messages
  - Profile management methods
  - Password reset functionality

### Step 3: Updated UI Components ✓
- **SignUpPage**: Now saves user data to Firestore with validation
- **LoginPage**: Enhanced error handling and loading states

---

## 🚀 **YOUR ACTION ITEMS**

### STEP 1: Create Fresh Firebase Project

1. **Go to Firebase Console**
   - Visit: https://console.firebase.google.com/
   - Sign in with your Google account
   - Click **"Add project"** or **"Create a project"**

2. **Configure Project**
   - **Project name:** `lorenz-motorcycle-service` (or your choice)
   - **Google Analytics:** Toggle OFF (optional)
   - Click **"Create project"**
   - Wait 30-60 seconds
   - Click **"Continue"**

---

### STEP 2: Enable Authentication

1. In Firebase Console, click **"Authentication"** (left sidebar)
2. Click **"Get started"**
3. Go to **"Sign-in method"** tab
4. Click **"Email/Password"**
5. **Toggle ON** the first option (Email/Password)
6. Click **"Save"**

✅ **Email/Password authentication is now enabled!**

---

### STEP 3: Enable Firestore Database

1. Click **"Firestore Database"** (left sidebar)
2. Click **"Create database"**
3. **Select:**
   - Mode: **"Start in test mode"** (for development)
   - Click **"Next"**
4. **Location:** Select your nearest region (e.g., `us-central`)
5. Click **"Enable"**
6. Wait for initialization

#### Configure Security Rules

After creation, go to **"Rules"** tab and paste:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow authenticated users to manage their own profile
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // Allow authenticated users to create and read appointments
    match /appointments/{appointmentId} {
      allow create: if request.auth != null;
      allow read, update, delete: if request.auth != null;
    }

    // Allow all authenticated users (temporary - for development)
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

Click **"Publish"**

---

### STEP 4: Register Android App

1. Click ⚙️ **gear icon** → **"Project settings"**
2. Scroll to **"Your apps"** section
3. Click **Android icon** 📱
4. **Fill in:**
   - **Android package name:** `com.example.lorenz_app`
   - **App nickname:** `Lorenz App` (optional)
   - **Debug SHA-1:** Leave blank for now
5. Click **"Register app"**
6. **Download `google-services.json`**
7. **Save it to:** `C:\Users\senku\OneDrive\Desktop\lorenz\lorenz_app\android\app\google-services.json`

---

### STEP 5: Register Web App (for Chrome testing)

1. Still in **"Project settings"**, click **Web icon** 🌐
2. **Fill in:**
   - **App nickname:** `Lorenz Web`
   - **Firebase Hosting:** Leave unchecked
3. Click **"Register app"**
4. **Copy the Firebase config** (you'll need this if manual setup is required)

---

### STEP 6: Configure Flutter Project with FlutterFire CLI

**Open Command Prompt/Terminal and run:**

```bash
cd C:\Users\senku\OneDrive\Desktop\lorenz\lorenz_app
flutterfire configure
```

**When prompted:**
1. **Select Firebase project:** Use arrow keys to choose your newly created project
2. **Select platforms:** Use arrow keys + spacebar to select:
   - ☑ Android
   - ☑ Web
3. Press **Enter** to confirm

**This will automatically:**
- Generate `lib/firebase_options.dart`
- Update Android configuration
- Update Web configuration

---

### STEP 7: Install Dependencies

```bash
cd C:\Users\senku\OneDrive\Desktop\lorenz\lorenz_app
flutter pub get
```

---

### STEP 8: Test the App

#### Run on Chrome (Web)

```bash
flutter run -d chrome
```

#### Run on Windows Desktop

```bash
flutter run -d windows
```

---

## 🧪 **TESTING GUIDE**

### Test 1: Sign Up (Create New Account)

1. **Launch the app**
2. Click **"Sign Up"** button
3. **Fill in:**
   - Email: `test@example.com`
   - Mobile: `+639123456789`
   - Password: `password123`
   - Birthdate: Select any date
4. Click **"Sign Up"** button

**Expected Results:**
- ✅ Loading indicator appears
- ✅ Success message: "Account created successfully!"
- ✅ Redirected back to login page
- ✅ User appears in Firebase Console → Authentication → Users
- ✅ User profile created in Firebase Console → Firestore → users collection

---

### Test 2: Sign In (Login)

1. On the **Login page**, enter:
   - Email: `test@example.com`
   - Password: `password123`
2. Click **"Sign In"** button

**Expected Results:**
- ✅ Loading indicator appears
- ✅ Successfully logged in
- ✅ Navigated to Home page
- ✅ User session is maintained

---

### Test 3: Error Handling

**Test wrong password:**
1. Enter correct email: `test@example.com`
2. Enter wrong password: `wrongpassword`
3. Click **"Sign In"**

**Expected:**
- ❌ Error message: "Incorrect password. Please try again."

**Test non-existent user:**
1. Enter: `nonexistent@example.com`
2. Enter any password
3. Click **"Sign In"**

**Expected:**
- ❌ Error message: "No account found with this email."

---

### Test 4: Verify Data in Firebase Console

1. **Go to Firebase Console → Authentication**
   - You should see your test user
   - Email: `test@example.com`

2. **Go to Firebase Console → Firestore Database**
   - Collection: `users`
   - Document ID: (user's UID)
   - Fields:
     - `email`: test@example.com
     - `fullName`: test (from email prefix)
     - `phoneNumber`: +639123456789
     - `role`: user
     - `createdAt`: timestamp
     - `updatedAt`: timestamp

---

## 📊 **FIRESTORE DATABASE STRUCTURE**

Your app will create these collections:

### `/users/{userId}`
```json
{
  "uid": "ABC123...",
  "email": "user@example.com",
  "fullName": "John Doe",
  "phoneNumber": "+639123456789",
  "role": "user",
  "createdAt": "2025-01-15T10:30:00Z",
  "updatedAt": "2025-01-15T10:30:00Z"
}
```

### `/appointments/{appointmentId}`
```json
{
  "userId": "ABC123...",
  "userEmail": "user@example.com",
  "service": "Oil Change",
  "motorcycleType": "Sport Bike",
  "dateTime": "2025-01-20T14:00:00Z",
  "status": "pending",
  "createdAt": "2025-01-15T10:30:00Z"
}
```

---

## 🔧 **TROUBLESHOOTING**

### Issue: "firebase_options.dart not found"

**Solution:** Run FlutterFire configure:
```bash
cd lorenz_app
flutterfire configure
```

---

### Issue: "No Firebase App '[DEFAULT]' has been created"

**Solution:** Ensure `firebase_options.dart` exists and main.dart has:
```dart
await Firebase.initializeApp(
  options: DefaultFirebaseOptions.currentPlatform,
);
```

---

### Issue: "Email already in use"

**Solution:** This means the account already exists. Try:
1. Use a different email
2. Or sign in with existing credentials
3. Or delete the user from Firebase Console → Authentication

---

### Issue: "Operation not allowed"

**Solution:** Enable Email/Password authentication:
1. Firebase Console → Authentication
2. Sign-in method tab
3. Enable Email/Password

---

## 🎯 **NEXT STEPS**

After completing the setup:

1. **Create an admin account:**
   ```dart
   // Manually create in Firebase Console or add role field
   ```

2. **Implement role-based access:**
   - Admin dashboard access control
   - User permissions

3. **Add appointment booking integration:**
   - Connect UI to Firestore
   - Real-time updates

4. **Security hardening:**
   - Update Firestore rules for production
   - Implement proper role-based security

---

## 📚 **HELPFUL LINKS**

- Firebase Console: https://console.firebase.google.com/
- Firebase Auth Docs: https://firebase.google.com/docs/auth
- Firestore Docs: https://firebase.google.com/docs/firestore
- FlutterFire Docs: https://firebase.flutter.dev/

---

## ✅ **CHECKLIST**

- [ ] Created Firebase project
- [ ] Enabled Email/Password Authentication
- [ ] Enabled Firestore Database
- [ ] Set up Firestore security rules
- [ ] Registered Android app
- [ ] Downloaded google-services.json
- [ ] Registered Web app
- [ ] Ran `flutterfire configure`
- [ ] Ran `flutter pub get`
- [ ] Tested Sign Up
- [ ] Tested Sign In
- [ ] Verified data in Firestore
- [ ] Tested error handling

---

**Created by:** Claude Code
**Date:** 2025-10-02
**Project:** Lorenz Motorcycle Service Management System
