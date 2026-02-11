# 🔐 Environment Configuration Guide

**Project:** Lorenz Motorcycle Service Management System
**Last Updated:** October 17, 2025

---

## 📋 Overview

This application uses environment variables to manage configuration across different environments (development, staging, production) and to securely store API keys and sensitive information.

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Your .env File

The `.env` file already exists in your project. If not, create it:

```bash
cd lorenz_app
cp .env.example .env
```

### Step 2: Get OpenRouter API Key (For AI Chatbot)

1. Visit [https://openrouter.ai/](https://openrouter.ai/)
2. Create a free account
3. Navigate to **Keys** section
4. Click **Create Key**
5. Copy the API key

### Step 3: Update .env File

Open `lorenz_app/.env` and update the following:

```env
# Replace this line:
OPENROUTER_API_KEY=your_openrouter_api_key_here

# With your actual key:
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
```

### Step 4: Verify Setup

```bash
cd lorenz_app
flutter pub get
flutter run -d chrome
```

Navigate to the AI Chatbot page and verify it works!

---

## 📝 Environment Variables Reference

### Required Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Yes* | API key for AI chatbot | `sk-or-v1-xxx...` |
| `ENVIRONMENT` | Yes | Current environment | `development` |

*Required only if `ENABLE_AI_CHATBOT=true`

### Optional Variables

| Variable | Default | Description | Options |
|----------|---------|-------------|---------|
| `API_URL` | `https://api.lorenz.com` | Backend API URL | Any valid URL |
| `ENABLE_AI_CHATBOT` | `true` | Enable/disable AI features | `true`, `false` |
| `ENABLE_ANALYTICS` | `true` | Enable Firebase Analytics | `true`, `false` |
| `ENABLE_CRASHLYTICS` | `true` | Enable crash reporting | `true`, `false` |
| `DEBUG_MODE` | `true` | Enable debug features | `true`, `false` |
| `VERBOSE_LOGGING` | `false` | Detailed console logs | `true`, `false` |
| `APP_NAME` | `Lorenz Motorcycle Service` | Application name | Any string |
| `APP_VERSION` | `1.0.0` | Version identifier | Semver format |

---

## 🌍 Environment-Specific Configuration

### Development (.env.development)

```env
ENVIRONMENT=development
DEBUG_MODE=true
VERBOSE_LOGGING=true
ENABLE_AI_CHATBOT=true
ENABLE_ANALYTICS=false
ENABLE_CRASHLYTICS=false
```

### Staging (.env.staging)

```env
ENVIRONMENT=staging
DEBUG_MODE=false
VERBOSE_LOGGING=false
ENABLE_AI_CHATBOT=true
ENABLE_ANALYTICS=true
ENABLE_CRASHLYTICS=true
API_URL=https://staging-api.lorenz.com
```

### Production (.env.production)

```env
ENVIRONMENT=production
DEBUG_MODE=false
VERBOSE_LOGGING=false
ENABLE_AI_CHATBOT=true
ENABLE_ANALYTICS=true
ENABLE_CRASHLYTICS=true
API_URL=https://api.lorenz.com
```

**Usage:**
```bash
# Switch environments
cp .env.development .env
flutter run

cp .env.production .env
flutter build apk
```

---

## 🔒 Security Best Practices

### DO ✅
- ✅ Keep `.env` in `.gitignore` (already configured)
- ✅ Use different API keys for dev/staging/production
- ✅ Rotate API keys regularly (every 90 days)
- ✅ Use strong, unique keys for each environment
- ✅ Document required variables in `.env.example`
- ✅ Store production keys in secure vault (1Password, AWS Secrets Manager)

### DON'T ❌
- ❌ **NEVER** commit `.env` to version control
- ❌ Don't share API keys via email or chat
- ❌ Don't hardcode secrets in source code
- ❌ Don't use production keys in development
- ❌ Don't log environment variables
- ❌ Don't expose `.env` file publicly

---

## 🛠️ Accessing Environment Variables in Code

### Reading Variables

```dart
import 'package:lorenz_app/config/environment.dart';

// Check environment
if (Environment.isDevelopment) {
  print('Running in development mode');
}

if (Environment.isProduction) {
  // Production-only code
}

// Get API key
final apiKey = Environment.openRouterApiKey;

// Check feature flags
if (Environment.enableAiChatbot) {
  // AI chatbot code
}

// Get custom values
final apiUrl = Environment.apiUrl;
final appName = Environment.appName;
```

### Validation

```dart
// Validate configuration on app start
void main() async {
  await Environment.initialize();

  if (!Environment.validateConfig()) {
    print('ERROR: Invalid configuration');
    return;
  }

  // Print config in debug mode
  Environment.printConfig();

  runApp(MyApp());
}
```

---

## 🧪 Testing Configuration

### Test Missing Variables

```bash
# Temporarily rename .env
mv .env .env.backup

# Run app - should show warnings
flutter run -d chrome

# Restore .env
mv .env.backup .env
```

### Test Invalid Values

Create `.env` with invalid values:
```env
ENABLE_AI_CHATBOT=invalid  # Should default to false
OPENROUTER_API_KEY=  # Should show warning
```

Run app and verify error handling.

---

## 🐛 Troubleshooting

### Issue: "AI Chatbot not working"

**Solution:**
1. Check `.env` file exists: `ls -la lorenz_app/.env`
2. Verify API key is set: `cat lorenz_app/.env | grep OPENROUTER`
3. Ensure no extra spaces around `=`
4. Restart the app after changing `.env`

### Issue: "Environment variables not loading"

**Solution:**
1. Run `flutter clean`
2. Run `flutter pub get`
3. Restart IDE/editor
4. Run `flutter run` again

### Issue: ".env file not found"

**Solution:**
```bash
cd lorenz_app
cp .env.example .env
# Edit .env with actual values
flutter pub get
```

### Issue: "Configuration errors on startup"

**Solution:**
1. Check `Environment.validateConfig()` output
2. Verify all required fields are set
3. Check for typos in variable names
4. Ensure boolean values are lowercase (`true`/`false`)

---

## 📚 Additional Resources

### Getting API Keys

| Service | Purpose | URL |
|---------|---------|-----|
| OpenRouter | AI Chatbot | https://openrouter.ai/ |
| Firebase | Backend | https://console.firebase.google.com/ |

### Environment Management Tools

- **flutter_dotenv**: Used in this project
- **envied**: Compile-time environment variables
- **flutter_config**: Native environment variables

### Documentation

- [flutter_dotenv Package](https://pub.dev/packages/flutter_dotenv)
- [Environment Best Practices](https://12factor.net/config)
- [Firebase Security Rules](https://firebase.google.com/docs/rules)

---

## 📞 Support

### Common Questions

**Q: Can I commit `.env.example`?**
A: Yes! `.env.example` should be committed as a template for team members.

**Q: How do I share environment config with my team?**
A: Share `.env.example` via git, then send actual keys securely (encrypted message, password manager).

**Q: Should I use different keys for each developer?**
A: For development, shared keys are okay. For production, use unique keys per environment.

**Q: How often should I rotate API keys?**
A: Every 90 days, or immediately if compromised.

**Q: What if I accidentally commit `.env`?**
A:
1. Immediately rotate all API keys
2. Remove file from git history: `git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty --tag-name-filter cat -- --all`
3. Force push: `git push origin --force --all`
4. Update `.env` with new keys

---

## ✅ Checklist

Before deployment, verify:

- [ ] `.env` file exists
- [ ] All required variables are set
- [ ] API keys are valid and active
- [ ] `.gitignore` includes `.env`
- [ ] No `.env` files in git history
- [ ] Production uses production keys
- [ ] Keys are documented in team password manager
- [ ] `Environment.validateConfig()` returns true
- [ ] App runs without configuration errors

---

**Status:** ✅ Environment configuration complete
**Next:** Configure Firebase and run the app
**See Also:** [FIREBASE_SETUP_GUIDE.md](FIREBASE_SETUP_GUIDE.md)
