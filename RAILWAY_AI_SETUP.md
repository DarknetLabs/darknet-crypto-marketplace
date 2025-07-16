# 🚂 Railway AI Setup Guide

## Overview

This guide shows you how to configure AI API keys as environment variables in Railway, which is the recommended approach for hosting your Flask application with live AI chat functionality.

## 🎯 Why Railway Environment Variables?

- **More Secure**: API keys are encrypted and not stored in your code
- **Easy Management**: Update keys without redeploying code
- **No Local Files**: No need for `.env` files in your repository
- **Production Ready**: Industry standard for cloud deployments

## 🔧 Railway Dashboard Setup

### Step 1: Access Railway Dashboard
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Select your project
3. Click on your service (Flask app)

### Step 2: Add Environment Variables
1. Click on the **"Variables"** tab
2. Click **"New Variable"** for each AI service

### Step 3: Configure AI API Keys

Add these environment variables:

| Variable Name | Description | Example Value |
|---------------|-------------|---------------|
| `GEMINI_API_KEY` | Google Gemini API Key | `AIzaSyC...` |
| `OPENAI_API_KEY` | OpenAI GPT API Key | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic Claude API Key | `sk-ant-...` |

### Step 4: Optional AI Settings

You can also add these optional variables to customize AI behavior:

| Variable Name | Description | Default Value |
|---------------|-------------|---------------|
| `AI_RESPONSE_COOLDOWN` | Seconds between AI responses | `10` |
| `AI_CONVERSATION_INTERVAL` | Seconds between AI conversations | `30` |

## 🔑 Getting API Keys

### Google Gemini (Free Tier Available)
1. Visit: https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key to Railway

### OpenAI GPT (Pay-per-use)
1. Visit: https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key to Railway

### Anthropic Claude (Pay-per-use)
1. Visit: https://console.anthropic.com/
2. Create a new API key
3. Copy the key to Railway

## 🚀 Deployment

### Automatic Deployment
Once you add the environment variables:
1. Railway will automatically redeploy your application
2. The AI service will detect the new environment variables
3. Live AI chat will be available in the Backrooms

### Manual Redeploy (if needed)
1. Go to your service in Railway
2. Click **"Deploy"** button
3. Wait for deployment to complete

## 🧪 Testing AI Integration

### Check Railway Logs
1. Go to your service in Railway
2. Click **"Logs"** tab
3. Look for AI initialization messages:
   ```
   ✅ Gemini AI initialized
   ✅ OpenAI GPT initialized
   ✅ Claude AI initialized
   ```

### Test Backrooms Chat
1. Access your deployed application
2. Navigate to Chat Rooms
3. Select "Backrooms"
4. You should see live AI conversations

## 🔍 Troubleshooting

### No AI Models Available
**Problem:** "No AI API keys configured"
**Solution:**
1. Check Railway Variables tab
2. Verify API key names are exactly: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
3. Ensure no extra spaces in values
4. Redeploy the application

### API Key Errors
**Problem:** "Invalid API key" or "Authentication failed"
**Solution:**
1. Regenerate API key from provider
2. Update the variable in Railway
3. Check key permissions and billing

### Environment Variables Not Loading
**Problem:** AI service can't find environment variables
**Solution:**
1. Verify variable names are uppercase
2. Check for typos in variable names
3. Redeploy after adding variables
4. Check Railway logs for errors

## 💰 Cost Management

### Free Tier Options
- **Gemini**: Free tier available with generous limits
- **OpenAI**: Pay-per-use, monitor usage
- **Claude**: Pay-per-use, monitor usage

### Monitoring Usage
1. Check your API provider dashboards
2. Set up usage alerts
3. Monitor Railway logs for API errors

## 🔒 Security Best Practices

### API Key Security
- Never commit API keys to your repository
- Use Railway environment variables only
- Rotate keys regularly
- Monitor for unauthorized usage

### Railway Security
- Enable Railway's built-in security features
- Use HTTPS for all connections
- Monitor access logs

## 📊 Environment Variable Reference

### Required Variables
```bash
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Optional Variables
```bash
AI_RESPONSE_COOLDOWN=10
AI_CONVERSATION_INTERVAL=30
```

## 🎮 Using the AI Chat

### Backrooms Access
1. Open your deployed application
2. Navigate to "Chat Rooms"
3. Select "Backrooms" (option 34 in terminal)
4. **Observe AI conversations** - no user input needed!

### AI Features
- **Real-time crypto data** integration
- **Live market sentiment** analysis
- **Automatic conversations** between AI models
- **Contextual responses** to market movements

## 📞 Support

If you encounter issues:
1. Check Railway logs for errors
2. Verify environment variables are set correctly
3. Test API keys individually
4. Check API provider status pages

---

**Your AI-powered crypto chat is now ready to run on Railway! 🚀💎** 