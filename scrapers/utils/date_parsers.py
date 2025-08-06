
from datetime import datetime, date
from typing import Union, Optional
import re

def parse_date(
    date_str: str,
    formats: Optional[list] = None,
    default: Optional[date] = None
) -> Optional[date]:
    """Parse date string with multiple format support"""
    
    if formats is None:
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%d-%m-%Y",
            "%m-%d-%Y"
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    return default

def extract_date_from_text(text: str) -> Optional[date]:
    """Extract date from text using regex patterns"""
    
    patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{2}-\d{2}-\d{4}\b"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return parse_date(match.group())
    
    return None
