#!/usr/bin/env python3
"""
Setup script for DB-AI-AGENT project
Handles environment setup, dependencies, and initial configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_project():
    """Setup the DB-AI-AGENT project"""
    
    print("🚀 Setting up DB-AI-AGENT project...")
    
    # Create necessary directories
    directories = [
        "scripts",
        "tests",
        "docs",
        "logs",
        "data",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(env_file, "w") as f:
            f.write("""# MongoDB Configuration
MONGODB_URI=your_mongodb_connection_string_here
MONGODB_DATABASE=sample_supplies

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Application Configuration
APP_NAME=DB-AI-AGENT
DEBUG=True
LOG_LEVEL=INFO
""")
        print("✅ Created .env file")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    print("🎉 Project setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment: source venv/bin/activate")
    print("2. Start the server: python scripts/start_server.py")
    print("3. Test the API: python scripts/test_api.py")
    
    return True

if __name__ == "__main__":
    setup_project() 