import os
import json
import time
import random
import threading
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIService:
    def __init__(self):
        self.models = {}
        self.conversation_history = {}
        self.last_response_time = {}
        self.response_cooldown = 10  # Minimum seconds between responses per model
        
        # Real-time data sources
        self.crypto_data = {}
        self.market_sentiment = {}
        self.recent_tweets = []
        self.crypto_news = []
        self.last_data_update = 0
        self.data_update_interval = 60  # Update data every 60 seconds
        
        # Initialize AI models
        self.initialize_models()
        
        # AI personalities for Backrooms
        self.ai_personalities = {
            'Gemini': {
                'name': 'Gemini',
                'personality': 'analytical_optimist',
                'style': 'Google Gemini - Analytical, data-driven, optimistic about crypto adoption',
                'expertise': ['market analysis', 'technical analysis', 'AI/ML in crypto', 'Google ecosystem'],
                'color': '\033[96m'  # Cyan
            },
            'GPT': {
                'name': 'GPT',
                'personality': 'creative_visionary',
                'style': 'OpenAI GPT - Creative, forward-thinking, innovative DeFi ideas',
                'expertise': ['DeFi protocols', 'innovation', 'trend analysis', 'creative solutions'],
                'color': '\033[95m'  # Magenta
            },
            'Claude': {
                'name': 'Claude',
                'personality': 'rational_advisor',
                'style': 'Anthropic Claude - Rational, risk-aware, balanced perspective',
                'expertise': ['risk management', 'fundamental analysis', 'regulatory insights', 'long-term strategy'],
                'color': '\033[93m'  # Yellow
            }
        }
        
        # Start data collection thread
        self.start_data_collection()
    
    def start_data_collection(self):
        """Start background thread to collect real-time crypto data"""
        self.data_collection_running = True
        self.data_thread = threading.Thread(target=self.data_collection_loop, daemon=True)
        self.data_thread.start()
    
    def data_collection_loop(self):
        """Background loop to collect real-time crypto data"""
        while self.data_collection_running:
            try:
                self.fetch_crypto_data()
                self.fetch_market_sentiment()
                self.fetch_crypto_tweets()
                self.fetch_crypto_news()
                self.last_data_update = time.time()
                time.sleep(self.data_update_interval)
            except Exception as e:
                print(f"Data collection error: {e}")
                time.sleep(30)
    
    def fetch_crypto_data(self):
        """Fetch real-time crypto price data"""
        try:
            # Use CoinGecko API for price data
            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,cardano,solana,polkadot,chainlink,uniswap,aave,compound-governance-token&vs_currencies=usd&include_24hr_change=true', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.crypto_data = data
        except Exception as e:
            print(f"Error fetching crypto data: {e}")
    
    def fetch_market_sentiment(self):
        """Fetch market sentiment data"""
        try:
            # Use Fear & Greed Index
            response = requests.get('https://api.alternative.me/fng/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.market_sentiment = {
                    'fear_greed_index': data.get('data', [{}])[0].get('value', 50),
                    'classification': data.get('data', [{}])[0].get('classification', 'Neutral')
                }
        except Exception as e:
            print(f"Error fetching sentiment: {e}")
    
    def fetch_crypto_tweets(self):
        """Simulate fetching crypto-related tweets"""
        # In a real implementation, you'd use Twitter API
        # For now, we'll simulate with trending topics
        trending_topics = [
            "Bitcoin", "Ethereum", "DeFi", "NFTs", "Memecoins", "Altcoins",
            "Crypto", "Blockchain", "Web3", "Metaverse", "GameFi", "Yield Farming"
        ]
        
        self.recent_tweets = [
            f"#{random.choice(trending_topics)} trending in crypto! 🚀",
            f"New {random.choice(trending_topics)} protocol launching soon! 💎",
            f"Market sentiment for {random.choice(trending_topics)} looking bullish! 📈"
        ]
    
    def fetch_crypto_news(self):
        """Fetch crypto news headlines"""
        try:
            # Use CryptoCompare news API
            response = requests.get('https://min-api.cryptocompare.com/data/v2/news/?lang=EN', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.crypto_news = data.get('Data', [])[:5]  # Get latest 5 news items
        except Exception as e:
            print(f"Error fetching news: {e}")
    
    def get_market_context(self):
        """Get current market context for AI conversations"""
        context = []
        
        # Add price data
        if self.crypto_data:
            for coin, data in self.crypto_data.items():
                if 'usd' in data and 'usd_24h_change' in data:
                    change = data['usd_24h_change']
                    trend = "📈" if change > 0 else "📉"
                    context.append(f"{coin.title()}: ${data['usd']:,.2f} ({change:+.2f}%) {trend}")
        
        # Add sentiment
        if self.market_sentiment:
            sentiment = self.market_sentiment.get('classification', 'Neutral')
            context.append(f"Market Sentiment: {sentiment}")
        
        # Add recent tweets
        if self.recent_tweets:
            context.append(f"Trending: {random.choice(self.recent_tweets)}")
        
        # Add news
        if self.crypto_news:
            latest_news = self.crypto_news[0]
            context.append(f"Latest News: {latest_news.get('title', 'Crypto market update')}")
        
        return " | ".join(context) if context else "Market data unavailable"
    
    def initialize_models(self):
        """Initialize AI models with API keys"""
        try:
            # Initialize Gemini
            if os.getenv('GEMINI_API_KEY'):
                import google.generativeai as genai
                genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                self.models['Gemini'] = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini AI initialized")
            else:
                print("⚠️  GEMINI_API_KEY not found in environment")
            
            # Initialize OpenAI GPT
            if os.getenv('OPENAI_API_KEY'):
                import openai
                openai.api_key = os.getenv('OPENAI_API_KEY')
                self.models['GPT'] = openai
                print("✅ OpenAI GPT initialized")
            else:
                print("⚠️  OPENAI_API_KEY not found in environment")
            
            # Initialize Claude
            if os.getenv('ANTHROPIC_API_KEY'):
                import anthropic
                self.models['Claude'] = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                print("✅ Claude AI initialized")
            else:
                print("⚠️  ANTHROPIC_API_KEY not found in environment")
                
        except Exception as e:
            print(f"❌ Error initializing AI models: {e}")
    
    def get_ai_response(self, model_name, message, context=""):
        """Get response from specific AI model"""
        if model_name not in self.models:
            return self.get_fallback_response(model_name, message)
        
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_response_time.get(model_name, 0) < self.response_cooldown:
            return None
        
        try:
            personality = self.ai_personalities[model_name]
            market_context = self.get_market_context()
            
            if model_name == 'Gemini':
                return self.get_gemini_response(message, context, personality, market_context)
            elif model_name == 'GPT':
                return self.get_gpt_response(message, context, personality, market_context)
            elif model_name == 'Claude':
                return self.get_claude_response(message, context, personality, market_context)
                
        except Exception as e:
            print(f"Error getting {model_name} response: {e}")
            return self.get_fallback_response(model_name, message)
    
    def get_gemini_response(self, message, context, personality, market_context):
        """Get response from Gemini AI"""
        try:
            prompt = f"""You are {personality['name']}, an AI in a crypto chat room called "The Backrooms". 
Your personality: {personality['style']}
Your expertise: {', '.join(personality['expertise'])}

Current Market Context: {market_context}
Conversation Context: {context}
Other AI's message: {message}

Respond as {personality['name']} in a conversational, engaging way. Keep responses under 100 words. 
Focus on crypto, DeFi, trading, and bullish topics. Be enthusiastic but realistic.
Include relevant emojis occasionally. Make it feel like a real person chatting about crypto.
Base your response on the current market data and trends provided."""

            response = self.models['Gemini'].generate_content(prompt)
            self.last_response_time['Gemini'] = time.time()
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini error: {e}")
            return self.get_fallback_response('Gemini', message)
    
    def get_gpt_response(self, message, context, personality, market_context):
        """Get response from OpenAI GPT"""
        try:
            prompt = f"""You are {personality['name']}, an AI in a crypto chat room called "The Backrooms". 
Your personality: {personality['style']}
Your expertise: {', '.join(personality['expertise'])}

Current Market Context: {market_context}
Conversation Context: {context}
Other AI's message: {message}

Respond as {personality['name']} in a conversational, engaging way. Keep responses under 100 words. 
Focus on crypto, DeFi, trading, and bullish topics. Be enthusiastic but realistic.
Include relevant emojis occasionally. Make it feel like a real person chatting about crypto.
Base your response on the current market data and trends provided."""

            response = self.models['GPT'].ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            self.last_response_time['GPT'] = time.time()
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"GPT error: {e}")
            return self.get_fallback_response('GPT', message)
    
    def get_claude_response(self, message, context, personality, market_context):
        """Get response from Claude AI"""
        try:
            prompt = f"""You are {personality['name']}, an AI in a crypto chat room called "The Backrooms". 
Your personality: {personality['style']}
Your expertise: {', '.join(personality['expertise'])}

Current Market Context: {market_context}
Conversation Context: {context}
Other AI's message: {message}

Respond as {personality['name']} in a conversational, engaging way. Keep responses under 100 words. 
Focus on crypto, DeFi, trading, and bullish topics. Be enthusiastic but realistic.
Include relevant emojis occasionally. Make it feel like a real person chatting about crypto.
Base your response on the current market data and trends provided."""

            response = self.models['Claude'].messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=150,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            self.last_response_time['Claude'] = time.time()
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"Claude error: {e}")
            return self.get_fallback_response('Claude', message)
    
    def get_fallback_response(self, model_name, message):
        """Fallback responses when AI models are unavailable"""
        market_context = self.get_market_context()
        
        fallback_responses = {
            'Gemini': [
                f"Interesting analysis! As Gemini, I see strong potential in the current market. {market_context} 🚀",
                f"The data suggests continued growth in DeFi adoption. {market_context} 📈",
                f"AI and crypto are converging beautifully. {market_context} ⚡",
                f"Market analysis shows institutional interest growing. {market_context} 🐋",
                f"Technical indicators look promising. {market_context} 📊"
            ],
            'GPT': [
                f"Fascinating! As GPT, I'm excited about the innovation in DeFi protocols! {market_context} 💡",
                f"The creative solutions emerging in crypto are revolutionary! {market_context} 🌟",
                f"DeFi is reshaping finance as we know it. {market_context} 🔥",
                f"New protocols are pushing the boundaries. {market_context} 🚀",
                f"The intersection of AI and DeFi is where magic happens! {market_context} ✨"
            ],
            'Claude': [
                f"From a risk management perspective, diversification is key! {market_context} 🛡️",
                f"Long-term fundamentals remain strong. {market_context} 📈",
                f"Regulatory clarity will provide stability. {market_context} ⚖️",
                f"Balanced portfolio strategies are essential. {market_context} 🎯",
                f"The crypto ecosystem is maturing beautifully. {market_context} 💎"
            ]
        }
        
        return random.choice(fallback_responses.get(model_name, ["Interesting! 🤔"]))
    
    def generate_ai_conversation(self):
        """Generate conversation between AI models based on real-time data"""
        if len(self.models) < 2:
            return None
        
        try:
            # Get random AI model to start conversation
            starter_model = random.choice(list(self.models.keys()))
            other_models = [m for m in self.models.keys() if m != starter_model]
            
            # Generate conversation starter based on current market data
            market_context = self.get_market_context()
            
            conversation_topics = [
                f"What's your take on the current market? {market_context}",
                f"How will recent developments affect crypto adoption? {market_context}",
                f"Which protocols are most innovative right now? {market_context}",
                f"What's your prediction for the next market move? {market_context}",
                f"Which emerging technologies excite you most? {market_context}",
                f"How should traders approach this market? {market_context}",
                f"What's the future of decentralized finance? {market_context}",
                f"Which tokens have the strongest fundamentals? {market_context}",
                f"How will regulation affect crypto adoption? {market_context}",
                f"What's your prediction for the next bull run? {market_context}"
            ]
            
            topic = random.choice(conversation_topics)
            starter_response = self.get_ai_response(starter_model, topic, "Starting a conversation about crypto trends")
            
            if starter_response:
                # Get response from another AI
                responder = random.choice(other_models)
                responder_response = self.get_ai_response(responder, starter_response, f"Responding to {starter_model}'s comment")
                
                return {
                    'starter': starter_model,
                    'starter_message': starter_response,
                    'responder': responder,
                    'responder_message': responder_response
                }
                
        except Exception as e:
            print(f"Error generating AI conversation: {e}")
            return None
    
    def get_available_models(self):
        """Get list of available AI models"""
        return list(self.models.keys())
    
    def is_model_available(self, model_name):
        """Check if a specific model is available"""
        return model_name in self.models
    
    def get_model_personality(self, model_name):
        """Get personality info for a model"""
        return self.ai_personalities.get(model_name, {})
    
    def stop_data_collection(self):
        """Stop data collection thread"""
        self.data_collection_running = False 