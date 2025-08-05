#!/bin/bash

echo "🧪 Testing Morning Maghreb Comprehensive Data Collection..."
echo "=========================================================="

# Run the comprehensive data collection script
python3 scripts/collect_market_data_comprehensive.py

echo ""
echo "✅ Comprehensive test completed. Check logs/comprehensive_data_collection.log for details."
echo ""
echo "📊 Expected Data Sources:"
echo "  - 78 companies from African Markets"
echo "  - ETFs from AMMC, CSE, and institutional sites"
echo "  - Bonds from government and corporate issuers"
echo "  - Market data from Casablanca Bourse"
echo "  - Banking data from Bank Al Maghrib" 