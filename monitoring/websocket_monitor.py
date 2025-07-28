
#!/usr/bin/env python3
"""
WebSocket Monitoring Script
Monitors WebSocket connectivity and performance
"""

import asyncio
import json
import logging
import websockets
import time
from datetime import datetime
from typing import Dict, Any

class WebSocketMonitor:
    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.metrics = {
            "connection_attempts": 0,
            "successful_connections": 0,
            "failed_connections": 0,
            "average_response_time": 0,
            "last_check": None
        }
    
    async def check_websocket_health(self) -> Dict[str, Any]:
        """Check WebSocket health"""
        start_time = time.time()
        self.metrics["connection_attempts"] += 1
        
        try:
            async with websockets.connect(self.websocket_url, timeout=10) as websocket:
                # Send ping message
                await websocket.send(json.dumps({"type": "ping", "timestamp": time.time()}))
                
                # Wait for pong response
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)
                
                response_time = time.time() - start_time
                self.metrics["successful_connections"] += 1
                self.metrics["average_response_time"] = (
                    (self.metrics["average_response_time"] * (self.metrics["successful_connections"] - 1) + response_time) /
                    self.metrics["successful_connections"]
                )
                
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "response": response_data,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.metrics["failed_connections"] += 1
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        finally:
            self.metrics["last_check"] = datetime.now().isoformat()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get monitoring metrics"""
        return {
            **self.metrics,
            "success_rate": (
                self.metrics["successful_connections"] / 
                max(self.metrics["connection_attempts"], 1) * 100
            )
        }

async def main():
    """Main WebSocket monitoring function"""
    monitor = WebSocketMonitor("ws://localhost:8000/ws")
    
    # Run health check
    health = await monitor.check_websocket_health()
    metrics = monitor.get_metrics()
    
    print(json.dumps({
        "health": health,
        "metrics": metrics
    }, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
