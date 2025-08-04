#!/usr/bin/env python3
"""
Minimal test to check if FastAPI app starts
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info") 