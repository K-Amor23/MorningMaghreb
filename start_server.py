#!/usr/bin/env python3
"""
Start server with proper environment loading
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from the root directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Verify environment is loaded
api_key = os.getenv("OpenAi_API_KEY")
if api_key:
    print(f"✅ OpenAI API key loaded: {api_key[:20]}...")
else:
    print("❌ OpenAI API key not found")

# Start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 