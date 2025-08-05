import hashlib
import hmac
import secrets
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from functools import wraps
import json

logger = logging.getLogger(__name__)

# Security configuration
SECURITY_CONFIG = {
    'rate_limit_window': 3600,  # 1 hour
    'max_requests_per_hour': 1000,
    'api_key_expiry_days': 365,
    'max_webhook_retries': 3,
    'webhook_timeout': 30,
    'allowed_origins': [
        'http://localhost:3000',
        'https://morningmaghreb.com',
        'https://www.morningmaghreb.com'
    ],
    'blocked_ips': [],
    'suspicious_patterns': [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'<iframe.*?>',
        r'<object.*?>',
        r'<embed.*?>'
    ]
}

class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        self.blocked_ips: set = set()
    
    def is_rate_limited(self, identifier: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is rate limited"""
        current_time = time.time()
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if current_time - req_time < window_seconds
            ]
        
        # Check if limit exceeded
        if identifier in self.requests and len(self.requests[identifier]) >= max_requests:
            return True
        
        # Add current request
        if identifier not in self.requests:
            self.requests[identifier] = []
        self.requests[identifier].append(current_time)
        
        return False
    
    def block_ip(self, ip: str, duration_minutes: int = 60):
        """Block an IP address temporarily"""
        self.blocked_ips.add(ip)
        # In production, use Redis with TTL for this
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips

class InputValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in value if ord(char) >= 32)
        
        # Check length
        if len(sanitized) > max_length:
            raise ValueError(f"Input too long. Maximum length: {max_length}")
        
        return sanitized.strip()
    
    @staticmethod
    def validate_ticker(ticker: str) -> str:
        """Validate stock ticker symbol"""
        if not ticker:
            raise ValueError("Ticker cannot be empty")
        
        # Remove any whitespace and convert to uppercase
        ticker = ticker.strip().upper()
        
        # Check format (alphanumeric, max 10 characters)
        if not re.match(r'^[A-Z0-9]{1,10}$', ticker):
            raise ValueError("Invalid ticker format. Must be 1-10 alphanumeric characters")
        
        return ticker
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email address"""
        if not email:
            raise ValueError("Email cannot be empty")
        
        email = email.strip().lower()
        
        # Basic email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        
        return email
    
    @staticmethod
    def validate_url(url: str) -> str:
        """Validate URL"""
        if not url:
            raise ValueError("URL cannot be empty")
        
        url = url.strip()
        
        # Basic URL validation
        if not re.match(r'^https?://[^\s/$.?#].[^\s]*$', url):
            raise ValueError("Invalid URL format")
        
        return url
    
    @staticmethod
    def validate_json_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize JSON payload"""
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")
        
        sanitized = {}
        for key, value in payload.items():
            # Sanitize key
            if not isinstance(key, str):
                raise ValueError("All keys must be strings")
            
            sanitized_key = InputValidator.sanitize_string(key, max_length=100)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized_value = InputValidator.sanitize_string(value)
            elif isinstance(value, (int, float)):
                sanitized_value = value
            elif isinstance(value, list):
                sanitized_value = [InputValidator.sanitize_string(str(v)) if isinstance(v, str) else v for v in value]
            elif isinstance(value, dict):
                sanitized_value = InputValidator.validate_json_payload(value)
            else:
                raise ValueError(f"Unsupported value type: {type(value)}")
            
            sanitized[sanitized_key] = sanitized_value
        
        return sanitized
    
    @staticmethod
    def check_suspicious_content(content: str) -> bool:
        """Check for suspicious content patterns"""
        content_lower = content.lower()
        
        for pattern in SECURITY_CONFIG['suspicious_patterns']:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True
        
        return False

class APIAuthManager:
    """API authentication and authorization manager"""
    
    def __init__(self):
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.rate_limiter = RateLimiter()
    
    def generate_api_key(self, user_id: str, permissions: List[str], 
                        rate_limit_per_hour: int = 1000) -> str:
        """Generate a new API key"""
        api_key = f"cas_sk_{secrets.token_urlsafe(32)}"
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        self.api_keys[api_key_hash] = {
            'user_id': user_id,
            'permissions': permissions,
            'rate_limit_per_hour': rate_limit_per_hour,
            'created_at': datetime.utcnow(),
            'last_used': None,
            'is_active': True
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return user info"""
        if not api_key:
            return None
        
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if api_key_hash not in self.api_keys:
            return None
        
        key_info = self.api_keys[api_key_hash]
        
        # Check if key is active
        if not key_info['is_active']:
            return None
        
        # Check if key has expired
        if 'expires_at' in key_info and key_info['expires_at'] < datetime.utcnow():
            return None
        
        # Update last used timestamp
        key_info['last_used'] = datetime.utcnow()
        
        return key_info
    
    def check_permission(self, key_info: Dict[str, Any], required_permission: str) -> bool:
        """Check if API key has required permission"""
        if not key_info:
            return False
        
        permissions = key_info.get('permissions', [])
        return required_permission in permissions or 'admin' in permissions
    
    def check_rate_limit(self, key_info: Dict[str, Any]) -> bool:
        """Check if API key is within rate limit"""
        if not key_info:
            return False
        
        identifier = f"api_key_{key_info['user_id']}"
        max_requests = key_info.get('rate_limit_per_hour', 1000)
        
        return not self.rate_limiter.is_rate_limited(
            identifier, max_requests, SECURITY_CONFIG['rate_limit_window']
        )

class WebhookSecurity:
    """Webhook security utilities"""
    
    @staticmethod
    def generate_webhook_secret() -> str:
        """Generate a webhook secret key"""
        return f"whsec_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def create_webhook_signature(payload: bytes, secret: str) -> str:
        """Create webhook signature"""
        return hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

# Global instances
auth_manager = APIAuthManager()
input_validator = InputValidator()

# Security decorators
def require_auth(required_permission: Optional[str] = None):
    """Decorator to require authentication"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would be implemented with FastAPI dependencies
            # For now, return the function as-is
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    """Decorator to apply rate limiting"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would be implemented with FastAPI dependencies
            # For now, return the function as-is
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_input(validation_rules: Dict[str, Any]):
    """Decorator to validate input parameters"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would validate inputs based on rules
            # For now, return the function as-is
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Security middleware functions
async def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.client.host if request.client else "unknown"

async def validate_request_origin(request: Request) -> bool:
    """Validate request origin"""
    origin = request.headers.get('Origin')
    if not origin:
        return True  # Allow requests without origin header
    
    return origin in SECURITY_CONFIG['allowed_origins']

async def check_request_security(request: Request) -> Dict[str, Any]:
    """Comprehensive security check for requests"""
    security_report = {
        'ip_address': await get_client_ip(request),
        'user_agent': request.headers.get('User-Agent', ''),
        'origin': request.headers.get('Origin', ''),
        'is_blocked': False,
        'warnings': []
    }
    
    # Check if IP is blocked
    if auth_manager.rate_limiter.is_ip_blocked(security_report['ip_address']):
        security_report['is_blocked'] = True
        security_report['warnings'].append('IP address is blocked')
    
    # Check for suspicious user agent
    user_agent = security_report['user_agent'].lower()
    suspicious_agents = ['bot', 'crawler', 'spider', 'scraper']
    if any(agent in user_agent for agent in suspicious_agents):
        security_report['warnings'].append('Suspicious user agent detected')
    
    # Check for suspicious patterns in URL
    url = str(request.url)
    if input_validator.check_suspicious_content(url):
        security_report['warnings'].append('Suspicious content in URL')
    
    return security_report

# Utility functions
def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security events"""
    logger.warning(f"Security event: {event_type} - {details}")

def sanitize_log_data(data: Any) -> Any:
    """Sanitize data for logging (remove sensitive information)"""
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if key.lower() in ['password', 'token', 'secret', 'key']:
                sanitized[key] = '***REDACTED***'
            else:
                sanitized[key] = sanitize_log_data(value)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_log_data(item) for item in data]
    else:
        return data 