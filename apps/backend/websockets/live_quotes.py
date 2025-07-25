#!/usr/bin/env python3
"""
WebSocket Live Quotes Service
Streams real-time stock quotes and updates to connected clients
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import aiohttp
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LiveQuote:
    """Live quote data structure"""
    ticker: str
    price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open: float
    previous_close: float
    timestamp: datetime
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None

@dataclass
class ClientConnection:
    """Client connection information"""
    websocket: WebSocket
    client_id: str
    subscribed_tickers: Set[str]
    last_heartbeat: datetime
    connection_time: datetime

class LiveQuotesManager:
    """Manages WebSocket connections and live quote streaming"""
    
    def __init__(self):
        self.active_connections: Dict[str, ClientConnection] = {}
        self.ticker_subscribers: Dict[str, Set[str]] = {}
        self.quote_cache: Dict[str, LiveQuote] = {}
        self.is_running = False
        self.update_interval = 2.0  # seconds
        self.heartbeat_interval = 30.0  # seconds
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Handle new WebSocket connection"""
        await websocket.accept()
        
        connection = ClientConnection(
            websocket=websocket,
            client_id=client_id,
            subscribed_tickers=set(),
            last_heartbeat=datetime.now(),
            connection_time=datetime.now()
        )
        
        self.active_connections[client_id] = connection
        
        # Send welcome message
        await self._send_message(client_id, {
            "type": "connection_established",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to Casablanca Insights Live Quotes"
        })
        
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, client_id: str):
        """Handle WebSocket disconnection"""
        if client_id in self.active_connections:
            connection = self.active_connections[client_id]
            
            # Remove from ticker subscriptions
            for ticker in connection.subscribed_tickers:
                if ticker in self.ticker_subscribers:
                    self.ticker_subscribers[ticker].discard(client_id)
                    if not self.ticker_subscribers[ticker]:
                        del self.ticker_subscribers[ticker]
            
            # Remove connection
            del self.active_connections[client_id]
            
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def subscribe_to_ticker(self, client_id: str, ticker: str):
        """Subscribe client to a specific ticker"""
        if client_id not in self.active_connections:
            return
        
        connection = self.active_connections[client_id]
        connection.subscribed_tickers.add(ticker)
        
        if ticker not in self.ticker_subscribers:
            self.ticker_subscribers[ticker] = set()
        self.ticker_subscribers[ticker].add(client_id)
        
        # Send current quote if available
        if ticker in self.quote_cache:
            await self._send_quote_update(client_id, self.quote_cache[ticker])
        
        # Send subscription confirmation
        await self._send_message(client_id, {
            "type": "subscription_confirmed",
            "ticker": ticker,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Client {client_id} subscribed to {ticker}")
    
    async def unsubscribe_from_ticker(self, client_id: str, ticker: str):
        """Unsubscribe client from a specific ticker"""
        if client_id not in self.active_connections:
            return
        
        connection = self.active_connections[client_id]
        connection.subscribed_tickers.discard(ticker)
        
        if ticker in self.ticker_subscribers:
            self.ticker_subscribers[ticker].discard(client_id)
            if not self.ticker_subscribers[ticker]:
                del self.ticker_subscribers[ticker]
        
        # Send unsubscription confirmation
        await self._send_message(client_id, {
            "type": "unsubscription_confirmed",
            "ticker": ticker,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Client {client_id} unsubscribed from {ticker}")
    
    async def handle_message(self, client_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        try:
            message_type = message.get("type")
            
            if message_type == "subscribe":
                ticker = message.get("ticker")
                if ticker:
                    await self.subscribe_to_ticker(client_id, ticker)
            
            elif message_type == "unsubscribe":
                ticker = message.get("ticker")
                if ticker:
                    await self.unsubscribe_from_ticker(client_id, ticker)
            
            elif message_type == "heartbeat":
                await self._handle_heartbeat(client_id)
            
            elif message_type == "get_quote":
                ticker = message.get("ticker")
                if ticker and ticker in self.quote_cache:
                    await self._send_quote_update(client_id, self.quote_cache[ticker])
            
            elif message_type == "get_all_quotes":
                await self._send_all_quotes(client_id)
            
            else:
                await self._send_message(client_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            await self._send_message(client_id, {
                "type": "error",
                "message": "Internal server error",
                "timestamp": datetime.now().isoformat()
            })
    
    async def _handle_heartbeat(self, client_id: str):
        """Handle client heartbeat"""
        if client_id in self.active_connections:
            self.active_connections[client_id].last_heartbeat = datetime.now()
            
            await self._send_message(client_id, {
                "type": "heartbeat_ack",
                "timestamp": datetime.now().isoformat()
            })
    
    async def _send_message(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                await self.disconnect(client_id)
    
    async def _send_quote_update(self, client_id: str, quote: LiveQuote):
        """Send quote update to specific client"""
        await self._send_message(client_id, {
            "type": "quote_update",
            "data": asdict(quote),
            "timestamp": datetime.now().isoformat()
        })
    
    async def _send_all_quotes(self, client_id: str):
        """Send all cached quotes to client"""
        quotes = [asdict(quote) for quote in self.quote_cache.values()]
        await self._send_message(client_id, {
            "type": "all_quotes",
            "data": quotes,
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_quote_update(self, quote: LiveQuote):
        """Broadcast quote update to all subscribed clients"""
        # Update cache
        self.quote_cache[quote.ticker] = quote
        
        # Get subscribers for this ticker
        subscribers = self.ticker_subscribers.get(quote.ticker, set())
        
        # Send update to all subscribers
        message = {
            "type": "quote_update",
            "data": asdict(quote),
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected_clients = []
        for client_id in subscribers:
            try:
                await self._send_message(client_id, message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
    
    async def start_quote_streaming(self):
        """Start the quote streaming service"""
        self.is_running = True
        logger.info("Starting live quote streaming service")
        
        while self.is_running:
            try:
                # Fetch latest quotes for all active tickers
                await self._fetch_and_broadcast_quotes()
                
                # Clean up stale connections
                await self._cleanup_stale_connections()
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in quote streaming: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def stop_quote_streaming(self):
        """Stop the quote streaming service"""
        self.is_running = False
        logger.info("Stopping live quote streaming service")
    
    async def _fetch_and_broadcast_quotes(self):
        """Fetch latest quotes and broadcast to subscribers"""
        try:
            # Get all unique tickers that have subscribers
            active_tickers = list(self.ticker_subscribers.keys())
            
            if not active_tickers:
                return
            
            # Fetch quotes from database or external API
            quotes = await self._fetch_latest_quotes(active_tickers)
            
            # Broadcast each quote
            for quote in quotes:
                await self.broadcast_quote_update(quote)
                
        except Exception as e:
            logger.error(f"Error fetching and broadcasting quotes: {e}")
    
    async def _fetch_latest_quotes(self, tickers: List[str]) -> List[LiveQuote]:
        """Fetch latest quotes from database"""
        quotes = []
        
        try:
            from database.connection import get_db_session
            
            async with get_db_session() as session:
                # Get latest prices for all tickers
                ticker_list = "', '".join(tickers)
                query = f"""
                    SELECT 
                        c.ticker,
                        cp.price,
                        cp.change,
                        cp.change_percent,
                        cp.volume,
                        cp.high,
                        cp.low,
                        cp.open,
                        cp.previous_close,
                        cp.timestamp,
                        c.market_cap_billion,
                        c.pe_ratio,
                        c.dividend_yield
                    FROM companies c
                    LEFT JOIN company_prices cp ON c.id = cp.company_id
                    WHERE c.ticker IN ('{ticker_list}')
                    AND cp.timestamp = (
                        SELECT MAX(timestamp) 
                        FROM company_prices cp2 
                        WHERE cp2.company_id = c.id
                    )
                    ORDER BY c.ticker
                """
                
                result = await session.execute(text(query))
                
                for row in result.fetchall():
                    quote = LiveQuote(
                        ticker=row.ticker,
                        price=float(row.price) if row.price else 0.0,
                        change=float(row.change) if row.change else 0.0,
                        change_percent=float(row.change_percent) if row.change_percent else 0.0,
                        volume=int(row.volume) if row.volume else 0,
                        high=float(row.high) if row.high else 0.0,
                        low=float(row.low) if row.low else 0.0,
                        open=float(row.open) if row.open else 0.0,
                        previous_close=float(row.previous_close) if row.previous_close else 0.0,
                        timestamp=row.timestamp,
                        market_cap=float(row.market_cap_billion) if row.market_cap_billion else None,
                        pe_ratio=float(row.pe_ratio) if row.pe_ratio else None,
                        dividend_yield=float(row.dividend_yield) if row.dividend_yield else None
                    )
                    quotes.append(quote)
                    
        except Exception as e:
            logger.error(f"Error fetching latest quotes: {e}")
        
        return quotes
    
    async def _cleanup_stale_connections(self):
        """Remove connections that haven't sent heartbeat"""
        current_time = datetime.now()
        stale_clients = []
        
        for client_id, connection in self.active_connections.items():
            time_since_heartbeat = (current_time - connection.last_heartbeat).total_seconds()
            
            if time_since_heartbeat > self.heartbeat_interval * 2:  # Allow 2 missed heartbeats
                stale_clients.append(client_id)
        
        for client_id in stale_clients:
            logger.info(f"Removing stale connection: {client_id}")
            await self.disconnect(client_id)

# Global instance
live_quotes_manager = LiveQuotesManager()

# WebSocket endpoint handlers
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for live quotes"""
    await live_quotes_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle message
            await live_quotes_manager.handle_message(client_id, message)
            
    except WebSocketDisconnect:
        await live_quotes_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        await live_quotes_manager.disconnect(client_id)

# Background task to start quote streaming
async def start_quote_streaming_task():
    """Background task to start quote streaming"""
    await live_quotes_manager.start_quote_streaming()

# Utility functions for external use
async def broadcast_quote_update(quote: LiveQuote):
    """Utility function to broadcast quote update"""
    await live_quotes_manager.broadcast_quote_update(quote)

async def get_active_connections_count() -> int:
    """Get number of active connections"""
    return len(live_quotes_manager.active_connections)

async def get_subscribed_tickers() -> List[str]:
    """Get list of tickers with active subscriptions"""
    return list(live_quotes_manager.ticker_subscribers.keys()) 