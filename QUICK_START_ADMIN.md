# Quick Start: Admin Setup

## 🚀 3-Minute Setup

### Step 1: Create Firebase Indexes (Required)
The app will show an error with a link when you try to view appointments. **Click that link** or create manually:

**Firebase Console** → **Firestore** → **Indexes** → **Create Index**

```
Collection: appointments
Fields:
  - userId (Ascending)
  - dateTime (Ascending)
```

### Step 2: Create Admin Account

**Option A: Via Firebase Console (Recommended)**
1. Open your app and sign up a new user:
   - Email: `admin@lorenz.com`
   - Password: `Admin@123456` (or your choice)
   - Name: `Admin`

2. Go to [Firebase Console](https://console.firebase.google.com)
   - Select project: `lorenz-app`
   - **Firestore Database** → **users** collection
   - Find the user you just created
   - Click to edit

3. Update two fields:
   ```
   role: "admin"   (change from "user")

   permissions: {
     "view_dashboard": true,
     "manage_users": true,
     "manage_appointments": true,
     "view_analytics": true,
     "manage_inventory": true,
     "system_settings": true
   }
   ```

4. Save and log out of the app

**Option B: Via Code (Development Only)**
Add this temporary code to your app (remove after use):

```dart
import 'package:lorenz_app/services/admin_service.dart';

Future<void> createAdmin() async {
  final adminService = AdminService();
  await adminService.createAdminAccount(
    email: 'admin@lorenz.com',
    password: 'Admin@123456',
    displayName: 'System Admin',
  );
  print('Admin created!');
}
```

### Step 3: Test Admin Login
1. Log in with admin credentials
2. You should be redirected to the **Admin Dashboard** (not the regular home page)
3. You should see:
   - Today's Appointments count
   - This Month's Appointments
   - This Year's Appointments
   - Appointment Analytics

### Step 4: Explore Admin Features
- Click **"This Year's Appointments"** → Opens **User Management**
- Click **"Today's Appointments"** → View/manage today's bookings
- Click **Refresh icon** → Reload data
- Click **Logout icon** → Sign out

---

## ✅ Verification Checklist

- [ ] Firebase indexes created (click error link or create manually)
- [ ] Admin account created with role="admin"
- [ ] Can log in as admin
- [ ] Redirected to admin dashboard (not user home)
- [ ] Can see appointment statistics
- [ ] Can open User Management page
- [ ] Can search and filter users
- [ ] Can change user roles
- [ ] Regular users CANNOT access admin pages

---

## 🔐 Security Reminder

After creating admin account, **immediately**:
1. Change the default admin password
2. Set up Firebase Security Rules (see [ADMIN_SETUP_GUIDE.md](./ADMIN_SETUP_GUIDE.md))
3. Test that regular users cannot access `/admin/*` routes

---

## 🐛 Troubleshooting

### "Index required" error
**Solution**: Click the link in the error message to create the index

### "Access Denied" when opening admin dashboard
**Solution**:
1. Check Firestore → users → your user
2. Verify `role` field is `"admin"` (not `"user"`)
3. Verify `isActive` is `true`
4. Log out and back in

### Admin dashboard not showing
**Solution**: Check browser console for errors, verify Firebase connection

### Can't change user roles
**Solution**: Update Firebase Security Rules (see full guide)

---

## 📚 Full Documentation

- **Setup Guide**: [ADMIN_SETUP_GUIDE.md](./ADMIN_SETUP_GUIDE.md)
- **Implementation Summary**: [ADMIN_IMPLEMENTATION_SUMMARY.md](./ADMIN_IMPLEMENTATION_SUMMARY.md)

---

## 🎯 What You Get

✅ **Secure Admin Panel**
- Role-based authentication
- Session management (8-hour timeout)
- Account lockout after 5 failed logins

✅ **User Management**
- View all users
- Change roles (Admin/User/Mechanic)
- Activate/deactivate accounts
- Search and filter

✅ **Appointment Management**
- View all appointments
- Update status
- Delete appointments
- Real-time statistics

✅ **Security & Audit**
- All admin actions logged
- Failed login tracking
- Security event monitoring

---

**Need Help?** See [ADMIN_SETUP_GUIDE.md](./ADMIN_SETUP_GUIDE.md) for detailed instructions.
