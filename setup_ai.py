#!/usr/bin/env python3
"""
AI Setup Script for Backrooms Chat
Helps users install required packages and configure API keys
"""

import os
import sys
import subprocess
import getpass

def print_banner():
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                        BACKROOMS AI CHAT SETUP                               ║")
    print("║                    Gemini • GPT • Claude Integration                        ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()

def install_packages():
    """Install required AI packages"""
    print("📦 Installing required AI packages...")
    
    packages = [
        'google-generativeai==0.3.2',
        'openai==1.3.7', 
        'anthropic==0.7.8',
        'python-dotenv==1.0.0'
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def get_api_key(service_name, url):
    """Get API key from user"""
    print(f"\n🔑 {service_name} API Key Setup")
    print(f"Get your API key from: {url}")
    print("Enter your API key (or press Enter to skip):")
    
    api_key = getpass.getpass("API Key: ").strip()
    return api_key if api_key else None

def create_env_file():
    """Create .env file with API keys"""
    print("\n🔧 Setting up API keys...")
    
    # Get API keys from user
    gemini_key = get_api_key("Gemini", "https://makersuite.google.com/app/apikey")
    openai_key = get_api_key("OpenAI GPT", "https://platform.openai.com/api-keys")
    claude_key = get_api_key("Anthropic Claude", "https://console.anthropic.com/")
    
    # Create .env file
    env_content = []
    
    if gemini_key:
        env_content.append(f"GEMINI_API_KEY={gemini_key}")
    else:
        env_content.append("# GEMINI_API_KEY=your_gemini_api_key_here")
    
    if openai_key:
        env_content.append(f"OPENAI_API_KEY={openai_key}")
    else:
        env_content.append("# OPENAI_API_KEY=your_openai_api_key_here")
    
    if claude_key:
        env_content.append(f"ANTHROPIC_API_KEY={claude_key}")
    else:
        env_content.append("# ANTHROPIC_API_KEY=your_anthropic_api_key_here")
    
    # Add optional settings
    env_content.extend([
        "",
        "# Optional: Customize AI behavior",
        "AI_RESPONSE_COOLDOWN=10",
        "AI_CONVERSATION_INTERVAL=30"
    ])
    
    try:
        with open('.env', 'w') as f:
            f.write('\n'.join(env_content))
        print("✅ .env file created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_ai_connection():
    """Test AI model connections"""
    print("\n🧪 Testing AI model connections...")
    
    try:
        from ai_service import AIService
        ai_service = AIService()
        
        available_models = ai_service.get_available_models()
        
        if not available_models:
            print("⚠️  No AI models are available. Check your API keys in .env file")
            return False
        
        print(f"✅ Available AI models: {', '.join(available_models)}")
        
        # Test a simple response
        for model in available_models[:1]:  # Test first available model
            print(f"Testing {model}...")
            response = ai_service.get_ai_response(model, "Hello!", "Test message")
            if response:
                print(f"✅ {model} is working: {response[:50]}...")
            else:
                print(f"❌ {model} failed to respond")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI models: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    print("This script will help you set up the live AI chat feature for the Backrooms.")
    print("You'll need API keys from Google Gemini, OpenAI, and/or Anthropic Claude.")
    print()
    
    # Install packages
    if not install_packages():
        print("❌ Package installation failed. Please check your internet connection.")
        return
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file.")
        return
    
    # Test connections
    if test_ai_connection():
        print("\n🎉 Setup completed successfully!")
        print("You can now use the live AI chat in the Backrooms!")
    else:
        print("\n⚠️  Setup completed with warnings.")
        print("The chat will work with fallback responses until you configure valid API keys.")
    
    print("\nTo update your API keys later, edit the .env file or run this script again.")

if __name__ == "__main__":
    main() 