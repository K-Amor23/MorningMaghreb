#!/usr/bin/env python3
"""
Test script for trading data pipeline
Tests yfinance integration with Moroccan stocks
"""

import yfinance as yf
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import time

def test_yfinance_moroccan_stocks():
    """Test fetching data for Moroccan stocks"""
    
    # Test with a few known Moroccan stocks
    test_tickers = [
        "ATW.MA",  # Attijariwafa Bank
        "IAM.MA",  # Maroc Telecom
        "BCP.MA",  # Banque Centrale Populaire
        "BMCE.MA", # BMCE Bank of Africa
        "CIH.MA",  # CIH Bank
    ]
    
    results = []
    
    print("Testing yfinance with Moroccan stocks...")
    print("=" * 50)
    
    for ticker in test_tickers:
        try:
            print(f"Fetching data for {ticker}...")
            
            # Fetch 30 days of data
            df = yf.download(
                ticker, 
                period="30d", 
                interval="1d",
                progress=False
            )
            
            if df.empty:
                print(f"❌ No data found for {ticker}")
                results.append({
                    'ticker': ticker,
                    'success': False,
                    'error': 'No data found'
                })
                continue
            
            # Get latest price
            latest_price = df['Close'].iloc[-1]
            latest_date = df.index[-1]
            
            print(f"✅ {ticker}: {latest_price:.2f} MAD (as of {latest_date.strftime('%Y-%m-%d')})")
            print(f"   Data points: {len(df)}")
            print(f"   Date range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
            
            results.append({
                'ticker': ticker,
                'success': True,
                'latest_price': float(latest_price),
                'latest_date': latest_date.isoformat(),
                'data_points': len(df),
                'date_range': {
                    'start': df.index[0].isoformat(),
                    'end': df.index[-1].isoformat()
                }
            })
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")
            results.append({
                'ticker': ticker,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    print(f"Successful: {successful}/{total} ({successful/total*100:.1f}%)")
    
    # Save results
    output_file = Path("test_trading_data_results.json")
    with open(output_file, 'w') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'total': total,
                'successful': successful,
                'success_rate': successful/total if total > 0 else 0
            }
        }, f, indent=2)
    
    print(f"Results saved to: {output_file}")
    
    return results

def test_with_cse_companies():
    """Test with actual CSE companies from our data"""
    
    try:
        # Load CSE companies
        data_file = Path("apps/backend/data/cse_companies_african_markets.json")
        with open(data_file, 'r') as f:
            companies = json.load(f)
        
        # Take first 5 companies for testing
        test_companies = companies[:5]
        
        print(f"\nTesting with CSE companies from our data...")
        print("=" * 50)
        
        results = []
        
        for company in test_companies:
            ticker = company['ticker']
            name = company['name']
            
            try:
                print(f"Testing {ticker} ({name})...")
                
                # Try with .MA suffix
                yf_ticker = f"{ticker}.MA"
                df = yf.download(
                    yf_ticker, 
                    period="7d", 
                    interval="1d",
                    progress=False
                )
                
                if df.empty:
                    print(f"❌ No data for {ticker}.MA")
                    results.append({
                        'ticker': ticker,
                        'name': name,
                        'yf_ticker': yf_ticker,
                        'success': False,
                        'error': 'No data found'
                    })
                else:
                    latest_price = df['Close'].iloc[-1]
                    print(f"✅ {ticker}.MA: {latest_price:.2f} MAD")
                    results.append({
                        'ticker': ticker,
                        'name': name,
                        'yf_ticker': yf_ticker,
                        'success': True,
                        'latest_price': float(latest_price),
                        'data_points': len(df)
                    })
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error with {ticker}: {e}")
                results.append({
                    'ticker': ticker,
                    'name': name,
                    'success': False,
                    'error': str(e)
                })
        
        # Save CSE test results
        cse_output_file = Path("test_cse_companies_results.json")
        with open(cse_output_file, 'w') as f:
            json.dump({
                'test_date': datetime.now().isoformat(),
                'results': results,
                'summary': {
                    'total': len(results),
                    'successful': sum(1 for r in results if r['success']),
                }
            }, f, indent=2)
        
        print(f"CSE test results saved to: {cse_output_file}")
        
        return results
        
    except Exception as e:
        print(f"Error loading CSE companies: {e}")
        return []

if __name__ == "__main__":
    print("🧪 Testing Trading Data Pipeline")
    print("=" * 50)
    
    # Test 1: Known Moroccan stocks
    test_yfinance_moroccan_stocks()
    
    # Test 2: CSE companies from our data
    test_with_cse_companies()
    
    print("\n✅ Testing complete!") 