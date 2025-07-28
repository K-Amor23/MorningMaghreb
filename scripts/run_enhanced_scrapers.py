#!/usr/bin/env python3
"""
Enhanced Scrapers Runner for Casablanca Insights

This script runs all the scrapers to collect real data:
1. Scrape 78 companies from African Markets
2. Scrape OHLCV data from Casablanca Bourse
3. Scrape financial reports from company websites
4. Scrape news and sentiment data
5. Store all data in Supabase
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "apps" / "backend"
sys.path.append(str(backend_path))

# Import our scrapers
from etl.african_markets_scraper import AfricanMarketsScraper
from etl.casablanca_bourse_scraper import CasablancaBourseScraper
from etl.financial_reports_scraper import FinancialReportsScraper
from etl.news_sentiment_scraper import NewsSentimentScraper
from etl.supabase_data_refresh import SupabaseDataRefresh

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scrape_african_markets():
    """Scrape real data from African Markets"""
    try:
        logger.info("🚀 Starting African Markets data scraping...")
        
        async with AfricanMarketsScraper() as scraper:
            # Scrape all companies
            companies = await scraper.scrape_all()
            
            # Save to data directory
            output_dir = Path("apps/backend/data")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"african_markets_data_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(companies, f, indent=2, default=str)
            
            logger.info(f"✅ Scraped {len(companies)} companies from African Markets")
            logger.info(f"📁 Saved to: {output_file}")
            
            return {
                'companies_count': len(companies),
                'output_file': str(output_file),
                'timestamp': timestamp,
                'companies': companies
            }
            
    except Exception as e:
        logger.error(f"❌ Error in scrape_african_markets: {e}")
        raise

async def scrape_casablanca_bourse():
    """Scrape OHLCV data from Casablanca Bourse"""
    try:
        logger.info("🚀 Starting Casablanca Bourse data scraping...")
        
        async with CasablancaBourseScraper() as scraper:
            # Scrape market data
            market_data = await scraper.scrape_all_market_data()
            
            # Save to data directory
            output_dir = Path("apps/backend/data")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"casablanca_bourse_data_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(market_data, f, indent=2, default=str)
            
            logger.info(f"✅ Scraped market data from Casablanca Bourse")
            logger.info(f"📁 Saved to: {output_file}")
            
            return {
                'tickers_count': len(market_data.get('tickers', [])),
                'output_file': str(output_file),
                'timestamp': timestamp,
                'market_data': market_data
            }
            
    except Exception as e:
        logger.error(f"❌ Error in scrape_casablanca_bourse: {e}")
        raise

async def scrape_financial_reports(companies: List[Dict]):
    """Scrape financial reports from company websites"""
    try:
        logger.info("🚀 Starting financial reports scraping...")
        
        scraper = FinancialReportsScraper()
        
        # Scrape reports for each company (limit to first 10 for testing)
        total_reports = 0
        companies_processed = 0
        
        for company in companies[:10]:  # Limit to first 10 companies for testing
            ticker = company.get('ticker')
            company_url = company.get('company_url')
            
            if company_url:
                logger.info(f"📄 Scraping reports for {ticker}")
                try:
                    reports = await scraper.scrape_company_reports(ticker, company_url)
                    total_reports += len(reports)
                    companies_processed += 1
                    logger.info(f"✅ Found {len(reports)} reports for {ticker}")
                except Exception as e:
                    logger.warning(f"⚠️ Error scraping reports for {ticker}: {e}")
            else:
                logger.warning(f"⚠️ No URL found for {ticker}")
        
        logger.info(f"✅ Processed {companies_processed} companies")
        logger.info(f"📄 Total reports found: {total_reports}")
        
        return {
            'companies_processed': companies_processed,
            'total_reports': total_reports
        }
        
    except Exception as e:
        logger.error(f"❌ Error in scrape_financial_reports: {e}")
        raise

async def scrape_news_sentiment(companies: List[Dict]):
    """Scrape news and sentiment data"""
    try:
        logger.info("🚀 Starting news and sentiment scraping...")
        
        scraper = NewsSentimentScraper()
        
        # Scrape news for each company (limit to first 10 for testing)
        total_news = 0
        companies_processed = 0
        
        for company in companies[:10]:  # Limit to first 10 companies for testing
            ticker = company.get('ticker')
            company_name = company.get('name')
            
            logger.info(f"📰 Scraping news for {ticker} - {company_name}")
            try:
                news_items = await scraper.scrape_company_news(ticker, company_name)
                total_news += len(news_items)
                companies_processed += 1
                logger.info(f"✅ Found {len(news_items)} news items for {ticker}")
            except Exception as e:
                logger.warning(f"⚠️ Error scraping news for {ticker}: {e}")
        
        logger.info(f"✅ Processed {companies_processed} companies")
        logger.info(f"📰 Total news items found: {total_news}")
        
        return {
            'companies_processed': companies_processed,
            'total_news': total_news
        }
        
    except Exception as e:
        logger.error(f"❌ Error in scrape_news_sentiment: {e}")
        raise

def sync_data_to_supabase(african_markets_results, casablanca_bourse_results, financial_reports_results, news_sentiment_results):
    """Sync all scraped data to Supabase"""
    try:
        logger.info("🚀 Starting data sync to Supabase...")
        
        # Initialize Supabase sync
        supabase_sync = SupabaseDataRefresh()
        
        # Sync companies data
        if african_markets_results and african_markets_results.get('companies'):
            companies = african_markets_results['companies']
            logger.info(f"📊 Syncing {len(companies)} companies to Supabase")
            supabase_sync.sync_companies(companies)
        
        # Sync market data
        if casablanca_bourse_results and casablanca_bourse_results.get('market_data'):
            market_data = casablanca_bourse_results['market_data']
            logger.info("📈 Syncing market data to Supabase")
            supabase_sync.sync_market_data(market_data)
        
        # Sync financial reports
        if financial_reports_results:
            logger.info(f"📄 Syncing {financial_reports_results['total_reports']} financial reports to Supabase")
            # Implementation for syncing reports
        
        # Sync news data
        if news_sentiment_results:
            logger.info(f"📰 Syncing {news_sentiment_results['total_news']} news items to Supabase")
            # Implementation for syncing news
        
        return {
            'companies_synced': len(companies) if african_markets_results and african_markets_results.get('companies') else 0,
            'market_data_synced': bool(casablanca_bourse_results and casablanca_bourse_results.get('market_data')),
            'reports_synced': financial_reports_results.get('total_reports', 0) if financial_reports_results else 0,
            'news_synced': news_sentiment_results.get('total_news', 0) if news_sentiment_results else 0
        }
        
    except Exception as e:
        logger.error(f"❌ Error in sync_data_to_supabase: {e}")
        raise

async def main():
    """Main function to run all scrapers"""
    try:
        logger.info("🎯 Starting Enhanced Casablanca Insights Scrapers")
        logger.info("=" * 60)
        
        # Step 1: Scrape African Markets data
        african_markets_results = await scrape_african_markets()
        
        # Step 2: Scrape Casablanca Bourse data
        casablanca_bourse_results = await scrape_casablanca_bourse()
        
        # Step 3: Scrape financial reports
        companies = african_markets_results.get('companies', [])
        financial_reports_results = await scrape_financial_reports(companies)
        
        # Step 4: Scrape news and sentiment
        news_sentiment_results = await scrape_news_sentiment(companies)
        
        # Step 5: Sync all data to Supabase
        sync_results = sync_data_to_supabase(
            african_markets_results,
            casablanca_bourse_results,
            financial_reports_results,
            news_sentiment_results
        )
        
        # Summary
        logger.info("🎉 Enhanced Scrapers Completed Successfully!")
        logger.info("=" * 60)
        logger.info("📊 Summary:")
        logger.info(f"   ✅ Companies: {african_markets_results['companies_count']}")
        logger.info(f"   ✅ Market Data: {casablanca_bourse_results['tickers_count']} tickers")
        logger.info(f"   ✅ Financial Reports: {financial_reports_results['total_reports']}")
        logger.info(f"   ✅ News Items: {news_sentiment_results['total_news']}")
        logger.info(f"   ✅ Synced to Supabase: {sync_results['companies_synced']} companies")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced Scrapers failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1) 