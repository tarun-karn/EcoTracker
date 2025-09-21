# Google OAuth2 Setup Guide for EcoTracker

## ✅ Current Status

**Google OAuth2 has been successfully implemented and integrated!**

### What's Working:
- ✅ Django-allauth is installed and configured
- ✅ Google OAuth2 provider is set up  
- ✅ OAuth2 URLs are properly routed (`/accounts/google/login/`)
- ✅ Login and signup pages have functional Google Sign-In buttons
- ✅ OAuth2 flow redirects to Google correctly
- ✅ Database tables are created for social accounts
- ✅ Management command created for easy OAuth2 app setup

### What You Need to Complete:

#### 1. Get Real Google OAuth2 Credentials

1. **Go to Google Cloud Console**: https://console.developers.google.com/
2. **Create a New Project** (or select existing)
3. **Enable APIs**: 
   - Enable "Google+ API" or "Google Identity"
4. **Create OAuth 2.0 Credentials**:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Name: "EcoTracker OAuth2"
   - **Authorized redirect URIs**: 
     ```
     http://127.0.0.1:8000/accounts/google/login/callback/
     https://yourdomain.com/accounts/google/login/callback/
     ```

#### 2. Update Your Credentials

Run this command with your real credentials:

```bash
python manage.py setup_google_oauth --client-id YOUR_ACTUAL_CLIENT_ID --client-secret YOUR_ACTUAL_CLIENT_SECRET
```

#### 3. Test the Integration

1. **Navigate to login page**: http://127.0.0.1:8000/users/login/
2. **Click "Sign in with Google"**
3. **Complete Google OAuth flow**
4. **User should be redirected back and logged in**

## Current Configuration

### Files Modified:
- `config/settings.py` - OAuth2 settings and apps
- `config/urls.py` - Added allauth URLs  
- `templates/registration/login.html` - Google Sign-In button
- `templates/registration/signup.html` - Google Sign-Up button
- `users/management/commands/setup_google_oauth.py` - Setup command

### Current Settings:
```python
# Allauth configuration
SITE_ID = 1
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# OAuth2 Provider Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    }
}
```

## Testing URLs

- **Home Page**: http://127.0.0.1:8000/
- **Login Page**: http://127.0.0.1:8000/users/login/
- **Signup Page**: http://127.0.0.1:8000/users/signup/
- **Google OAuth Direct**: http://127.0.0.1:8000/accounts/google/login/
- **OAuth Test Endpoint**: http://127.0.0.1:8000/users/test-oauth/

## Error Resolution

### Issues Fixed:
- ❌ **JWT Module Missing** → ✅ Installed `PyJWT[crypto]`
- ❌ **Context Processors Error** → ✅ Removed deprecated allauth context processors
- ❌ **ALLOWED_HOSTS Error** → ✅ Added development hosts
- ❌ **Deprecated Settings** → ✅ Updated to new allauth syntax

### Current Error Expected:
When clicking Google Sign-In with placeholder credentials, you'll see:
```
"The OAuth client was not found"
```
This is expected until you provide real Google credentials.

## Next Steps

1. **Get real Google OAuth2 credentials** from Google Cloud Console
2. **Update credentials** using the management command
3. **Test the complete OAuth2 flow**
4. **Configure for production** with your real domain

The infrastructure is 100% ready - you just need the Google credentials!