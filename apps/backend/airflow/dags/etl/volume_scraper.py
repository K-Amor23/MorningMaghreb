#!/usr/bin/env python3
"""
Volume Data Scraper for Casablanca Stock Exchange

This scraper fetches comprehensive volume data for all CSE stocks including:
- Daily volume
- Average volume
- Volume trends
- Volume analysis metrics
"""

import asyncio
import aiohttp
import ssl
import json
import csv
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
from bs4 import BeautifulSoup
import pandas as pd
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class VolumeData:
    """Data class for volume information"""
    ticker: str
    date: datetime
    volume: int
    average_volume: Optional[int] = None
    volume_change_percent: Optional[float] = None
    volume_ma_5: Optional[int] = None  # 5-day moving average
    volume_ma_20: Optional[int] = None  # 20-day moving average
    volume_ratio: Optional[float] = None  # Current volume / average volume
    high_volume_alert: bool = False  # Volume > 2x average
    source: str = "volume_scraper"
    scraped_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        if self.date:
            data['date'] = self.date.isoformat()
        if self.scraped_at:
            data['scraped_at'] = self.scraped_at.isoformat()
        return data

class VolumeScraper:
    """Comprehensive volume data scraper for CSE stocks"""
    
    def __init__(self):
        self.session = None
        self.base_url = "https://www.african-markets.com"
        
        # Multiple sources for volume data
        self.sources = {
            "african_markets": {
                "url": "https://www.african-markets.com/en/stock-markets/bvc/listed-companies",
                "name": "African Markets"
            },
            "wafabourse": {
                "url": "https://www.wafabourse.com/fr/marche/actions",
                "name": "Wafabourse"
            },
            "investing": {
                "url": "https://www.investing.com/equities/morocco",
                "name": "Investing.com"
            },
            "yahoo_finance": {
                "url": "https://finance.yahoo.com/quote/{ticker}.MA",
                "name": "Yahoo Finance"
            }
        }
        
    async def __aenter__(self):
        """Setup async HTTP session"""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=connector,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    def clean_volume_value(self, value: str) -> Optional[int]:
        """Clean and convert volume values"""
        if not value or value == '-':
            return None
        
        # Remove common volume suffixes and convert
        value = value.replace(',', '').replace(' ', '').upper()
        
        # Handle different volume formats (K, M, B)
        multipliers = {
            'K': 1000,
            'M': 1000000,
            'B': 1000000000
        }
        
        for suffix, multiplier in multipliers.items():
            if value.endswith(suffix):
                try:
                    return int(float(value[:-1]) * multiplier)
                except:
                    pass
        
        # Try direct conversion
        try:
            return int(float(value))
        except:
            return None
    
    async def scrape_african_markets_volume(self) -> List[VolumeData]:
        """Scrape volume data from African Markets"""
        volume_data = []
        
        try:
            url = self.sources["african_markets"]["url"]
            logger.info(f"🔍 Scraping volume data from: {url}")
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch African Markets: HTTP {response.status}")
                    return volume_data
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for volume data in tables
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    
                    if len(rows) < 2:
                        continue
                    
                    # Check if this table has volume data
                    header_row = rows[0]
                    headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
                    
                    if 'volume' in headers or 'vol' in headers:
                        volume_col_idx = None
                        ticker_col_idx = None
                        
                        # Find volume and ticker columns
                        for i, header in enumerate(headers):
                            if 'volume' in header or 'vol' in header:
                                volume_col_idx = i
                            elif 'ticker' in header or 'symbol' in header or 'code' in header:
                                ticker_col_idx = i
                        
                        if volume_col_idx is not None:
                            # Process data rows
                            for row in rows[1:]:
                                cells = row.find_all(['td', 'th'])
                                
                                if len(cells) > max(volume_col_idx, ticker_col_idx or 0):
                                    try:
                                        # Extract ticker
                                        ticker = ""
                                        if ticker_col_idx is not None:
                                            ticker_cell = cells[ticker_col_idx]
                                            ticker = ticker_cell.get_text(strip=True).upper()
                                        else:
                                            # Try to find ticker in first column
                                            first_cell = cells[0]
                                            ticker_match = re.search(r'([A-Z]{2,6})', first_cell.get_text(strip=True))
                                            if ticker_match:
                                                ticker = ticker_match.group(1)
                                        
                                        # Extract volume
                                        volume_cell = cells[volume_col_idx]
                                        volume_text = volume_cell.get_text(strip=True)
                                        volume = self.clean_volume_value(volume_text)
                                        
                                        if ticker and volume:
                                            volume_data.append(VolumeData(
                                                ticker=ticker,
                                                date=datetime.now(),
                                                volume=volume,
                                                source="African Markets",
                                                scraped_at=datetime.now()
                                            ))
                                            logger.info(f"✅ Found volume for {ticker}: {volume:,}")
                                    
                                    except Exception as e:
                                        logger.warning(f"Error processing volume row: {e}")
                                        continue
                
                logger.info(f"📊 Successfully scraped {len(volume_data)} volume records from African Markets")
                
        except Exception as e:
            logger.error(f"Error scraping African Markets volume: {e}")
        
        return volume_data
    
    async def scrape_wafabourse_volume(self) -> List[VolumeData]:
        """Scrape volume data from Wafabourse"""
        volume_data = []
        
        try:
            url = self.sources["wafabourse"]["url"]
            logger.info(f"🔍 Scraping volume data from: {url}")
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch Wafabourse: HTTP {response.status}")
                    return volume_data
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for volume data in JavaScript variables
                scripts = soup.find_all('script')
                
                for script in scripts:
                    if script.string:
                        # Look for volume data in JavaScript
                        volume_patterns = [
                            r'volume["\']?\s*[:=]\s*["\']?(\d+(?:,\d+)*)["\']?',
                            r'vol["\']?\s*[:=]\s*["\']?(\d+(?:,\d+)*)["\']?',
                            r'volume\s*:\s*(\d+(?:,\d+)*)',
                            r'vol\s*:\s*(\d+(?:,\d+)*)'
                        ]
                        
                        for pattern in volume_patterns:
                            matches = re.findall(pattern, script.string, re.IGNORECASE)
                            for match in matches:
                                try:
                                    volume = self.clean_volume_value(match)
                                    if volume:
                                        # Try to find ticker in the same script
                                        ticker_match = re.search(r'["\']([A-Z]{2,6})["\']', script.string)
                                        if ticker_match:
                                            ticker = ticker_match.group(1)
                                            volume_data.append(VolumeData(
                                                ticker=ticker,
                                                date=datetime.now(),
                                                volume=volume,
                                                source="Wafabourse",
                                                scraped_at=datetime.now()
                                            ))
                                            logger.info(f"✅ Found volume for {ticker}: {volume:,}")
                                except:
                                    pass
                
                logger.info(f"📊 Successfully scraped {len(volume_data)} volume records from Wafabourse")
                
        except Exception as e:
            logger.error(f"Error scraping Wafabourse volume: {e}")
        
        return volume_data
    
    async def scrape_investing_volume(self) -> List[VolumeData]:
        """Scrape volume data from Investing.com"""
        volume_data = []
        
        try:
            url = self.sources["investing"]["url"]
            logger.info(f"🔍 Scraping volume data from: {url}")
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch Investing.com: HTTP {response.status}")
                    return volume_data
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for volume data in tables
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        
                        if len(cells) >= 3:
                            try:
                                # Look for volume data
                                for i, cell in enumerate(cells):
                                    cell_text = cell.get_text(strip=True)
                                    
                                    # Check if this looks like volume data
                                    if re.match(r'[\d,]+[KMB]?', cell_text):
                                        volume = self.clean_volume_value(cell_text)
                                        
                                        if volume:
                                            # Try to find ticker in nearby cells
                                            ticker = ""
                                            for j in range(max(0, i-2), min(len(cells), i+3)):
                                                if j != i:
                                                    ticker_match = re.search(r'([A-Z]{2,6})', cells[j].get_text(strip=True))
                                                    if ticker_match:
                                                        ticker = ticker_match.group(1)
                                                        break
                                            
                                            if ticker:
                                                volume_data.append(VolumeData(
                                                    ticker=ticker,
                                                    date=datetime.now(),
                                                    volume=volume,
                                                    source="Investing.com",
                                                    scraped_at=datetime.now()
                                                ))
                                                logger.info(f"✅ Found volume for {ticker}: {volume:,}")
                                                break
                            
                            except Exception as e:
                                logger.warning(f"Error processing Investing.com row: {e}")
                                continue
                
                logger.info(f"📊 Successfully scraped {len(volume_data)} volume records from Investing.com")
                
        except Exception as e:
            logger.error(f"Error scraping Investing.com volume: {e}")
        
        return volume_data
    
    async def calculate_volume_metrics(self, volume_data: List[VolumeData]) -> List[VolumeData]:
        """Calculate additional volume metrics"""
        # Group by ticker
        ticker_groups = {}
        for data in volume_data:
            if data.ticker not in ticker_groups:
                ticker_groups[data.ticker] = []
            ticker_groups[data.ticker].append(data)
        
        enhanced_data = []
        
        for ticker, data_list in ticker_groups.items():
            if len(data_list) > 0:
                # Use the most recent data point
                latest_data = data_list[0]
                
                # Calculate average volume if we have multiple sources
                if len(data_list) > 1:
                    volumes = [d.volume for d in data_list if d.volume]
                    if volumes:
                        latest_data.average_volume = int(sum(volumes) / len(volumes))
                        
                        # Calculate volume ratio
                        if latest_data.average_volume:
                            latest_data.volume_ratio = latest_data.volume / latest_data.average_volume
                            latest_data.high_volume_alert = latest_data.volume_ratio > 2.0
                
                enhanced_data.append(latest_data)
        
        return enhanced_data
    
    async def scrape_all_volume_data(self) -> List[VolumeData]:
        """Scrape volume data from all sources"""
        all_volume_data = []
        
        # Scrape from all sources concurrently
        tasks = [
            self.scrape_african_markets_volume(),
            self.scrape_wafabourse_volume(),
            self.scrape_investing_volume()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        for result in results:
            if isinstance(result, list):
                all_volume_data.extend(result)
            else:
                logger.error(f"Error in volume scraping: {result}")
        
        # Calculate additional metrics
        enhanced_data = await self.calculate_volume_metrics(all_volume_data)
        
        logger.info(f"📊 Total volume records collected: {len(enhanced_data)}")
        return enhanced_data
    
    async def export_volume_data(self, volume_data: List[VolumeData], output_dir: Path):
        """Export volume data to files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert to dictionaries
        data_dicts = [data.to_dict() for data in volume_data]
        
        # Export to JSON
        json_file = output_dir / f"volume_data_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "source": "Volume Scraper",
                    "scraped_at": datetime.now().isoformat(),
                    "total_records": len(volume_data),
                    "sources": list(set(data.source for data in volume_data))
                },
                "data": data_dicts
            }, f, indent=2, ensure_ascii=False, default=str)
        
        # Export to CSV
        csv_file = output_dir / f"volume_data_{timestamp}.csv"
        if data_dicts:
            df = pd.DataFrame(data_dicts)
            df.to_csv(csv_file, index=False, encoding='utf-8')
        
        logger.info(f"📄 Exported volume data to {json_file} and {csv_file}")
        
        return json_file, csv_file

async def main():
    """Main function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Volume Data Scraper for Casablanca Stock Exchange")
    logger.info("=" * 70)
    
    output_dir = Path("data/volume")
    
    async with VolumeScraper() as scraper:
        volume_data = await scraper.scrape_all_volume_data()
        
        if not volume_data:
            logger.error("❌ No volume data found!")
            return
        
        logger.info(f"\n📊 VOLUME SCRAPING RESULTS:")
        logger.info(f"Total volume records: {len(volume_data)}")
        
        # Show breakdown by source
        sources = {}
        for data in volume_data:
            source = data.source
            sources[source] = sources.get(source, 0) + 1
        
        logger.info(f"\n📈 Volume data by source:")
        for source, count in sorted(sources.items()):
            logger.info(f"  - {source}: {count}")
        
        # Show high volume alerts
        high_volume = [data for data in volume_data if data.high_volume_alert]
        if high_volume:
            logger.info(f"\n🚨 High Volume Alerts ({len(high_volume)} stocks):")
            for data in high_volume:
                ratio = data.volume_ratio or 0
                logger.info(f"  - {data.ticker}: {data.volume:,} ({(ratio*100):.1f}% of avg)")
        
        # Export results
        await scraper.export_volume_data(volume_data, output_dir)
        
        logger.info(f"\n📋 Sample volume data (first 10):")
        for i, data in enumerate(volume_data[:10]):
            avg_vol = data.average_volume or "N/A"
            ratio = f"{(data.volume_ratio*100):.1f}%" if data.volume_ratio else "N/A"
            logger.info(f"  {i+1:2d}. {data.ticker:6s} - {data.volume:>10,} - Avg: {avg_vol:>10} - Ratio: {ratio:>6}")
        
        logger.info(f"\n🎉 Successfully scraped volume data for {len(volume_data)} stocks!")

if __name__ == "__main__":
    asyncio.run(main()) 