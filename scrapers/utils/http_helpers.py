
import requests
import time
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
    retries: int = 3
) -> requests.Response:
    """Make HTTP request with retry logic"""
    
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Add default headers
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    response = session.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        data=data,
        timeout=timeout
    )
    
    response.raise_for_status()
    return response

def add_delay(seconds: float = 1.0):
    """Add delay between requests"""
    time.sleep(seconds)
