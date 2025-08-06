
import os
from typing import Dict, Any, Optional
from pathlib import Path
import json

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or environment"""
    
    config = {}
    
    # Load from file if provided
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config.update(json.load(f))
    
    # Load from environment variables
    env_config = {
        "SUPABASE_URL": os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "SENDGRID_API_KEY": os.getenv("SENDGRID_API_KEY"),
        "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY")
    }
    
    config.update({k: v for k, v in env_config.items() if v})
    
    return config

def get_scraper_config(scraper_name: str) -> Dict[str, Any]:
    """Get configuration for specific scraper"""
    
    config = load_config()
    
    # Scraper-specific configurations
    scraper_configs = {
        "financial_reports": {
            "base_url": "https://www.casablanca-bourse.com",
            "delay": 2.0,
            "max_retries": 3
        },
        "news_sentiment": {
            "base_url": "https://api.newsapi.org",
            "delay": 1.0,
            "max_retries": 5
        },
        "market_data": {
            "base_url": "https://api.marketdata.com",
            "delay": 0.5,
            "max_retries": 3
        }
    }
    
    return {**config, **scraper_configs.get(scraper_name, {})}
