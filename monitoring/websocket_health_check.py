
#!/usr/bin/env python3
"""
WebSocket Health Check
Simple health check for WebSocket endpoint
"""

import asyncio
import websockets
import json
from datetime import datetime

async def check_websocket_health(websocket_url: str) -> dict:
    """Check if WebSocket is healthy"""
    try:
        async with websockets.connect(websocket_url, timeout=5) as websocket:
            # Send simple ping
            await websocket.send(json.dumps({"type": "health_check"}))
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=3)
            
            return {
                "status": "healthy",
                "response": json.loads(response),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import sys
    websocket_url = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8000/ws"
    
    result = asyncio.run(check_websocket_health(websocket_url))
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result["status"] == "healthy" else 1)
