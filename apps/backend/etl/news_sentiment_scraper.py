#!/usr/bin/env python3
"""
News and Sentiment Scraper

This scraper extracts news and performs sentiment analysis from:
1. Moroccan financial media
2. Company press releases
3. International financial news

Data Sources:
- Le Matin
- Medias24
- L'Economiste
- TelQuel Finance
- Company websites
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import re
import time
import urllib.parse
from textblob import TextBlob
import nltk

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsSentimentScraper:
    """Scraper for news and sentiment analysis"""
    
    def __init__(self):
        self.session = None
        self.output_dir = Path("apps/backend/data/news_sentiment")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Moroccan financial media sources
        self.media_sources = {
            'le_matin': {
                'name': 'Le Matin',
                'url': 'https://lematin.ma',
                'finance_url': 'https://lematin.ma/journal/economie',
                'search_url': 'https://lematin.ma/recherche'
            },
            'medias24': {
                'name': 'Medias24',
                'url': 'https://www.medias24.com',
                'finance_url': 'https://www.medias24.com/economie',
                'search_url': 'https://www.medias24.com/recherche'
            },
            'leconomiste': {
                'name': "L'Economiste",
                'url': 'https://www.leconomiste.com',
                'finance_url': 'https://www.leconomiste.com/economie',
                'search_url': 'https://www.leconomiste.com/recherche'
            },
            'telquel': {
                'name': 'TelQuel',
                'url': 'https://telquel.ma',
                'finance_url': 'https://telquel.ma/categorie/economie',
                'search_url': 'https://telquel.ma/recherche'
            }
        }
        
        # Company tickers to search for
        self.company_tickers = [
            'ATW', 'IAM', 'BCP', 'BMCE', 'CIH', 'WAA', 'CTM', 'MNG', 'MADESA', 'SOTHEMA',
            'Attijariwafa', 'Maroc Telecom', 'Banque Centrale Populaire', 'BMCE Bank',
            'CIH Bank', 'Wafa Assurance', 'Maroc Telecom', 'Managem', 'Madesa', 'Sothema'
        ]
        
        logger.info("News and Sentiment Scraper initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text using TextBlob"""
        try:
            # Clean text
            cleaned_text = re.sub(r'[^\w\s]', '', text)
            
            # Create TextBlob object
            blob = TextBlob(cleaned_text)
            
            # Get polarity (-1 to 1, where -1 is negative, 1 is positive)
            polarity = blob.sentiment.polarity
            
            # Get subjectivity (0 to 1, where 0 is objective, 1 is subjective)
            subjectivity = blob.sentiment.subjectivity
            
            # Determine sentiment category
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'sentiment': sentiment,
                'confidence': abs(polarity)  # Higher absolute polarity = higher confidence
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing sentiment: {e}")
            return {
                'polarity': 0.0,
                'subjectivity': 0.5,
                'sentiment': 'neutral',
                'confidence': 0.0
            }
    
    async def scrape_media_source(self, source_key: str, source_info: Dict) -> List[Dict]:
        """Scrape news from a specific media source"""
        try:
            logger.info(f"Scraping {source_info['name']}...")
            
            articles = []
            
            # Get finance section
            try:
                async with self.session.get(source_info['finance_url']) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Look for article links
                        article_links = soup.find_all('a', href=True)
                        
                        for link in article_links:
                            href = link.get('href')
                            text = link.get_text(strip=True)
                            
                            if href and text and len(text) > 20:  # Reasonable article title length
                                # Check if article mentions any company
                                mentioned_companies = []
                                for ticker in self.company_tickers:
                                    if ticker.lower() in text.lower():
                                        mentioned_companies.append(ticker)
                                
                                if mentioned_companies:
                                    # Get full URL
                                    full_url = urllib.parse.urljoin(source_info['url'], href)
                                    
                                    # Analyze sentiment
                                    sentiment = self.analyze_sentiment(text)
                                    
                                    article = {
                                        'title': text,
                                        'url': full_url,
                                        'source': source_info['name'],
                                        'source_key': source_key,
                                        'mentioned_companies': mentioned_companies,
                                        'sentiment': sentiment,
                                        'published_date': datetime.now().strftime('%Y-%m-%d'),
                                        'scraped_at': datetime.now().isoformat()
                                    }
                                    
                                    articles.append(article)
                        
                        logger.info(f"Found {len(articles)} relevant articles from {source_info['name']}")
                        
            except Exception as e:
                logger.warning(f"Error scraping {source_info['name']}: {e}")
            
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping media source {source_key}: {e}")
            return []
    
    async def scrape_company_press_releases(self, ticker: str) -> List[Dict]:
        """Scrape press releases from company websites"""
        try:
            logger.info(f"Scraping press releases for {ticker}...")
            
            # Company press release URLs
            company_press_urls = {
                'ATW': 'https://www.attijariwafabank.com/fr/actualites',
                'IAM': 'https://www.iam.ma/fr/actualites',
                'BCP': 'https://www.banquecentrale.ma/fr/actualites',
                'BMCE': 'https://www.bmcebank.ma/fr/actualites',
                'CIH': 'https://www.cihbank.ma/fr/actualites'
            }
            
            if ticker not in company_press_urls:
                return []
            
            url = company_press_urls[ticker]
            articles = []
            
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Look for press release links
                        links = soup.find_all('a', href=True)
                        
                        for link in links:
                            href = link.get('href')
                            text = link.get_text(strip=True)
                            
                            if href and text and len(text) > 10:
                                # Check if it's a press release
                                if any(keyword in text.lower() for keyword in ['communiqué', 'presse', 'actualité', 'news', 'release']):
                                    full_url = urllib.parse.urljoin(url, href)
                                    
                                    # Analyze sentiment
                                    sentiment = self.analyze_sentiment(text)
                                    
                                    article = {
                                        'title': text,
                                        'url': full_url,
                                        'source': f'{ticker} Press Release',
                                        'source_key': 'company_press',
                                        'mentioned_companies': [ticker],
                                        'sentiment': sentiment,
                                        'published_date': datetime.now().strftime('%Y-%m-%d'),
                                        'scraped_at': datetime.now().isoformat()
                                    }
                                    
                                    articles.append(article)
                        
                        logger.info(f"Found {len(articles)} press releases for {ticker}")
                        
            except Exception as e:
                logger.warning(f"Error scraping press releases for {ticker}: {e}")
            
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping company press releases for {ticker}: {e}")
            return []
    
    async def scrape_all_news(self) -> Dict:
        """Scrape news from all sources"""
        try:
            logger.info("Starting comprehensive news scraping...")
            
            all_articles = []
            
            # Scrape media sources
            logger.info("Scraping media sources...")
            for source_key, source_info in self.media_sources.items():
                try:
                    articles = await self.scrape_media_source(source_key, source_info)
                    all_articles.extend(articles)
                    await asyncio.sleep(2)  # Be respectful
                except Exception as e:
                    logger.error(f"Error scraping {source_key}: {e}")
                    continue
            
            # Scrape company press releases
            logger.info("Scraping company press releases...")
            for ticker in ['ATW', 'IAM', 'BCP', 'BMCE', 'CIH']:
                try:
                    press_releases = await self.scrape_company_press_releases(ticker)
                    all_articles.extend(press_releases)
                    await asyncio.sleep(1)  # Be respectful
                except Exception as e:
                    logger.error(f"Error scraping press releases for {ticker}: {e}")
                    continue
            
            # Save data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.output_dir / f"news_sentiment_{timestamp}.json"
            
            result = {
                'success': True,
                'data': all_articles,
                'count': len(all_articles),
                'timestamp': datetime.now().isoformat(),
                'output_file': str(output_file),
                'summary': {
                    'by_source': {},
                    'by_sentiment': {},
                    'by_company': {},
                    'sentiment_stats': {
                        'positive': 0,
                        'negative': 0,
                        'neutral': 0,
                        'avg_polarity': 0.0,
                        'avg_subjectivity': 0.0
                    }
                }
            }
            
            # Generate summary statistics
            total_polarity = 0.0
            total_subjectivity = 0.0
            
            for article in all_articles:
                # By source
                source = article['source']
                result['summary']['by_source'][source] = result['summary']['by_source'].get(source, 0) + 1
                
                # By sentiment
                sentiment = article['sentiment']['sentiment']
                result['summary']['by_sentiment'][sentiment] = result['summary']['by_sentiment'].get(sentiment, 0) + 1
                
                # By company
                for company in article['mentioned_companies']:
                    result['summary']['by_company'][company] = result['summary']['by_company'].get(company, 0) + 1
                
                # Sentiment statistics
                total_polarity += article['sentiment']['polarity']
                total_subjectivity += article['sentiment']['subjectivity']
            
            # Calculate averages
            if all_articles:
                result['summary']['sentiment_stats']['avg_polarity'] = round(total_polarity / len(all_articles), 3)
                result['summary']['sentiment_stats']['avg_subjectivity'] = round(total_subjectivity / len(all_articles), 3)
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully scraped {len(all_articles)} news articles")
            logger.info(f"Data saved to: {output_file}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive news scraping: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_sentiment_summary(self, articles: List[Dict]) -> Dict:
        """Generate sentiment summary for articles"""
        try:
            if not articles:
                return {
                    'total_articles': 0,
                    'sentiment_distribution': {},
                    'top_companies': [],
                    'avg_sentiment': 'neutral'
                }
            
            # Sentiment distribution
            sentiment_counts = {}
            company_mentions = {}
            
            for article in articles:
                sentiment = article['sentiment']['sentiment']
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                
                for company in article['mentioned_companies']:
                    company_mentions[company] = company_mentions.get(company, 0) + 1
            
            # Top mentioned companies
            top_companies = sorted(company_mentions.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Overall sentiment
            positive_count = sentiment_counts.get('positive', 0)
            negative_count = sentiment_counts.get('negative', 0)
            neutral_count = sentiment_counts.get('neutral', 0)
            
            if positive_count > negative_count:
                overall_sentiment = 'positive'
            elif negative_count > positive_count:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
            
            return {
                'total_articles': len(articles),
                'sentiment_distribution': sentiment_counts,
                'top_companies': top_companies,
                'avg_sentiment': overall_sentiment,
                'positive_ratio': round(positive_count / len(articles), 3) if articles else 0,
                'negative_ratio': round(negative_count / len(articles), 3) if articles else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating sentiment summary: {e}")
            return {}

async def main():
    """Main function to run the scraper"""
    print("🔄 Starting News and Sentiment Scraper")
    print("=" * 60)
    
    async with NewsSentimentScraper() as scraper:
        # Scrape all news
        result = await scraper.scrape_all_news()
        
        if result['success']:
            print(f"✅ Successfully scraped {result['count']} news articles")
            print(f"📁 Data saved to: {result['output_file']}")
            
            # Show summary
            print("\n📊 Scraping Summary:")
            print("-" * 40)
            
            print("By Source:")
            for source, count in result['summary']['by_source'].items():
                print(f"  {source}: {count} articles")
            
            print("\nBy Sentiment:")
            for sentiment, count in result['summary']['by_sentiment'].items():
                print(f"  {sentiment}: {count} articles")
            
            print("\nBy Company:")
            for company, count in sorted(result['summary']['by_company'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {company}: {count} mentions")
            
            print(f"\nSentiment Statistics:")
            stats = result['summary']['sentiment_stats']
            print(f"  Average Polarity: {stats['avg_polarity']}")
            print(f"  Average Subjectivity: {stats['avg_subjectivity']}")
            
            # Show sample articles
            if result['data']:
                print("\n📋 Sample Articles:")
                print("-" * 40)
                for i, article in enumerate(result['data'][:5]):
                    print(f"{i+1}. {article['title'][:60]}...")
                    print(f"   Source: {article['source']}")
                    print(f"   Sentiment: {article['sentiment']['sentiment']} ({article['sentiment']['polarity']})")
                    print(f"   Companies: {', '.join(article['mentioned_companies'])}")
        else:
            print(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
    
    print("\n✅ News and sentiment scraping completed")

if __name__ == "__main__":
    asyncio.run(main()) 