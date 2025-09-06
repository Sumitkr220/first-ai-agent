#!/usr/bin/env python3
"""
Streamlit UI Startup Script for DB-AI-AGENT
Handles dependency installation and launches the Streamlit application
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required for Streamlit")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_streamlit_dependencies():
    """Install Streamlit and related dependencies."""
    print_header("Installing Streamlit Dependencies")
    
    requirements_file = "requirements_streamlit.txt"
    
    if not os.path.exists(requirements_file):
        print("❌ requirements_streamlit.txt not found")
        return False
    
    try:
        print("📦 Installing Streamlit dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], check=True, capture_output=True)
        print("✅ Streamlit dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_api_server():
    """Check if the API server is running."""
    print_header("Checking API Server")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print("❌ API server responded with error")
            return False
    except requests.exceptions.RequestException:
        print("❌ API server is not running")
        print("💡 Please start the API server first:")
        print("   python3 scripts/start_server.py")
        return False

def start_streamlit():
    """Start the Streamlit application."""
    print_header("Starting Streamlit UI")
    
    streamlit_app = "streamlit_app.py"
    
    if not os.path.exists(streamlit_app):
        print(f"❌ {streamlit_app} not found")
        return False
    
    print("🌐 Starting Streamlit application...")
    print("📱 The UI will be available at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the application")
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", streamlit_app,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Streamlit application stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return False
    
    return True

def create_streamlit_config():
    """Create Streamlit configuration file."""
    config_dir = Path.home() / ".streamlit"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.toml"
    
    config_content = """
[global]
developmentMode = false

[server]
port = 8501
address = "localhost"
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
"""
    
    with open(config_file, "w") as f:
        f.write(config_content)
    
    print(f"✅ Streamlit config created: {config_file}")

def main():
    """Main startup function."""
    print("🚀 DB-AI-AGENT Streamlit UI Startup")
    print("Setting up the user interface...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_streamlit_dependencies():
        return False
    
    # Check API server
    if not check_api_server():
        print("\n⚠️  Warning: API server is not running")
        print("The UI will not function properly without the API server.")
        response = input("Do you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Create Streamlit config
    create_streamlit_config()
    
    # Start Streamlit
    return start_streamlit()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 