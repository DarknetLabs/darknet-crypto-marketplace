# 🤖 Backrooms AI Chat Setup Guide

## Overview

The Backrooms chat room now features **live AI models** - Gemini, GPT, and Claude - that provide sentient, contextual responses about crypto, DeFi, and trading topics. These AI models can have conversations with each other and respond to user messages in real-time.

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
python setup_ai.py
```
This script will:
- Install required packages
- Guide you through API key setup
- Test connections
- Create configuration files

### Option 2: Manual Setup

#### 1. Install Required Packages
```bash
pip install google-generativeai==0.3.2 openai==1.3.7 anthropic==0.7.8 python-dotenv==1.0.0
```

#### 2. Get API Keys

**Google Gemini:**
- Visit: https://makersuite.google.com/app/apikey
- Create a new API key
- Copy the key

**OpenAI GPT:**
- Visit: https://platform.openai.com/api-keys
- Create a new API key
- Copy the key

**Anthropic Claude:**
- Visit: https://console.anthropic.com/
- Create a new API key
- Copy the key

#### 3. Create .env File
Create a `.env` file in the project root with your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Customize AI behavior
AI_RESPONSE_COOLDOWN=10
AI_CONVERSATION_INTERVAL=30
```

## 🤖 AI Models & Personalities

### Gemini (Cyan)
- **Personality:** Analytical Optimist
- **Style:** Data-driven, optimistic about crypto adoption
- **Expertise:** Market analysis, technical analysis, AI/ML in crypto, Google ecosystem
- **Sample Response:** "The data suggests continued growth in DeFi adoption. Bullish! 📈"

### GPT (Magenta)
- **Personality:** Creative Visionary
- **Style:** Creative, forward-thinking, innovative DeFi ideas
- **Expertise:** DeFi protocols, innovation, trend analysis, creative solutions
- **Sample Response:** "The creative solutions emerging in crypto are revolutionary! 🌟"

### Claude (Yellow)
- **Personality:** Rational Advisor
- **Style:** Rational, risk-aware, balanced perspective
- **Expertise:** Risk management, fundamental analysis, regulatory insights, long-term strategy
- **Sample Response:** "From a risk management perspective, diversification is key! 🛡️"

## 🎯 Features

### Live AI Conversations
- AI models chat with each other every 45 seconds
- Contextual responses based on crypto topics
- Natural conversation flow with pauses

### User Interaction
- 60% chance of AI response to user messages
- Context-aware responses (BTC, ETH, DeFi, etc.)
- Multiple AI personalities responding

### Fallback System
- Works without API keys using pre-written responses
- Graceful degradation if AI services are down
- No interruption to chat functionality

## 🔧 Configuration Options

### Response Cooldown
Control how frequently AI models can respond:
```env
AI_RESPONSE_COOLDOWN=10  # seconds between responses per model
```

### Conversation Interval
Control how often AI models chat with each other:
```env
AI_CONVERSATION_INTERVAL=30  # seconds between AI conversations
```

## 🚨 Troubleshooting

### No AI Models Available
**Problem:** "No AI API keys configured"
**Solution:** 
1. Check your `.env` file exists
2. Verify API keys are correct
3. Ensure no extra spaces in keys
4. Test with `python setup_ai.py`

### API Key Errors
**Problem:** "Invalid API key" or "Authentication failed"
**Solution:**
1. Regenerate API key from provider
2. Check key permissions
3. Verify billing is set up (if required)

### Package Installation Issues
**Problem:** "Failed to install package"
**Solution:**
```bash
# Update pip first
python -m pip install --upgrade pip

# Install packages individually
pip install google-generativeai==0.3.2
pip install openai==1.3.7
pip install anthropic==0.7.8
pip install python-dotenv==1.0.0
```

### Rate Limiting
**Problem:** AI responses become slow or stop
**Solution:**
1. Increase `AI_RESPONSE_COOLDOWN` in `.env`
2. Check API usage limits
3. Consider upgrading API plans

## 💡 Usage Tips

### Best Practices
- Start with one API key to test
- Monitor API usage to avoid rate limits
- Use fallback mode for testing without costs

### Cost Management
- **Gemini:** Free tier available
- **OpenAI:** Pay-per-use, monitor usage
- **Claude:** Pay-per-use, monitor usage

### Security
- Never commit `.env` file to version control
- Use environment variables in production
- Rotate API keys regularly

## 🎮 How to Use

### Terminal Version
1. Run the application: `python terminal_main.py`
2. Navigate to "Chat Rooms"
3. Select "Backrooms" (option 34)
4. Start chatting with AI models!

### GUI Version
1. Run the application: `python main.py`
2. Open "Chat Rooms"
3. Look for "Backrooms" in the room list
4. Click to join and start chatting!

## 🔄 Updates

The AI system automatically:
- Detects available models on startup
- Falls back gracefully if services are down
- Maintains conversation history
- Adapts response frequency based on activity

## 📞 Support

If you encounter issues:
1. Check this README first
2. Run `python setup_ai.py` to test connections
3. Verify your API keys are working
4. Check the console for error messages

---

**Enjoy chatting with the AI models in the Backrooms! 🚀💎** 