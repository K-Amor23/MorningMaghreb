#!/bin/bash

echo "🧪 Testing Morning Maghreb Live Ticker Orchestrator..."
echo "======================================================"

# Run a single test update
python3 scripts/live_ticker_orchestrator.py test

echo ""
echo "✅ Live ticker test completed. Check logs/live_ticker_orchestrator.log for details."
echo ""
echo "📊 Expected Results:"
echo "  - Live data from 16 priority tickers"
echo "  - Data from multiple sources (African Markets, Casablanca Bourse, Wafa Bourse)"
echo "  - Real-time price updates and market movements"
echo "  - Database updates and file saves" 