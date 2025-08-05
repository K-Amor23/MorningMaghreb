#!/bin/bash

echo "🚀 Starting Morning Maghreb Live Ticker Orchestrator..."
echo "======================================================"
echo "📈 Priority tickers: ATW, IAM, BCP, BMCE, CIH, WAA, SAH, ADH, LBV, MAR, LES, CEN, HOL, LAF, MSA, TMA"
echo "⏰ Update interval: 5 minutes"
echo "📊 Sources: African Markets, Casablanca Bourse, Wafa Bourse"
echo "="*60

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the live orchestrator
python3 scripts/live_ticker_orchestrator.py

echo ""
echo "🛑 Live ticker orchestrator stopped."
echo "📝 Logs saved to: logs/live_ticker_orchestrator.log" 