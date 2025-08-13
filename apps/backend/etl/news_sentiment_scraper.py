#!/usr/bin/env python3
"""
News Sentiment Scraper for Moroccan Companies

This script queries Google News RSS for a list of Moroccan companies and stores
headlines, publication date, link, and sentiment score in Postgres.

Features:
- Google News RSS integration
- Sentiment analysis (positive/negative/neutral)
- Batch processing for multiple companies
- Supabase integration
- Duplicate detection
- Error handling and retry logic
"""

import asyncio
import aiohttp
import json
import logging
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import xml.etree.ElementTree as ET
import re
import time
import urllib.parse
from textblob import TextBlob
import hashlib

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
except ImportError:
    print("⚠️  Supabase client not available, will save to JSON only")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_sentiment_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsSentimentScraper:
    """Scraper for news sentiment analysis"""
    
    def __init__(self, batch_size: int = 10, max_concurrent: int = 10):
        self.session = None
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.output_dir = Path("../data/news_sentiment")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load companies from African Markets data
        self.companies = self.load_companies()
        
        # Supabase client
        self.supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if self.supabase_url and self.supabase_service_key:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            self.service_client = create_client(self.supabase_url, self.supabase_service_key)
            logger.info("✅ Supabase client initialized")
        else:
            self.supabase = None
            self.service_client = None
            logger.warning("⚠️  Supabase credentials not found, will save to JSON only")
        
        # News sources to prioritize
        self.priority_sources = [
            'reuters.com', 'bloomberg.com', 'ft.com', 'wsj.com',
            'moroccoworldnews.com', 'moroccotoday.news', 'lematin.ma',
            'leconomiste.com', 'lnt.ma', '2m.ma', 'medias24.com',
            'challenge.ma', 'mapexpress.ma', 'h24info.ma', 'telquel.ma', 'hespress.com',
            'aujourdhui.ma', 'leseco.ma', 'boursenews.ma'
        ]
        # Languages/regions to try for Google News RSS
        self.gnews_locales = [
            {"hl": "en", "ceid": "MA:en", "gl": "MA"},
            {"hl": "fr", "ceid": "MA:fr", "gl": "MA"},
            {"hl": "ar", "ceid": "MA:ar", "gl": "MA"},
        ]
        
        logger.info(f"✅ News Sentiment Scraper initialized with {len(self.companies)} companies")
    
    def load_companies(self) -> List[Dict]:
        """Load companies from African Markets data"""
        try:
            companies_file = "../data/cse_companies_african_markets.json"
            
            if not os.path.exists(companies_file):
                logger.error(f"❌ Companies file not found: {companies_file}")
                return []
            
            with open(companies_file, 'r', encoding='utf-8') as f:
                companies_data = json.load(f)
            
            logger.info(f"✅ Loaded {len(companies_data)} companies from African Markets data")
            return companies_data
            
        except Exception as e:
            logger.error(f"❌ Error loading companies: {str(e)}")
            return []
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Normalize score to 0-1 range
            sentiment_score = (polarity + 1) / 2
            
            return sentiment, round(sentiment_score, 3)
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing sentiment: {str(e)}")
            return 'neutral', 0.5
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)]', '', text)
        
        return text.strip()
    
    def extract_source_from_url(self, url: str) -> str:
        """Extract source domain from URL"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
            
        except Exception:
            return "unknown"
    
    def is_priority_source(self, source: str) -> bool:
        """Check if source is in priority list"""
        return any(priority in source.lower() for priority in self.priority_sources)
    
    async def fetch_google_news_rss(self, company_name: str, ticker: str) -> List[Dict]:
        """Fetch news from Google News RSS for a company, trying multiple locales and query variants"""
        try:
            logger.info(f"🔍 Fetching news for {ticker} ({company_name})")

            # Build multiple query variants
            query_variants = [
                f"{company_name} {ticker} Maroc",
                f"{company_name} Maroc",
                f"{company_name} Casablanca",
                f"{ticker} Bourse",
                f"{company_name} actualités",
                f"{company_name} أخبار",
            ]

            all_items: List[Dict] = []
            for loc in self.gnews_locales:
                for q in query_variants:
                    encoded_query = urllib.parse.quote(q)
                    rss_url = (
                        f"https://news.google.com/rss/search?q={encoded_query}"
                        f"&hl={loc['hl']}&gl={loc['gl']}&ceid={loc['ceid']}"
                    )
                    try:
                        async with self.session.get(rss_url) as response:
                            if response.status != 200:
                                continue
                            content = await response.text()
                    except Exception:
                        continue

                    try:
                        root = ET.fromstring(content)
                        items = root.findall('.//item')
                        for item in items[:20]:
                            try:
                                title_elem = item.find('title')
                                link_elem = item.find('link')
                                pub_date_elem = item.find('pubDate')
                                source_elem = item.find('source')
                                if not all([title_elem, link_elem]):
                                    continue
                                title = self.clean_text(title_elem.text or "")
                                link = link_elem.text or ""
                                source = source_elem.text if source_elem is not None else self.extract_source_from_url(link)
                                pub_date = None
                                if pub_date_elem and pub_date_elem.text:
                                    date_str = pub_date_elem.text
                                    for fmt in ['%a, %d %b %Y %H:%M:%S %Z', '%a, %d %b %Y %H:%M:%S %z']:
                                        try:
                                            pub_date = datetime.strptime(date_str, fmt)
                                            break
                                        except ValueError:
                                            continue
                                if not pub_date:
                                    pub_date = datetime.now()
                                sentiment, sentiment_score = self.analyze_sentiment(title)
                                content_preview = title[:200] + "..." if len(title) > 200 else title
                                unique_id = hashlib.md5(f"{ticker}_{link}_{pub_date.isoformat()}".encode()).hexdigest()
                                news_item = {
                                    'id': unique_id,
                                    'ticker': ticker,
                                    'headline': title,
                                    'source': source,
                                    'url': link,
                                    'published_at': pub_date.isoformat(),
                                    'sentiment': sentiment,
                                    'sentiment_score': sentiment_score,
                                    'content_preview': content_preview,
                                    'is_priority_source': self.is_priority_source(source),
                                    'scraped_at': datetime.now().isoformat()
                                }
                                all_items.append(news_item)
                            except Exception as e:
                                logger.warning(f"⚠️  Error parsing news item for {ticker}: {str(e)}")
                                continue
                    except ET.ParseError:
                        continue

            logger.info(f"✅ Found {len(all_items)} news items for {ticker}")
            return all_items
                
        except Exception as e:
            logger.error(f"❌ Error fetching news for {ticker}: {str(e)}")
            return []
    
    async def process_company_batch(self, companies_batch: List[Dict]) -> List[Dict]:
        """Process a batch of companies"""
        tasks = []
        for company in companies_batch:
            task = self.fetch_google_news_rss(company['name'], company['ticker'])
            tasks.append(task)
        
        # Execute tasks with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def limited_task(task):
            async with semaphore:
                return await task
        
        limited_tasks = [limited_task(task) for task in tasks]
        results = await asyncio.gather(*limited_tasks, return_exceptions=True)
        
        # Flatten results and filter out exceptions
        all_news = []
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            else:
                logger.error(f"❌ Task failed: {str(result)}")
        
        return all_news
    
    async def insert_news_to_supabase(self, news_items: List[Dict]) -> bool:
        """Insert news items to Supabase"""
        if not self.service_client or not news_items:
            return False
        
        try:
            # Prepare data for insertion
            news_to_insert = []
            for item in news_items:
                news_to_insert.append({
                    'ticker': item['ticker'],
                    'headline': item['headline'],
                    'source': item['source'],
                    'url': item['url'],
                    'published_at': item['published_at'],
                    'sentiment': item['sentiment'],
                    'sentiment_score': item['sentiment_score'],
                    'content_preview': item['content_preview']
                })
            
            # Insert in batches
            batch_size = 50
            for i in range(0, len(news_to_insert), batch_size):
                batch = news_to_insert[i:i + batch_size]
                
                result = self.service_client.table('company_news').upsert(
                    batch,
                    on_conflict='ticker,url,published_at'
                ).execute()
                
                logger.info(f"✅ Inserted batch {i//batch_size + 1} ({len(batch)} items)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inserting news to Supabase: {str(e)}")
            return False
    
    def save_news_to_json(self, news_items: List[Dict], batch_num: int) -> str:
        """Save news items to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"news_sentiment_batch_{batch_num}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_items, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved {len(news_items)} news items to {filepath}")
        return str(filepath)
    
    async def run_batch_scraping(self) -> Dict:
        """Run the complete batch scraping process"""
        start_time = time.time()
        
        logger.info("🚀 Starting news sentiment scraping...")
        logger.info(f"📊 Processing {len(self.companies)} companies in batches of {self.batch_size}")
        
        all_news = []
        batch_results = []
        
        # Process companies in batches
        for i in range(0, len(self.companies), self.batch_size):
            batch_num = i // self.batch_size + 1
            batch = self.companies[i:i + self.batch_size]
            
            logger.info(f"\n📋 Processing batch {batch_num} ({len(batch)} companies)")
            
            # Process batch
            batch_news = await self.process_company_batch(batch)
            all_news.extend(batch_news)
            
            # Save batch results
            batch_file = self.save_news_to_json(batch_news, batch_num)
            
            # Insert to Supabase
            if self.service_client:
                await self.insert_news_to_supabase(batch_news)
            
            batch_results.append({
                'batch_num': batch_num,
                'companies': len(batch),
                'news_found': len(batch_news),
                'file': batch_file
            })
            
            # Small delay between batches
            await asyncio.sleep(2)
        
        # Calculate sentiment statistics
        sentiment_stats = {
            'positive': len([n for n in all_news if n['sentiment'] == 'positive']),
            'negative': len([n for n in all_news if n['sentiment'] == 'negative']),
            'neutral': len([n for n in all_news if n['sentiment'] == 'neutral']),
            'total': len(all_news)
        }
        
        # Save final results
        final_results = {
            'timestamp': datetime.now().isoformat(),
            'total_companies': len(self.companies),
            'total_news': len(all_news),
            'sentiment_stats': sentiment_stats,
            'batch_size': self.batch_size,
            'max_concurrent': self.max_concurrent,
            'batch_results': batch_results,
            'news_items': all_news
        }
        
        final_file = self.output_dir / f"news_sentiment_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(final_file, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False)
        
        elapsed_time = time.time() - start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ NEWS SENTIMENT SCRAPING COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"📊 Total companies processed: {len(self.companies)}")
        logger.info(f"📰 Total news items found: {len(all_news)}")
        logger.info(f"😊 Positive: {sentiment_stats['positive']}")
        logger.info(f"😞 Negative: {sentiment_stats['negative']}")
        logger.info(f"😐 Neutral: {sentiment_stats['neutral']}")
        logger.info(f"⏱️  Total time: {elapsed_time:.2f} seconds")
        logger.info(f"📁 Final results saved to: {final_file}")
        
        return final_results

async def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='News Sentiment Scraper')
    parser.add_argument('--batch-size', type=int, default=10, 
                       help='Number of companies to process in each batch (default: 10)')
    parser.add_argument('--max-concurrent', type=int, default=10,
                       help='Maximum concurrent requests (default: 10)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode - validate configuration without scraping')
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = NewsSentimentScraper(batch_size=args.batch_size, max_concurrent=args.max_concurrent)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - Validating configuration...")
        print(f"   Total companies: {len(scraper.companies)}")
        print(f"   Batch size: {args.batch_size}")
        print(f"   Max concurrent: {args.max_concurrent}")
        print(f"   Priority sources: {len(scraper.priority_sources)}")
        return
    
    async with scraper:
        results = await scraper.run_batch_scraping()
        
        # Print summary
        print("\n📋 SCRAPING SUMMARY:")
        print(f"   Companies processed: {results['total_companies']}")
        print(f"   News items found: {results['total_news']}")
        print(f"   Batches completed: {len(results['batch_results'])}")
        
        sentiment_stats = results['sentiment_stats']
        print(f"\n😊 Sentiment Distribution:")
        print(f"   Positive: {sentiment_stats['positive']} ({sentiment_stats['positive']/sentiment_stats['total']*100:.1f}%)")
        print(f"   Negative: {sentiment_stats['negative']} ({sentiment_stats['negative']/sentiment_stats['total']*100:.1f}%)")
        print(f"   Neutral: {sentiment_stats['neutral']} ({sentiment_stats['neutral']/sentiment_stats['total']*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main()) 