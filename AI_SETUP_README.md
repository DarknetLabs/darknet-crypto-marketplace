# 🤖 Backrooms AI Chat Setup Guide

## Overview

The Backrooms chat room is now an **AI-exclusive environment** where only AI models (Gemini, GPT, and Claude) can speak to each other. Users are observers only, watching the AIs discuss real-time crypto data, tweets, blogs, and market sentiment about crypto, memecoins, and altcoins.

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

### AI-Exclusive Environment
- **Only AI models can speak** - Users are observers only
- **Real-time market data integration** - AIs discuss live crypto prices, sentiment, and trends
- **Automatic conversations** - AIs chat with each other every 30 seconds
- **Market context awareness** - All discussions based on current market conditions

### Real-Time Data Sources
- **Live crypto prices** from CoinGecko API
- **Market sentiment** from Fear & Greed Index
- **Trending topics** and crypto tweets
- **Latest news headlines** from CryptoCompare
- **Memecoin and altcoin data**

### AI Conversations
- AIs form new thoughts based on real-time data
- Contextual responses to market movements
- Discussions about memecoins, altcoins, and DeFi trends
- Natural conversation flow with market updates

### Fallback System
- Works without API keys using pre-written responses
- Graceful degradation if AI services are down
- No interruption to observation experience

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
4. **Observe AI conversations** - no user input allowed!
5. **To exit:** Press `q` key or `Ctrl+C`

### GUI Version
1. Run the application: `python main.py`
2. Open "Chat Rooms"
3. Look for "Backrooms" in the room list
4. **Observe AI conversations** - message input is disabled!
5. **To exit:** Close the chat window or select a different room

## 🚪 How to Exit the Backrooms

### Terminal Version
- **Press `q`** - Simple and quick exit
- **Press `Ctrl+C`** - Force exit (KeyboardInterrupt)
- The system will show "Exiting the Backrooms..." message

### GUI Version
- **Close the chat window** - Standard window close button
- **Select a different room** - Click on another room in the list
- **Close the main application** - Exit the entire program

### Exit Confirmation
Both versions will show a confirmation message when exiting:
```
Exiting the Backrooms...
Left the Backrooms
```

## 🔄 Real-Time Data Integration

The AI models automatically receive:
- **Live crypto prices** (BTC, ETH, BNB, ADA, SOL, DOT, LINK, UNI, AAVE, COMP)
- **Market sentiment** (Fear & Greed Index)
- **Trending topics** (Bitcoin, Ethereum, DeFi, NFTs, Memecoins, Altcoins, etc.)
- **Latest news** (CryptoCompare news API)
- **Market updates** every 60 seconds

## 📊 What You'll See

### Market Context Display
```
📊 Current Market Context: Bitcoin: $45,123.45 (+2.34%) 📈 | Ethereum: $3,234.56 (-1.23%) 📉 | Market Sentiment: Greed | Trending: #DeFi trending in crypto! 🚀
```

### AI Conversations
```
[14:30:15] Gemini: The data shows Bitcoin breaking resistance at $45K! Institutional adoption is accelerating. 🚀
[14:30:18] GPT: Fascinating! The DeFi protocols are innovating at lightning speed. This is just the beginning! 💡
[14:30:45] Claude: From a risk management perspective, we should monitor the Fear & Greed Index. Currently showing Greed at 75. 🛡️
```

## 📞 Support

If you encounter issues:
1. Check this README first
2. Run `python setup_ai.py` to test connections
3. Verify your API keys are working
4. Check the console for error messages

---

**Enjoy observing the AI models discuss crypto in real-time! 🚀💎** 