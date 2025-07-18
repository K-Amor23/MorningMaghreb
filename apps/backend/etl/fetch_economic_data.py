import asyncio
import logging
import requests
import pandas as pd
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, date
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
import io
import yaml
from bs4 import BeautifulSoup
import time
import random

from storage.local_fs import LocalFileStorage
from models.financials import ETLJob, JobType, JobStatus

logger = logging.getLogger(__name__)

class EconomicDataFetcher:
    """Fetches economic data from BAM (Bank Al-Maghrib) website"""
    
    def __init__(self, storage: LocalFileStorage):
        self.storage = storage
        self.base_url = "https://www.bkam.ma"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Configure SSL verification - set to False for development only
        self.session.verify = False
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Economic data sources configuration
        self.data_sources = {
            'key_policy_rate': {
                'url': 'https://www.bkam.ma/Marche-des-capitaux/Taux-et-cours/Taux-directeur',
                'frequency': 'monthly',
                'format': 'xls',
                'description': 'Key Policy Rate - 7-day rate decisions'
            },
            'foreign_exchange_reserves': {
                'url': 'https://www.bkam.ma/Marche-des-capitaux/Taux-et-cours/Reserves-de-change',
                'frequency': 'weekly',
                'format': 'xls',
                'description': 'Foreign Exchange Reserves in MAD and foreign currencies'
            },
            'inflation_cpi': {
                'url': 'https://www.bkam.ma/Statistiques/Statistiques-monetaires-et-financieres/Indices-des-prix',
                'frequency': 'monthly',
                'format': 'xls',
                'description': 'Inflation (CPI) data'
            },
            'money_supply': {
                'url': 'https://www.bkam.ma/Statistiques/Statistiques-monetaires-et-financieres/Aggregats-monetaires',
                'frequency': 'monthly',
                'format': 'xls',
                'description': 'Money Supply (M1/M2/M3)'
            },
            'balance_of_payments': {
                'url': 'https://www.bkam.ma/Statistiques/Statistiques-monetaires-et-financieres/Balance-des-paiements',
                'frequency': 'quarterly',
                'format': 'xls',
                'description': 'Balance of Payments - foreign trade and capital flows'
            },
            'credit_to_economy': {
                'url': 'https://www.bkam.ma/Statistiques/Statistiques-monetaires-et-financieres/Credit-a-leconomie',
                'frequency': 'monthly',
                'format': 'xls',
                'description': 'Credit to Economy - sectoral lending breakdown'
            }
        }
    
    async def fetch_all_economic_data(self, data_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch all economic data or specific data types"""
        if data_types is None:
            data_types = list(self.data_sources.keys())
        
        results = {
            "start_time": datetime.now(),
            "data_types_requested": data_types,
            "data_fetched": [],
            "errors": [],
            "total_files": 0
        }
        
        for data_type in data_types:
            if data_type not in self.data_sources:
                results["errors"].append(f"Unknown data type: {data_type}")
                continue
                
            try:
                logger.info(f"Fetching {data_type} data...")
                data_result = await self._fetch_single_data_type(data_type)
                results["data_fetched"].append(data_result)
                results["total_files"] += data_result.get("files_downloaded", 0)
                
            except Exception as e:
                error_msg = f"Error fetching {data_type}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        results["end_time"] = datetime.now()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()
        
        return results
    
    async def _fetch_single_data_type(self, data_type: str) -> Dict[str, Any]:
        """Fetch data for a single economic indicator"""
        source_config = self.data_sources[data_type]
        
        result = {
            "data_type": data_type,
            "source_url": source_config["url"],
            "files_downloaded": 0,
            "files_processed": 0,
            "data_points": 0,
            "latest_date": None,
            "errors": []
        }
        
        try:
            # Get the page content
            response = self.session.get(source_config["url"], timeout=30)
            response.raise_for_status()
            
            # Parse the page to find download links
            soup = BeautifulSoup(response.content, 'html.parser')
            download_links = self._extract_download_links(soup, source_config["format"])
            
            if not download_links:
                result["errors"].append("No download links found")
                return result
            
            # Download and process each file
            for link in download_links[:5]:  # Limit to latest 5 files
                try:
                    file_result = await self._download_and_process_file(
                        link, data_type, source_config
                    )
                    if file_result["success"]:
                        result["files_downloaded"] += 1
                        result["files_processed"] += 1
                        result["data_points"] += file_result["data_points"]
                        
                        # Update latest date
                        if file_result["date"]:
                            if not result["latest_date"] or file_result["date"] > result["latest_date"]:
                                result["latest_date"] = file_result["date"]
                    else:
                        result["errors"].append(f"Failed to process {link}: {file_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    result["errors"].append(f"Error processing {link}: {e}")
                
                # Add delay between requests
                await asyncio.sleep(random.uniform(1, 3))
            
        except Exception as e:
            result["errors"].append(f"Error fetching {data_type}: {e}")
        
        return result
    
    def _extract_download_links(self, soup: BeautifulSoup, file_format: str) -> List[str]:
        """Extract download links from the page"""
        links = []
        
        # Look for links with the specified format
        for link in soup.find_all('a', href=True):
            href = link['href']
            if file_format.lower() in href.lower():
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    full_url = urljoin(self.base_url, href)
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(self.base_url, href)
                
                links.append(full_url)
        
        # Also look for download buttons or specific patterns
        for link in soup.find_all('a', class_=re.compile(r'download|btn|link')):
            href = link.get('href')
            if href and file_format.lower() in href.lower():
                full_url = urljoin(self.base_url, href)
                if full_url not in links:
                    links.append(full_url)
        
        return links
    
    async def _download_and_process_file(self, url: str, data_type: str, 
                                       source_config: Dict[str, Any]) -> Dict[str, Any]:
        """Download and process a single file"""
        result = {
            "url": url,
            "success": False,
            "data_points": 0,
            "date": None,
            "error": None
        }
        
        try:
            # Download the file
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract filename from URL or headers
            filename = self._extract_filename(url, response.headers)
            
            # Save the raw file
            file_path = await self._save_raw_file(
                response.content, data_type, filename
            )
            
            # Parse the file based on format
            if source_config["format"] == "xls":
                parsed_data = await self._parse_excel_file(response.content, data_type)
            else:
                parsed_data = await self._parse_generic_file(response.content, data_type)
            
            if parsed_data:
                # Save parsed data
                parsed_file_path = await self._save_parsed_data(
                    parsed_data, data_type, filename
                )
                
                result["success"] = True
                result["data_points"] = len(parsed_data.get("data", []))
                result["date"] = parsed_data.get("latest_date")
                result["file_path"] = file_path
                result["parsed_file_path"] = parsed_file_path
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error downloading/processing {url}: {e}")
        
        return result
    
    def _extract_filename(self, url: str, headers: Dict[str, str]) -> str:
        """Extract filename from URL or headers"""
        # Try to get filename from Content-Disposition header
        content_disposition = headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            filename = re.search(r'filename="?([^"]+)"?', content_disposition)
            if filename:
                return filename.group(1)
        
        # Extract from URL
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        
        if not filename or '.' not in filename:
            # Generate filename based on current date
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"economic_data_{timestamp}.xls"
        
        return filename
    
    async def _save_raw_file(self, content: bytes, data_type: str, filename: str) -> str:
        """Save raw downloaded file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{data_type}_{timestamp}_{filename}"
        
        file_path = f"economic_data/raw/{safe_filename}"
        await self.storage.save_file(file_path, content)
        
        return file_path
    
    async def _parse_excel_file(self, content: bytes, data_type: str) -> Optional[Dict[str, Any]]:
        """Parse Excel file content"""
        try:
            # Read Excel file
            df = pd.read_excel(io.BytesIO(content), sheet_name=None)
            
            parsed_data = {
                "data_type": data_type,
                "source": "BAM",
                "parsed_at": datetime.now().isoformat(),
                "sheets": {},
                "data": [],
                "latest_date": None
            }
            
            # Process each sheet
            for sheet_name, sheet_df in df.items():
                sheet_data = self._process_excel_sheet(sheet_df, sheet_name, data_type)
                parsed_data["sheets"][sheet_name] = sheet_data
                
                # Extract data points
                if sheet_data.get("data_points"):
                    parsed_data["data"].extend(sheet_data["data_points"])
                
                # Update latest date
                if sheet_data.get("latest_date"):
                    if not parsed_data["latest_date"] or sheet_data["latest_date"] > parsed_data["latest_date"]:
                        parsed_data["latest_date"] = sheet_data["latest_date"]
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing Excel file for {data_type}: {e}")
            return None
    
    def _process_excel_sheet(self, df: pd.DataFrame, sheet_name: str, data_type: str) -> Dict[str, Any]:
        """Process a single Excel sheet"""
        sheet_data = {
            "sheet_name": sheet_name,
            "rows": len(df),
            "columns": len(df.columns),
            "data_points": [],
            "latest_date": None
        }
        
        try:
            # Clean the dataframe
            df_clean = self._clean_dataframe(df)
            
            # Extract data based on data type
            if data_type == "key_policy_rate":
                data_points = self._extract_policy_rate_data(df_clean)
            elif data_type == "foreign_exchange_reserves":
                data_points = self._extract_forex_reserves_data(df_clean)
            elif data_type == "inflation_cpi":
                data_points = self._extract_inflation_data(df_clean)
            elif data_type == "money_supply":
                data_points = self._extract_money_supply_data(df_clean)
            elif data_type == "balance_of_payments":
                data_points = self._extract_balance_payments_data(df_clean)
            elif data_type == "credit_to_economy":
                data_points = self._extract_credit_data(df_clean)
            else:
                data_points = self._extract_generic_data(df_clean)
            
            sheet_data["data_points"] = data_points
            
            # Find latest date
            if data_points:
                dates = [point.get("date") for point in data_points if point.get("date")]
                if dates:
                    sheet_data["latest_date"] = max(dates)
            
        except Exception as e:
            logger.error(f"Error processing sheet {sheet_name}: {e}")
        
        return sheet_data
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare dataframe for processing"""
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Convert numeric columns
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric, replacing common separators
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='ignore')
        
        return df
    
    def _extract_policy_rate_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract policy rate data"""
        data_points = []
        
        # Look for date and rate columns
        date_col = None
        rate_col = None
        
        for col in df.columns:
            col_str = str(col).lower()
            if any(word in col_str for word in ['date', 'periode', 'mois', 'annee']):
                date_col = col
            elif any(word in col_str for word in ['taux', 'rate', 'directeur', '7']):
                rate_col = col
        
        if date_col and rate_col:
            for _, row in df.iterrows():
                try:
                    date_val = pd.to_datetime(row[date_col], errors='coerce')
                    rate_val = pd.to_numeric(row[rate_col], errors='coerce')
                    
                    if pd.notna(date_val) and pd.notna(rate_val):
                        data_points.append({
                            "date": date_val.date(),
                            "rate": float(rate_val),
                            "unit": "percent",
                            "indicator": "key_policy_rate"
                        })
                except Exception as e:
                    continue
        
        return data_points
    
    def _extract_forex_reserves_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract foreign exchange reserves data"""
        data_points = []
        
        # Look for date and reserves columns
        date_col = None
        reserves_col = None
        
        for col in df.columns:
            col_str = str(col).lower()
            if any(word in col_str for word in ['date', 'periode', 'mois', 'annee']):
                date_col = col
            elif any(word in col_str for word in ['reserves', 'change', 'mad', 'devises']):
                reserves_col = col
        
        if date_col and reserves_col:
            for _, row in df.iterrows():
                try:
                    date_val = pd.to_datetime(row[date_col], errors='coerce')
                    reserves_val = pd.to_numeric(row[reserves_col], errors='coerce')
                    
                    if pd.notna(date_val) and pd.notna(reserves_val):
                        data_points.append({
                            "date": date_val.date(),
                            "reserves": float(reserves_val),
                            "unit": "MAD",
                            "indicator": "foreign_exchange_reserves"
                        })
                except Exception as e:
                    continue
        
        return data_points
    
    def _extract_inflation_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract inflation (CPI) data"""
        data_points = []
        
        # Look for date and CPI columns
        date_col = None
        cpi_col = None
        
        for col in df.columns:
            col_str = str(col).lower()
            if any(word in col_str for word in ['date', 'periode', 'mois', 'annee']):
                date_col = col
            elif any(word in col_str for word in ['cpi', 'inflation', 'indice', 'prix']):
                cpi_col = col
        
        if date_col and cpi_col:
            for _, row in df.iterrows():
                try:
                    date_val = pd.to_datetime(row[date_col], errors='coerce')
                    cpi_val = pd.to_numeric(row[cpi_col], errors='coerce')
                    
                    if pd.notna(date_val) and pd.notna(cpi_val):
                        data_points.append({
                            "date": date_val.date(),
                            "cpi": float(cpi_val),
                            "unit": "index",
                            "indicator": "inflation_cpi"
                        })
                except Exception as e:
                    continue
        
        return data_points
    
    def _extract_money_supply_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract money supply data (M1, M2, M3)"""
        data_points = []
        
        # Look for date and money supply columns
        date_col = None
        m1_col = None
        m2_col = None
        m3_col = None
        
        for col in df.columns:
            col_str = str(col).lower()
            if any(word in col_str for word in ['date', 'periode', 'mois', 'annee']):
                date_col = col
            elif 'm1' in col_str:
                m1_col = col
            elif 'm2' in col_str:
                m2_col = col
            elif 'm3' in col_str:
                m3_col = col
        
        if date_col:
            for _, row in df.iterrows():
                try:
                    date_val = pd.to_datetime(row[date_col], errors='coerce')
                    
                    if pd.notna(date_val):
                        data_point = {"date": date_val.date(), "indicator": "money_supply"}
                        
                        if m1_col and pd.notna(row[m1_col]):
                            data_point["m1"] = float(row[m1_col])
                        if m2_col and pd.notna(row[m2_col]):
                            data_point["m2"] = float(row[m2_col])
                        if m3_col and pd.notna(row[m3_col]):
                            data_point["m3"] = float(row[m3_col])
                        
                        data_point["unit"] = "MAD"
                        data_points.append(data_point)
                except Exception as e:
                    continue
        
        return data_points
    
    def _extract_balance_payments_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract balance of payments data"""
        data_points = []
        
        # Look for date and balance columns
        date_col = None
        balance_col = None
        
        for col in df.columns:
            col_str = str(col).lower()
            if any(word in col_str for word in ['date', 'periode', 'trimestre', 'annee']):
                date_col = col
            elif any(word in col_str for word in ['balance', 'paiements', 'compte', 'courant']):
                balance_col = col
        
        if date_col and balance_col:
            for _, row in df.iterrows():
                try:
                    date_val = pd.to_datetime(row[date_col], errors='coerce')
                    balance_val = pd.to_numeric(row[balance_col], errors='coerce')
                    
                    if pd.notna(date_val) and pd.notna(balance_val):
                        data_points.append({
                            "date": date_val.date(),
                            "balance": float(balance_val),
                            "unit": "MAD",
                            "indicator": "balance_of_payments"
                        })
                except Exception as e:
                    continue
        
        return data_points
    
    def _extract_credit_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract credit to economy data"""
        data_points = []
        
        # Look for date and credit columns
        date_col = None
        credit_col = None
        
        for col in df.columns:
            col_str = str(col).lower()
            if any(word in col_str for word in ['date', 'periode', 'mois', 'annee']):
                date_col = col
            elif any(word in col_str for word in ['credit', 'economie', 'pret', 'financement']):
                credit_col = col
        
        if date_col and credit_col:
            for _, row in df.iterrows():
                try:
                    date_val = pd.to_datetime(row[date_col], errors='coerce')
                    credit_val = pd.to_numeric(row[credit_col], errors='coerce')
                    
                    if pd.notna(date_val) and pd.notna(credit_val):
                        data_points.append({
                            "date": date_val.date(),
                            "credit": float(credit_val),
                            "unit": "MAD",
                            "indicator": "credit_to_economy"
                        })
                except Exception as e:
                    continue
        
        return data_points
    
    def _extract_generic_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract generic data when specific parser is not available"""
        data_points = []
        
        # Try to find date column
        date_col = None
        for col in df.columns:
            col_str = str(col).lower()
            if any(word in col_str for word in ['date', 'periode', 'mois', 'annee', 'trimestre']):
                date_col = col
                break
        
        if date_col:
            for _, row in df.iterrows():
                try:
                    date_val = pd.to_datetime(row[date_col], errors='coerce')
                    
                    if pd.notna(date_val):
                        data_point = {"date": date_val.date()}
                        
                        # Add all numeric columns as values
                        for col in df.columns:
                            if col != date_col:
                                val = pd.to_numeric(row[col], errors='coerce')
                                if pd.notna(val):
                                    data_point[str(col)] = float(val)
                        
                        data_points.append(data_point)
                except Exception as e:
                    continue
        
        return data_points
    
    async def _parse_generic_file(self, content: bytes, data_type: str) -> Optional[Dict[str, Any]]:
        """Parse generic file formats (PDF, etc.)"""
        # For now, return basic structure
        # In the future, this could use PDF parsing libraries
        return {
            "data_type": data_type,
            "source": "BAM",
            "parsed_at": datetime.now().isoformat(),
            "data": [],
            "latest_date": None,
            "note": "Generic file parsing not implemented yet"
        }
    
    async def _save_parsed_data(self, data: Dict[str, Any], data_type: str, 
                              original_filename: str) -> str:
        """Save parsed data as JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}_parsed.json"
        
        file_path = f"economic_data/parsed/{filename}"
        
        # Convert dates to strings for JSON serialization
        json_data = self._prepare_for_json(data)
        
        await self.storage.save_json(file_path, json_data)
        
        return file_path
    
    def _prepare_for_json(self, data: Any) -> Any:
        """Prepare data for JSON serialization"""
        if isinstance(data, dict):
            return {k: self._prepare_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._prepare_for_json(item) for item in data]
        elif isinstance(data, (datetime, date)):
            return data.isoformat()
        else:
            return data
    
    async def get_latest_data(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Get the latest data for a specific economic indicator"""
        try:
            # This would typically query the database for the latest records
            # For now, return a placeholder
            return {
                "data_type": data_type,
                "latest_date": None,
                "value": None,
                "unit": None
            }
        except Exception as e:
            logger.error(f"Error getting latest data for {data_type}: {e}")
            return None
    
    async def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of all available economic data"""
        summary = {
            "total_indicators": len(self.data_sources),
            "indicators": {},
            "last_updated": datetime.now().isoformat()
        }
        
        for data_type, config in self.data_sources.items():
            summary["indicators"][data_type] = {
                "description": config["description"],
                "frequency": config["frequency"],
                "format": config["format"],
                "url": config["url"]
            }
        
        return summary


async def main():
    """Test the economic data fetcher"""
    storage = LocalFileStorage()
    fetcher = EconomicDataFetcher(storage)
    
    # Test fetching key policy rate data
    results = await fetcher.fetch_all_economic_data(['key_policy_rate'])
    
    print("Economic Data Fetch Results:")
    print(f"Total files: {results['total_files']}")
    print(f"Errors: {len(results['errors'])}")
    
    for data_result in results['data_fetched']:
        print(f"\n{data_result['data_type']}:")
        print(f"  Files downloaded: {data_result['files_downloaded']}")
        print(f"  Data points: {data_result['data_points']}")
        print(f"  Latest date: {data_result['latest_date']}")


if __name__ == "__main__":
    asyncio.run(main()) 