#!/usr/bin/env python3
"""Quick setup script for essential packages only."""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Quick setup for essential packages."""
    print("🚀 Quick Setup - Essential Packages Only")
    print("=" * 50)
    
    # Essential packages that should work on most systems
    essential_packages = [
        "fastapi",
        "uvicorn", 
        "requests",
        "beautifulsoup4",
        "pydantic",
        "python-multipart",
        "aiofiles",
        "lxml"
    ]
    
    print("📦 Installing essential packages...")
    
    for package in essential_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    
    print("\n🧪 Testing essential imports...")
    
    try:
        import fastapi
        import requests
        from bs4 import BeautifulSoup
        print("✅ Essential packages working!")
        
        # Create directories
        for directory in ["vector_db", "cache", "logs"]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"✅ Created directory: {directory}")
        
        print("\n🎉 Quick setup completed!")
        print("\n📋 You can now run:")
        print("   python main.py")
        print("\n💡 The chatbot will work in basic mode.")
        print("   For full LLM features, install additional packages later:")
        print("   pip install transformers torch sentence-transformers")
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        print("💡 Try manual installation:")
        print("   pip install fastapi uvicorn requests beautifulsoup4")

if __name__ == "__main__":
    main()
