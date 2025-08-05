#!/bin/bash

echo "🧪 Testing Morning Maghreb data collection..."
echo "============================================="

# Run the simple data collection script
python3 scripts/collect_market_data_simple.py

echo ""
echo "✅ Test completed. Check logs/data_collection.log for details."
