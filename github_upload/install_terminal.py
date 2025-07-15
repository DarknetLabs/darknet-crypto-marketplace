#!/usr/bin/env python3
"""
Installation script for DARKNET CRYPTO MARKETPLACE Terminal Version
"""

import subprocess
import sys
import os
import platform

def print_banner():
    """Print installation banner"""
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                    DARKNET CRYPTO MARKETPLACE v2.1                           ║")
    print("║                              TERMINAL INSTALLER                              ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install from requirements file
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_terminal.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def test_installation():
    """Test if the installation was successful"""
    print("\n🧪 Testing installation...")
    
    try:
        # Try to import required modules
        import requests
        import cryptography
        import web3
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_launcher_scripts():
    """Create launcher scripts for different platforms"""
    print("\n🚀 Creating launcher scripts...")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Windows batch file already exists
        print("✅ Windows launcher (run_terminal.bat) ready")
    else:
        # Make shell script executable
        try:
            os.chmod("run_terminal.sh", 0o755)
            print("✅ Unix/Linux launcher (run_terminal.sh) ready")
        except Exception as e:
            print(f"⚠️  Warning: Could not make shell script executable: {e}")

def show_usage_instructions():
    """Show usage instructions"""
    print("\n🎯 Installation Complete!")
    print("\nTo start the application:")
    
    system = platform.system().lower()
    if system == "windows":
        print("   Option 1: Double-click 'run_terminal.bat'")
        print("   Option 2: Run 'python terminal_main.py'")
    else:
        print("   Option 1: Run './run_terminal.sh'")
        print("   Option 2: Run 'python3 terminal_main.py'")
    
    print("\n📖 For more information, see TERMINAL_README.md")
    print("🔧 For troubleshooting, check the README file")

def main():
    """Main installation function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        return
    
    # Install dependencies
    if not install_dependencies():
        input("\nPress Enter to exit...")
        return
    
    # Test installation
    if not test_installation():
        input("\nPress Enter to exit...")
        return
    
    # Create launcher scripts
    create_launcher_scripts()
    
    # Show usage instructions
    show_usage_instructions()
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 