#!/usr/bin/env python3
"""
Server startup script for DB-AI-AGENT
Handles server initialization and configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def start_server():
    """Start the FastAPI server"""
    
    print("🚀 Starting DB-AI-AGENT server...")
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run setup first.")
        return False
    
    # Set environment variables
    os.environ.setdefault("MONGODB_DATABASE", "sample_supplies")
    
    # Start the server
    try:
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main_simple:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        print("✅ Starting server on http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔧 Press Ctrl+C to stop the server")
        
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_server() 