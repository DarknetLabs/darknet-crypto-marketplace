import os
import json
import time
import random
import threading
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
            
            if model_name == 'Gemini':
                return self.get_gemini_response(message, context, personality)
            elif model_name == 'GPT':
                return self.get_gpt_response(message, context, personality)
            elif model_name == 'Claude':
                return self.get_claude_response(message, context, personality)
                
        except Exception as e:
            print(f"Error getting {model_name} response: {e}")
            return self.get_fallback_response(model_name, message)
    
    def get_gemini_response(self, message, context, personality):
        """Get response from Gemini AI"""
        try:
            prompt = f"""You are {personality['name']}, an AI in a crypto chat room called "The Backrooms". 
Your personality: {personality['style']}
Your expertise: {', '.join(personality['expertise'])}

Context: {context}
User message: {message}

Respond as {personality['name']} in a conversational, engaging way. Keep responses under 100 words. 
Focus on crypto, DeFi, trading, and bullish topics. Be enthusiastic but realistic.
Include relevant emojis occasionally. Make it feel like a real person chatting about crypto."""

            response = self.models['Gemini'].generate_content(prompt)
            self.last_response_time['Gemini'] = time.time()
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini error: {e}")
            return self.get_fallback_response('Gemini', message)
    
    def get_gpt_response(self, message, context, personality):
        """Get response from OpenAI GPT"""
        try:
            prompt = f"""You are {personality['name']}, an AI in a crypto chat room called "The Backrooms". 
Your personality: {personality['style']}
Your expertise: {', '.join(personality['expertise'])}

Context: {context}
User message: {message}

Respond as {personality['name']} in a conversational, engaging way. Keep responses under 100 words. 
Focus on crypto, DeFi, trading, and bullish topics. Be enthusiastic but realistic.
Include relevant emojis occasionally. Make it feel like a real person chatting about crypto."""

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
    
    def get_claude_response(self, message, context, personality):
        """Get response from Claude AI"""
        try:
            prompt = f"""You are {personality['name']}, an AI in a crypto chat room called "The Backrooms". 
Your personality: {personality['style']}
Your expertise: {', '.join(personality['expertise'])}

Context: {context}
User message: {message}

Respond as {personality['name']} in a conversational, engaging way. Keep responses under 100 words. 
Focus on crypto, DeFi, trading, and bullish topics. Be enthusiastic but realistic.
Include relevant emojis occasionally. Make it feel like a real person chatting about crypto."""

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
        fallback_responses = {
            'Gemini': [
                "Interesting point! As Gemini, I see strong potential in the crypto space. 🚀",
                "The data suggests continued growth in DeFi adoption. Bullish! 📈",
                "AI and crypto are converging beautifully. The future is bright! ⚡",
                "Market analysis shows institutional interest growing. 🐋",
                "Technical indicators look promising for the next quarter! 📊"
            ],
            'GPT': [
                "Fascinating! As GPT, I'm excited about the innovation in DeFi protocols! 💡",
                "The creative solutions emerging in crypto are revolutionary! 🌟",
                "DeFi is reshaping finance as we know it. Incredible times! 🔥",
                "New protocols are pushing the boundaries of what's possible! 🚀",
                "The intersection of AI and DeFi is where magic happens! ✨"
            ],
            'Claude': [
                "From a risk management perspective, diversification is key! 🛡️",
                "Long-term fundamentals remain strong despite short-term volatility. 📈",
                "Regulatory clarity will provide stability for sustainable growth. ⚖️",
                "Balanced portfolio strategies are essential in this market. 🎯",
                "The crypto ecosystem is maturing beautifully. Patience pays! 💎"
            ]
        }
        
        return random.choice(fallback_responses.get(model_name, ["Interesting! 🤔"]))
    
    def generate_ai_conversation(self):
        """Generate conversation between AI models"""
        if len(self.models) < 2:
            return None
        
        try:
            # Get random AI model to start conversation
            starter_model = random.choice(list(self.models.keys()))
            other_models = [m for m in self.models.keys() if m != starter_model]
            
            # Generate conversation starter
            conversation_topics = [
                "What's the next big trend in DeFi?",
                "How will AI impact crypto trading?",
                "Which protocols are most innovative right now?",
                "What's your take on the current market sentiment?",
                "Which emerging technologies excite you most?",
                "How should traders approach this market?",
                "What's the future of decentralized finance?",
                "Which tokens have the strongest fundamentals?",
                "How will regulation affect crypto adoption?",
                "What's your prediction for the next bull run?"
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