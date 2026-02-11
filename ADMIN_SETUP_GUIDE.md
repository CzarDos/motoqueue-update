# Admin Dashboard Setup Guide

## Overview
This guide explains how to set up and use the admin dashboard with role-based access control.

## Features Implemented

### ✅ Backend Logic & Data Integration
1. **Admin Service** (`lib/services/admin_service.dart`)
   - User management (get all users, filter by role, activate/deactivate)
   - Appointment management (CRUD operations, statistics)
   - Feedback management
   - Analytics and reporting
   - Security audit logs
   - System statistics

2. **Admin Providers** (`lib/providers/admin_providers.dart`)
   - Riverpod providers for reactive data fetching
   - Real-time data streams
   - Automatic caching and refresh

3. **Secure Authentication** (`lib/services/secure_auth_service.dart`)
   - Role-based authentication (Admin, User, Mechanic)
   - Session management and validation
   - Failed login tracking and account lockout
   - Security event logging

### ✅ Access Control
1. **Admin Guard** (`lib/widgets/auth_guard.dart`)
   - Protects admin routes from unauthorized access
   - Role verification
   - Permission-based access control
   - Session validity checks

2. **Authentication Flow**
   - Login redirects admins to admin dashboard
   - Normal users redirected to user homepage
   - Automatic role detection on app launch
   - Google OAuth integration with role detection

### ✅ Admin Dashboard UI Integration
1. **Admin Dashboard** (`lib/admin/admin_page.dart`)
   - Real-time appointment statistics
   - Today's, monthly, and yearly metrics
   - Protected with AdminGuard
   - Analytics integration

2. **User Management Page** (`lib/admin/users_management_page.dart`)
   - View all users with search and filter
   - Change user roles
   - Activate/deactivate accounts
   - View detailed user information
   - Real-time updates

3. **Appointments Management** (`lib/admin/admin_dashboard_pages.dart`)
   - View today's appointments
   - Update appointment status
   - Delete appointments
   - Real-time refresh

---

## Creating an Admin Account

### Method 1: Using Firebase Console (Recommended for First Admin)

1. **Sign up a new account in your app**
   - Use the Sign Up page in your app
   - Enter email, password, and name
   - Complete registration as a normal user

2. **Update user role in Firebase Console**
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Select your project: `lorenz-app`
   - Navigate to **Firestore Database**
   - Find the **users** collection
   - Locate the newly created user document
   - Click to edit
   - Change the `role` field from `user` to `admin`
   - Update the `permissions` field to include admin permissions:
   ```json
   {
     "view_dashboard": true,
     "manage_users": true,
     "manage_appointments": true,
     "view_analytics": true,
     "manage_inventory": true,
     "system_settings": true
   }
   ```
   - Save changes

3. **Log out and log back in**
   - The user will now be redirected to the admin dashboard

### Method 2: Using Flutter Code (For Development)

Create a temporary script in your Flutter app:

```dart
// Run this once in your app to create an admin account
import 'package:lorenz_app/services/admin_service.dart';
import 'package:lorenz_app/services/secure_auth_service.dart';

Future<void> createAdminAccount() async {
  final adminService = AdminService();

  try {
    final adminProfile = await adminService.createAdminAccount(
      email: 'admin@lorenz.com',
      password: 'Admin@123456',  // Use a strong password
      displayName: 'System Administrator',
    );

    print('Admin account created successfully!');
    print('Email: ${adminProfile.email}');
    print('Role: ${adminProfile.role}');
  } catch (e) {
    print('Error creating admin: $e');
  }
}
```

**Important**: Remove this code after creating the admin account for security.

### Method 3: Using Firebase Admin SDK (Production)

For production environments, use Firebase Admin SDK from a secure server:

```javascript
const admin = require('firebase-admin');

async function createAdmin(email, password, displayName) {
  // Create user in Firebase Auth
  const userRecord = await admin.auth().createUser({
    email: email,
    password: password,
    displayName: displayName,
  });

  // Create user profile in Firestore
  await admin.firestore().collection('users').doc(userRecord.uid).set({
    uid: userRecord.uid,
    email: email,
    role: 'admin',
    displayName: displayName,
    isActive: true,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    lastLoginAt: admin.firestore.FieldValue.serverTimestamp(),
    permissions: {
      view_dashboard: true,
      manage_users: true,
      manage_appointments: true,
      view_analytics: true,
      manage_inventory: true,
      system_settings: true,
    },
  });

  console.log('Admin created:', userRecord.uid);
}

// Usage
createAdmin('admin@lorenz.com', 'SecurePassword123!', 'Admin User');
```

---

## Admin Login Credentials (Default)

**⚠️ IMPORTANT: Change these credentials immediately after first login!**

```
Email: admin@lorenz.com
Password: Admin@123456
```

To change the password:
1. Log in to the admin dashboard
2. Go to Profile Settings
3. Update password to a secure one

---

## Admin Dashboard Features

### 1. User Management
- **Access**: Admin Dashboard → User Management
- **Features**:
  - View all registered users
  - Search users by email or name
  - Filter by role (Admin, User, Mechanic)
  - Change user roles
  - Activate/Deactivate accounts
  - View detailed user information
  - View user permissions

### 2. Appointment Management
- **Access**: Admin Dashboard → Appointments
- **Features**:
  - View today's appointments
  - Filter by date range
  - Update appointment status
  - Delete appointments
  - View customer information
  - Real-time updates

### 3. Analytics
- **Access**: Admin Dashboard → Analytics
- **Features**:
  - Appointment statistics
  - User registration trends
  - Service type distribution
  - Revenue reports (if payment integrated)

### 4. Security & Audit
- **Automatic Features**:
  - All admin actions are logged
  - Failed login attempts tracked
  - Session management
  - Account lockout after 5 failed attempts

---

## Security Best Practices

### 1. Password Requirements
The system enforces strong passwords:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### 2. Account Lockout
- After 5 failed login attempts, account is locked for 30 minutes
- Admins can clear failed attempts for users

### 3. Session Management
- Admin sessions expire after 8 hours of inactivity
- Users are automatically logged out after session expiration

### 4. Audit Logging
All admin actions are logged including:
- User role changes
- Account activation/deactivation
- Data access events
- Login/logout events

---

## Firebase Security Rules

Ensure your Firestore security rules protect admin data:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Helper function to check if user is admin
    function isAdmin() {
      return request.auth != null &&
             get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin' &&
             get(/databases/$(database)/documents/users/$(request.auth.uid)).data.isActive == true;
    }

    // Users collection - admins can read/write all, users can only read their own
    match /users/{userId} {
      allow read: if request.auth != null && (request.auth.uid == userId || isAdmin());
      allow write: if isAdmin();
      allow create: if request.auth != null && request.auth.uid == userId;
    }

    // Appointments - users can CRUD their own, admins can CRUD all
    match /appointments/{appointmentId} {
      allow read: if request.auth != null &&
                     (resource.data.userId == request.auth.uid || isAdmin());
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null &&
                               (resource.data.userId == request.auth.uid || isAdmin());
    }

    // Feedback - users can create, admins can read all
    match /feedback/{feedbackId} {
      allow create: if request.auth != null;
      allow read, update, delete: if isAdmin();
    }

    // Security logs - admin only
    match /security_logs/{logId} {
      allow read, write: if isAdmin();
    }

    // Security documents - admin only
    match /security/{document} {
      allow read, write: if isAdmin();
    }
  }
}
```

---

## Troubleshooting

### Issue: "Access Denied" when accessing admin dashboard

**Solution**:
1. Verify the user's role in Firestore is set to `admin`
2. Check that `isActive` is set to `true`
3. Ensure the user has logged out and back in after role change
4. Clear app cache and restart

### Issue: Firebase index required error

**Solution**:
1. Click the auto-generated link in the error message
2. Or manually create indexes in Firebase Console → Firestore → Indexes
3. Required indexes:
   - Collection: `appointments`, Fields: `userId` (Ascending), `dateTime` (Ascending)
   - Collection: `appointments`, Fields: `dateTime` (Ascending)

### Issue: Cannot change user roles

**Solution**:
1. Verify you're logged in as an admin
2. Check Firestore security rules allow admin write access
3. Ensure target user exists in Firestore

### Issue: Admin session expires too quickly

**Solution**:
- Session timeout is set to 8 hours in `SecureAuthService`
- To change, modify `_sessionTimeout` in `lib/services/secure_auth_service.dart`

---

## API Reference

### Admin Service Methods

```dart
// User Management
Future<List<UserProfile>> getAllUsers()
Future<List<UserProfile>> getUsersByRole(UserRole role)
Future<void> updateUserRole(String userId, UserRole newRole)
Future<void> activateUser(String userId)
Future<void> deactivateUser(String userId)

// Appointment Management
Future<List<Map<String, dynamic>>> getAllAppointments()
Future<Map<String, int>> getAppointmentStatistics()
Future<void> updateAppointmentStatus(String appointmentId, String status)
Future<void> deleteAppointment(String appointmentId)

// Analytics
Future<Map<String, int>> getUserRegistrationTrend()
Future<Map<String, int>> getAppointmentsByServiceType()
Future<Map<String, dynamic>> getSystemStatistics()

// Security
Future<List<Map<String, dynamic>>> getSecurityEvents({int limit = 50})
Future<void> clearFailedLoginAttempts(String email)
```

---

## Next Steps

1. **Create your first admin account** using one of the methods above
2. **Test the admin dashboard** by logging in
3. **Configure Firebase security rules** to protect your data
4. **Create additional admin users** if needed through the User Management page
5. **Review security logs** periodically to monitor admin activity

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Firebase Console for errors
3. Check Flutter console for detailed error messages
4. Verify Firestore security rules are correctly configured

---

**Last Updated**: 2025-10-06
**Version**: 1.0.0
