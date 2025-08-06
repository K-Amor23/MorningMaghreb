
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd
import logging

class BaseScraper(ABC):
    """Base class for all scrapers with common interface"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """Fetch data and return as DataFrame"""
        pass
    
    @abstractmethod
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate fetched data"""
        pass
    
    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform data to standard format"""
        return data
    
    def save_data(self, data: pd.DataFrame, destination: str) -> bool:
        """Save data to destination"""
        try:
            data.to_csv(destination, index=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            return False
