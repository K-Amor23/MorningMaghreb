#!/usr/bin/env python3
"""
Enhanced Notification Service with Web Push API

Features:
- Browser push notifications (Web Push API)
- Granular user preferences
- Integration with existing alert system
- Multiple notification channels
- Notification history tracking
- Performance monitoring
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import requests
from pywebpush import webpush, WebPushException

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
except ImportError:
    print("⚠️  Supabase client not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notification_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    PRICE_ALERT = "price_alert"
    PORTFOLIO_UPDATE = "portfolio_update"
    MARKET_UPDATE = "market_update"
    NEWS_ALERT = "news_alert"
    SYSTEM_ALERT = "system_alert"
    BACKTEST_COMPLETE = "backtest_complete"
    RISK_ALERT = "risk_alert"

class NotificationChannel(Enum):
    WEB_PUSH = "web_push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"

class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class NotificationPreferences:
    user_id: str
    web_push_enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    in_app_enabled: bool = True
    price_alerts: bool = True
    portfolio_updates: bool = True
    market_updates: bool = True
    news_alerts: bool = False
    system_alerts: bool = True
    backtest_notifications: bool = True
    risk_alerts: bool = True
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    timezone: str = "UTC"

@dataclass
class NotificationPayload:
    title: str
    body: str
    icon: Optional[str] = None
    badge: Optional[str] = None
    image: Optional[str] = None
    tag: Optional[str] = None
    data: Optional[Dict] = None
    actions: Optional[List[Dict]] = None
    require_interaction: bool = False
    silent: bool = False
    timestamp: Optional[datetime] = None

class NotificationService:
    """Enhanced notification service with Web Push API support"""
    
    def __init__(self):
        # Supabase client
        self.supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if self.supabase_url and self.supabase_service_key:
            self.supabase = create_client(self.supabase_url, self.supabase_service_key)
            logger.info("✅ Supabase client initialized")
        else:
            self.supabase = None
            logger.warning("⚠️  Supabase credentials not found")
        
        # VAPID keys for Web Push API
        self.vapid_public_key = os.getenv('VAPID_PUBLIC_KEY')
        self.vapid_private_key = os.getenv('VAPID_PRIVATE_KEY')
        self.vapid_email = os.getenv('VAPID_EMAIL', 'notifications@casablancainsights.com')
        
        # Email service configuration
        self.email_service_url = os.getenv('EMAIL_SERVICE_URL')
        self.email_api_key = os.getenv('EMAIL_API_KEY')
        
        # SMS service configuration
        self.sms_service_url = os.getenv('SMS_SERVICE_URL')
        self.sms_api_key = os.getenv('SMS_API_KEY')
        
        logger.info("✅ Notification Service initialized")
    
    def get_user_preferences(self, user_id: str) -> Optional[NotificationPreferences]:
        """Get user notification preferences"""
        try:
            if self.supabase:
                response = self.supabase.table('user_notification_preferences').select('*').eq('user_id', user_id).execute()
                if response.data:
                    data = response.data[0]
                    return NotificationPreferences(
                        user_id=data['user_id'],
                        web_push_enabled=data.get('web_push_enabled', True),
                        email_enabled=data.get('email_enabled', True),
                        sms_enabled=data.get('sms_enabled', False),
                        in_app_enabled=data.get('in_app_enabled', True),
                        price_alerts=data.get('price_alerts', True),
                        portfolio_updates=data.get('portfolio_updates', True),
                        market_updates=data.get('market_updates', True),
                        news_alerts=data.get('news_alerts', False),
                        system_alerts=data.get('system_alerts', True),
                        backtest_notifications=data.get('backtest_notifications', True),
                        risk_alerts=data.get('risk_alerts', True),
                        quiet_hours_start=data.get('quiet_hours_start', '22:00'),
                        quiet_hours_end=data.get('quiet_hours_end', '08:00'),
                        timezone=data.get('timezone', 'UTC')
                    )
            
            # Return default preferences if not found
            return NotificationPreferences(user_id=user_id)
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return NotificationPreferences(user_id=user_id)
    
    def update_user_preferences(self, user_id: str, preferences: NotificationPreferences) -> bool:
        """Update user notification preferences"""
        try:
            if self.supabase:
                data = {
                    'user_id': user_id,
                    'web_push_enabled': preferences.web_push_enabled,
                    'email_enabled': preferences.email_enabled,
                    'sms_enabled': preferences.sms_enabled,
                    'in_app_enabled': preferences.in_app_enabled,
                    'price_alerts': preferences.price_alerts,
                    'portfolio_updates': preferences.portfolio_updates,
                    'market_updates': preferences.market_updates,
                    'news_alerts': preferences.news_alerts,
                    'system_alerts': preferences.system_alerts,
                    'backtest_notifications': preferences.backtest_notifications,
                    'risk_alerts': preferences.risk_alerts,
                    'quiet_hours_start': preferences.quiet_hours_start,
                    'quiet_hours_end': preferences.quiet_hours_end,
                    'timezone': preferences.timezone,
                    'updated_at': datetime.now().isoformat()
                }
                
                # Upsert preferences
                self.supabase.table('user_notification_preferences').upsert(data).execute()
                return True
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    def get_user_subscriptions(self, user_id: str) -> List[Dict]:
        """Get user's push notification subscriptions"""
        try:
            if self.supabase:
                response = self.supabase.table('push_subscriptions').select('*').eq('user_id', user_id).execute()
                return response.data
            return []
        except Exception as e:
            logger.error(f"Error getting user subscriptions: {e}")
            return []
    
    def add_push_subscription(self, user_id: str, subscription: Dict) -> bool:
        """Add a new push subscription for a user"""
        try:
            if self.supabase:
                data = {
                    'user_id': user_id,
                    'endpoint': subscription['endpoint'],
                    'p256dh': subscription['keys']['p256dh'],
                    'auth': subscription['keys']['auth'],
                    'created_at': datetime.now().isoformat()
                }
                
                self.supabase.table('push_subscriptions').insert(data).execute()
                return True
        except Exception as e:
            logger.error(f"Error adding push subscription: {e}")
            return False
    
    def remove_push_subscription(self, user_id: str, endpoint: str) -> bool:
        """Remove a push subscription"""
        try:
            if self.supabase:
                self.supabase.table('push_subscriptions').delete().eq('user_id', user_id).eq('endpoint', endpoint).execute()
                return True
        except Exception as e:
            logger.error(f"Error removing push subscription: {e}")
            return False
    
    def is_quiet_hours(self, user_id: str) -> bool:
        """Check if current time is within user's quiet hours"""
        try:
            preferences = self.get_user_preferences(user_id)
            if not preferences:
                return False
            
            now = datetime.now()
            current_time = now.strftime('%H:%M')
            
            # Simple time comparison (in production, use proper timezone handling)
            return preferences.quiet_hours_start <= current_time <= preferences.quiet_hours_end
        except Exception as e:
            logger.error(f"Error checking quiet hours: {e}")
            return False
    
    def should_send_notification(self, user_id: str, notification_type: NotificationType) -> bool:
        """Check if notification should be sent based on user preferences"""
        try:
            preferences = self.get_user_preferences(user_id)
            if not preferences:
                return True  # Default to sending if no preferences found
            
            # Check if in quiet hours
            if self.is_quiet_hours(user_id):
                return False
            
            # Check type-specific preferences
            if notification_type == NotificationType.PRICE_ALERT and not preferences.price_alerts:
                return False
            elif notification_type == NotificationType.PORTFOLIO_UPDATE and not preferences.portfolio_updates:
                return False
            elif notification_type == NotificationType.MARKET_UPDATE and not preferences.market_updates:
                return False
            elif notification_type == NotificationType.NEWS_ALERT and not preferences.news_alerts:
                return False
            elif notification_type == NotificationType.SYSTEM_ALERT and not preferences.system_alerts:
                return False
            elif notification_type == NotificationType.BACKTEST_COMPLETE and not preferences.backtest_notifications:
                return False
            elif notification_type == NotificationType.RISK_ALERT and not preferences.risk_alerts:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking notification preferences: {e}")
            return True
    
    async def send_web_push_notification(self, user_id: str, payload: NotificationPayload) -> bool:
        """Send web push notification to user"""
        try:
            if not self.vapid_private_key:
                logger.warning("VAPID private key not configured")
                return False
            
            subscriptions = self.get_user_subscriptions(user_id)
            if not subscriptions:
                logger.info(f"No push subscriptions found for user {user_id}")
                return False
            
            success_count = 0
            for subscription in subscriptions:
                try:
                    push_data = {
                        'title': payload.title,
                        'body': payload.body,
                        'icon': payload.icon or '/icon-192x192.png',
                        'badge': payload.badge or '/badge-72x72.png',
                        'image': payload.image,
                        'tag': payload.tag,
                        'data': payload.data or {},
                        'actions': payload.actions or [],
                        'require_interaction': payload.require_interaction,
                        'silent': payload.silent,
                        'timestamp': payload.timestamp.isoformat() if payload.timestamp else datetime.now().isoformat()
                    }
                    
                    webpush(
                        subscription_info={
                            'endpoint': subscription['endpoint'],
                            'keys': {
                                'p256dh': subscription['p256dh'],
                                'auth': subscription['auth']
                            }
                        },
                        data=json.dumps(push_data),
                        vapid_private_key=self.vapid_private_key,
                        vapid_claims={
                            'sub': f'mailto:{self.vapid_email}'
                        }
                    )
                    success_count += 1
                    
                except WebPushException as e:
                    logger.error(f"Web push failed for subscription {subscription['endpoint']}: {e}")
                    # Remove invalid subscription
                    if e.response and e.response.status_code == 410:
                        self.remove_push_subscription(user_id, subscription['endpoint'])
                
                except Exception as e:
                    logger.error(f"Error sending web push notification: {e}")
            
            return success_count > 0
        except Exception as e:
            logger.error(f"Error in send_web_push_notification: {e}")
            return False
    
    async def send_email_notification(self, user_id: str, payload: NotificationPayload) -> bool:
        """Send email notification to user"""
        try:
            if not self.email_service_url or not self.email_api_key:
                logger.warning("Email service not configured")
                return False
            
            # Get user email from database
            user_email = self.get_user_email(user_id)
            if not user_email:
                logger.warning(f"No email found for user {user_id}")
                return False
            
            email_data = {
                'to': user_email,
                'subject': payload.title,
                'body': payload.body,
                'html_body': self.format_email_html(payload),
                'api_key': self.email_api_key
            }
            
            response = requests.post(self.email_service_url, json=email_data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    async def send_sms_notification(self, user_id: str, payload: NotificationPayload) -> bool:
        """Send SMS notification to user"""
        try:
            if not self.sms_service_url or not self.sms_api_key:
                logger.warning("SMS service not configured")
                return False
            
            # Get user phone from database
            user_phone = self.get_user_phone(user_id)
            if not user_phone:
                logger.warning(f"No phone found for user {user_id}")
                return False
            
            sms_data = {
                'to': user_phone,
                'message': f"{payload.title}: {payload.body}",
                'api_key': self.sms_api_key
            }
            
            response = requests.post(self.sms_service_url, json=sms_data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
            return False
    
    async def send_in_app_notification(self, user_id: str, payload: NotificationPayload) -> bool:
        """Send in-app notification"""
        try:
            if self.supabase:
                notification_data = {
                    'user_id': user_id,
                    'title': payload.title,
                    'body': payload.body,
                    'type': 'in_app',
                    'data': payload.data or {},
                    'read': False,
                    'created_at': datetime.now().isoformat()
                }
                
                self.supabase.table('notifications').insert(notification_data).execute()
                return True
        except Exception as e:
            logger.error(f"Error sending in-app notification: {e}")
            return False
    
    async def send_notification(
        self, 
        user_id: str, 
        notification_type: NotificationType,
        payload: NotificationPayload,
        channels: List[NotificationChannel] = None
    ) -> Dict[str, bool]:
        """Send notification through multiple channels"""
        try:
            # Check if notification should be sent
            if not self.should_send_notification(user_id, notification_type):
                logger.info(f"Notification blocked for user {user_id} (preferences/quiet hours)")
                return {'sent': False, 'reason': 'blocked_by_preferences'}
            
            # Get user preferences
            preferences = self.get_user_preferences(user_id)
            if not preferences:
                logger.warning(f"No preferences found for user {user_id}")
                return {'sent': False, 'reason': 'no_preferences'}
            
            # Determine channels to use
            if channels is None:
                channels = []
                if preferences.web_push_enabled:
                    channels.append(NotificationChannel.WEB_PUSH)
                if preferences.email_enabled:
                    channels.append(NotificationChannel.EMAIL)
                if preferences.sms_enabled:
                    channels.append(NotificationChannel.SMS)
                if preferences.in_app_enabled:
                    channels.append(NotificationChannel.IN_APP)
            
            results = {}
            
            # Send through each channel
            for channel in channels:
                if channel == NotificationChannel.WEB_PUSH and preferences.web_push_enabled:
                    results['web_push'] = await self.send_web_push_notification(user_id, payload)
                elif channel == NotificationChannel.EMAIL and preferences.email_enabled:
                    results['email'] = await self.send_email_notification(user_id, payload)
                elif channel == NotificationChannel.SMS and preferences.sms_enabled:
                    results['sms'] = await self.send_sms_notification(user_id, payload)
                elif channel == NotificationChannel.IN_APP and preferences.in_app_enabled:
                    results['in_app'] = await self.send_in_app_notification(user_id, payload)
            
            # Log notification
            self.log_notification(user_id, notification_type, payload, results)
            
            return {
                'sent': any(results.values()),
                'results': results,
                'channels_attempted': len(channels)
            }
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return {'sent': False, 'error': str(e)}
    
    def get_user_email(self, user_id: str) -> Optional[str]:
        """Get user email address"""
        try:
            if self.supabase:
                response = self.supabase.table('user_profiles').select('email').eq('user_id', user_id).execute()
                if response.data:
                    return response.data[0].get('email')
        except Exception as e:
            logger.error(f"Error getting user email: {e}")
        return None
    
    def get_user_phone(self, user_id: str) -> Optional[str]:
        """Get user phone number"""
        try:
            if self.supabase:
                response = self.supabase.table('user_profiles').select('phone').eq('user_id', user_id).execute()
                if response.data:
                    return response.data[0].get('phone')
        except Exception as e:
            logger.error(f"Error getting user phone: {e}")
        return None
    
    def format_email_html(self, payload: NotificationPayload) -> str:
        """Format notification as HTML email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{payload.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: #1a73e8; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .footer {{ text-align: center; padding: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Casablanca Insights</h1>
                </div>
                <div class="content">
                    <h2>{payload.title}</h2>
                    <p>{payload.body}</p>
                    {f'<p><small>Data: {json.dumps(payload.data)}</small></p>' if payload.data else ''}
                </div>
                <div class="footer">
                    <p>You received this notification from Casablanca Insights</p>
                    <p><a href="{os.getenv('FRONTEND_URL', 'https://casablancainsights.com')}">View Dashboard</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def log_notification(self, user_id: str, notification_type: NotificationType, payload: NotificationPayload, results: Dict[str, bool]):
        """Log notification attempt"""
        try:
            if self.supabase:
                log_data = {
                    'user_id': user_id,
                    'notification_type': notification_type.value,
                    'title': payload.title,
                    'body': payload.body,
                    'channels_attempted': list(results.keys()),
                    'success_count': sum(results.values()),
                    'total_channels': len(results),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.supabase.table('notification_logs').insert(log_data).execute()
        except Exception as e:
            logger.error(f"Error logging notification: {e}")
    
    def get_notification_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's notification history"""
        try:
            if self.supabase:
                response = self.supabase.table('notifications').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
                return response.data
            return []
        except Exception as e:
            logger.error(f"Error getting notification history: {e}")
            return []
    
    def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        """Mark notification as read"""
        try:
            if self.supabase:
                self.supabase.table('notifications').update({'read': True}).eq('id', notification_id).eq('user_id', user_id).execute()
                return True
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False

# Initialize service
notification_service = NotificationService() 