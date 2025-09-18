#!/usr/bin/env python3
"""Setup script for the Jira Customer Support Chatbot."""

import os
import sys
import subprocess
import platform

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

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies."""
    print("\n💡 First, let's upgrade pip...")
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Pip upgrade failed, continuing anyway...")
    
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("\n❌ Dependency installation failed. This might be due to:")
        print("   1. Incompatible package versions")
        print("   2. Missing system dependencies")
        print("   3. Network connectivity issues")
        print("\n💡 Try these solutions:")
        print("   - Update pip: pip install --upgrade pip")
        print("   - Install system dependencies: apt-get install python3-dev build-essential")
        print("   - Use conda instead: conda install pytorch transformers")
        return False
    return True

def create_directories():
    """Create necessary directories."""
    directories = ["vector_db", "cache", "logs"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory already exists: {directory}")

def setup_environment():
    """Setup environment configuration."""
    env_file = ".env"
    env_example = "env.example"
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            print(f"\n📝 Creating {env_file} from {env_example}")
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print(f"✅ Created {env_file}")
            print("💡 Please edit .env file with your Jira credentials (optional)")
        else:
            print(f"⚠️  {env_example} not found, skipping environment setup")
    else:
        print(f"📁 {env_file} already exists")

def test_installation():
    """Test the installation."""
    print("\n🧪 Testing installation...")
    
    # Test imports
    try:
        import fastapi
        import requests
        from bs4 import BeautifulSoup  # This is the correct import
        print("✅ Core packages imported successfully")
        
        # Test optional packages
        optional_packages = []
        try:
            import transformers
            optional_packages.append("transformers")
        except ImportError:
            print("⚠️  transformers not available - LLM will use fallback mode")
        
        try:
            import chromadb
            optional_packages.append("chromadb")
        except ImportError:
            print("⚠️  chromadb not available - documentation search will be limited")
        
        if optional_packages:
            print(f"✅ Optional packages available: {', '.join(optional_packages)}")
        
    except ImportError as e:
        print(f"❌ Core import error: {e}")
        print("💡 Try: pip install beautifulsoup4")
        return False
    
    # Test configuration
    try:
        from config import config
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up Jira Customer Support Chatbot...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_environment()
    
    # Test installation
    if not test_installation():
        print("\n❌ Setup failed at testing")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your Jira credentials (optional)")
    print("2. Run: python main.py")
    print("3. Open browser to: http://localhost:8000")
    print("4. Run tests: python test_chatbot.py")
    print("\n📚 Documentation:")
    print("- README.md: Overview and basic usage")
    print("- TESTING.md: Comprehensive testing guide")
    print("- DOCUMENTATION.md: Technical documentation")
    
    print("\n🐳 Docker option:")
    print("docker-compose up --build")

if __name__ == "__main__":
    main()
