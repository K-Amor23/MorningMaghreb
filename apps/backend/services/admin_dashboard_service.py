"""
Admin Dashboard Service
Handles user analytics, data ingestion monitoring, and system performance metrics
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, text

from models.admin_dashboard import (
    UserAnalytics, DataIngestionLog, SystemPerformance
)
from models.user import User, UserProfile
from models.market_data import Quote, Company

logger = logging.getLogger(__name__)


class AdminDashboardService:
    """Service for admin dashboard analytics and monitoring"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================================
    # USER ANALYTICS
    # ============================================================================
    
    async def track_user_activity(
        self,
        user_id: str,
        session_id: str,
        page_visited: str,
        action_type: str,
        action_data: Dict[str, Any] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        session_duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """Track user activity for analytics"""
        try:
            analytics = UserAnalytics(
                user_id=user_id,
                session_id=session_id,
                page_visited=page_visited,
                action_type=action_type,
                action_data=action_data or {},
                user_agent=user_agent,
                ip_address=ip_address,
                session_duration=session_duration
            )
            self.db.add(analytics)
            self.db.commit()
            
            return {
                "success": True,
                "analytics_id": str(analytics.id),
                "message": "Activity tracked successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error tracking user activity: {e}")
            raise HTTPException(status_code=500, detail="Failed to track activity")
    
    async def get_user_engagement_metrics(
        self,
        days: int = 30,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user engagement metrics"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Base query
            query = self.db.query(UserAnalytics).filter(
                UserAnalytics.created_at >= start_date
            )
            
            if user_id:
                query = query.filter(UserAnalytics.user_id == user_id)
            
            # Total activities
            total_activities = query.count()
            
            # Unique users
            unique_users = query.with_entities(UserAnalytics.user_id).distinct().count()
            
            # Unique sessions
            unique_sessions = query.with_entities(UserAnalytics.session_id).distinct().count()
            
            # Average session duration
            avg_session_duration = query.with_entities(
                func.avg(UserAnalytics.session_duration)
            ).scalar() or 0
            
            # Most visited pages
            page_visits = query.with_entities(
                UserAnalytics.page_visited,
                func.count(UserAnalytics.id).label('visit_count')
            ).group_by(UserAnalytics.page_visited).order_by(
                desc(text('visit_count'))
            ).limit(10).all()
            
            # Action type distribution
            action_distribution = query.with_entities(
                UserAnalytics.action_type,
                func.count(UserAnalytics.id).label('action_count')
            ).group_by(UserAnalytics.action_type).all()
            
            # Daily activity trend
            daily_activity = query.with_entities(
                func.date(UserAnalytics.created_at).label('date'),
                func.count(UserAnalytics.id).label('activity_count')
            ).group_by(text('date')).order_by(text('date')).all()
            
            return {
                "period_days": days,
                "total_activities": total_activities,
                "unique_users": unique_users,
                "unique_sessions": unique_sessions,
                "avg_session_duration_seconds": float(avg_session_duration),
                "most_visited_pages": [
                    {"page": page, "visits": count} 
                    for page, count in page_visits
                ],
                "action_distribution": [
                    {"action": action, "count": count} 
                    for action, count in action_distribution
                ],
                "daily_activity_trend": [
                    {"date": date.isoformat(), "count": count} 
                    for date, count in daily_activity
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user engagement metrics: {e}")
            raise HTTPException(status_code=500, detail="Failed to get engagement metrics")
    
    async def get_user_retention_analysis(self, days: int = 90) -> Dict[str, Any]:
        """Analyze user retention patterns"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get all users with their first activity
            user_first_activity = self.db.query(
                UserAnalytics.user_id,
                func.min(UserAnalytics.created_at).label('first_activity'),
                func.max(UserAnalytics.created_at).label('last_activity'),
                func.count(UserAnalytics.id).label('total_activities')
            ).filter(
                UserAnalytics.created_at >= start_date
            ).group_by(UserAnalytics.user_id).all()
            
            # Calculate retention cohorts
            cohorts = {}
            for user_id, first_activity, last_activity, total_activities in user_first_activity:
                cohort_week = first_activity.strftime('%Y-%W')
                if cohort_week not in cohorts:
                    cohorts[cohort_week] = {
                        "users": [],
                        "total_users": 0,
                        "retention_rates": {}
                    }
                
                cohorts[cohort_week]["users"].append({
                    "user_id": user_id,
                    "first_activity": first_activity.isoformat(),
                    "last_activity": last_activity.isoformat(),
                    "total_activities": total_activities,
                    "days_active": (last_activity - first_activity).days
                })
                cohorts[cohort_week]["total_users"] += 1
            
            # Calculate retention rates for each cohort
            for cohort_week, cohort_data in cohorts.items():
                for user_data in cohort_data["users"]:
                    days_active = user_data["days_active"]
                    week_retention = min(days_active // 7, 12)  # Up to 12 weeks
                    
                    for week in range(1, week_retention + 1):
                        week_key = f"week_{week}"
                        if week_key not in cohort_data["retention_rates"]:
                            cohort_data["retention_rates"][week_key] = 0
                        cohort_data["retention_rates"][week_key] += 1
                
                # Convert to percentages
                total_users = cohort_data["total_users"]
                for week_key in cohort_data["retention_rates"]:
                    cohort_data["retention_rates"][week_key] = (
                        cohort_data["retention_rates"][week_key] / total_users * 100
                    )
            
            return {
                "analysis_period_days": days,
                "total_cohorts": len(cohorts),
                "cohorts": cohorts
            }
            
        except Exception as e:
            logger.error(f"Error analyzing user retention: {e}")
            raise HTTPException(status_code=500, detail="Failed to analyze retention")
    
    async def get_top_performing_users(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top performing users based on engagement"""
        try:
            # Calculate engagement scores using database function
            top_users = self.db.execute(text("""
                SELECT 
                    u.id as user_id,
                    u.email,
                    up.subscription_tier,
                    calculate_user_engagement_score(u.id) as engagement_score,
                    COUNT(DISTINCT ua.session_id) as total_sessions,
                    COUNT(ua.id) as total_actions,
                    MAX(ua.created_at) as last_activity
                FROM users u
                LEFT JOIN user_profiles up ON u.id = up.user_id
                LEFT JOIN user_analytics ua ON u.id = ua.user_id
                GROUP BY u.id, u.email, up.subscription_tier
                ORDER BY calculate_user_engagement_score(u.id) DESC
                LIMIT :limit
            """), {"limit": limit}).fetchall()
            
            user_data = []
            for user in top_users:
                user_data.append({
                    "user_id": str(user.user_id),
                    "email": user.email,
                    "subscription_tier": user.subscription_tier,
                    "engagement_score": float(user.engagement_score),
                    "total_sessions": user.total_sessions,
                    "total_actions": user.total_actions,
                    "last_activity": user.last_activity.isoformat() if user.last_activity else None
                })
            
            return user_data
            
        except Exception as e:
            logger.error(f"Error getting top performing users: {e}")
            raise HTTPException(status_code=500, detail="Failed to get top users")
    
    # ============================================================================
    # DATA INGESTION MONITORING
    # ============================================================================
    
    async def log_data_ingestion(
        self,
        source_name: str,
        data_type: str,
        ingestion_type: str,
        records_processed: int,
        records_successful: int,
        records_failed: int = 0,
        processing_time_ms: Optional[int] = None,
        file_size_bytes: Optional[int] = None,
        error_messages: Optional[List[str]] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Log data ingestion activity"""
        try:
            ingestion_log = DataIngestionLog(
                source_name=source_name,
                data_type=data_type,
                ingestion_type=ingestion_type,
                records_processed=records_processed,
                records_successful=records_successful,
                records_failed=records_failed,
                processing_time_ms=processing_time_ms,
                file_size_bytes=file_size_bytes,
                error_messages=error_messages or [],
                metadata=metadata or {},
                started_at=datetime.now()
            )
            self.db.add(ingestion_log)
            self.db.commit()
            
            return {
                "success": True,
                "log_id": str(ingestion_log.id),
                "message": "Data ingestion logged successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging data ingestion: {e}")
            raise HTTPException(status_code=500, detail="Failed to log ingestion")
    
    async def complete_data_ingestion(
        self,
        log_id: str,
        error_messages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Mark data ingestion as completed"""
        try:
            ingestion_log = self.db.query(DataIngestionLog).filter(
                DataIngestionLog.id == log_id
            ).first()
            
            if not ingestion_log:
                raise HTTPException(status_code=404, detail="Ingestion log not found")
            
            ingestion_log.completed_at = datetime.now()
            if error_messages:
                ingestion_log.error_messages = error_messages
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Data ingestion completed"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error completing data ingestion: {e}")
            raise HTTPException(status_code=500, detail="Failed to complete ingestion")
    
    async def get_data_ingestion_summary(
        self,
        days: int = 30,
        source_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get data ingestion summary"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Base query
            query = self.db.query(DataIngestionLog).filter(
                DataIngestionLog.started_at >= start_date
            )
            
            if source_name:
                query = query.filter(DataIngestionLog.source_name == source_name)
            
            # Total ingestion jobs
            total_jobs = query.count()
            
            # Successful vs failed jobs
            successful_jobs = query.filter(DataIngestionLog.records_failed == 0).count()
            failed_jobs = total_jobs - successful_jobs
            
            # Total records processed
            total_records = query.with_entities(
                func.sum(DataIngestionLog.records_processed)
            ).scalar() or 0
            
            # Total successful records
            total_successful = query.with_entities(
                func.sum(DataIngestionLog.records_successful)
            ).scalar() or 0
            
            # Average processing time
            avg_processing_time = query.with_entities(
                func.avg(DataIngestionLog.processing_time_ms)
            ).scalar() or 0
            
            # Success rate by source
            source_success_rates = query.with_entities(
                DataIngestionLog.source_name,
                func.avg(
                    func.cast(DataIngestionLog.records_successful, func.Float) /
                    func.cast(DataIngestionLog.records_processed, func.Float)
                ).label('success_rate')
            ).group_by(DataIngestionLog.source_name).all()
            
            # Recent ingestion activity
            recent_activity = query.order_by(
                desc(DataIngestionLog.started_at)
            ).limit(10).all()
            
            recent_activity_data = []
            for activity in recent_activity:
                recent_activity_data.append({
                    "id": str(activity.id),
                    "source_name": activity.source_name,
                    "data_type": activity.data_type,
                    "records_processed": activity.records_processed,
                    "records_successful": activity.records_successful,
                    "records_failed": activity.records_failed,
                    "processing_time_ms": activity.processing_time_ms,
                    "started_at": activity.started_at.isoformat(),
                    "completed_at": activity.completed_at.isoformat() if activity.completed_at else None,
                    "success_rate": (
                        activity.records_successful / activity.records_processed * 100
                        if activity.records_processed > 0 else 0
                    )
                })
            
            return {
                "period_days": days,
                "total_jobs": total_jobs,
                "successful_jobs": successful_jobs,
                "failed_jobs": failed_jobs,
                "success_rate": (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0,
                "total_records_processed": total_records,
                "total_records_successful": total_successful,
                "avg_processing_time_ms": float(avg_processing_time),
                "source_success_rates": [
                    {"source": source, "success_rate": float(rate)}
                    for source, rate in source_success_rates
                ],
                "recent_activity": recent_activity_data
            }
            
        except Exception as e:
            logger.error(f"Error getting data ingestion summary: {e}")
            raise HTTPException(status_code=500, detail="Failed to get ingestion summary")
    
    # ============================================================================
    # SYSTEM PERFORMANCE MONITORING
    # ============================================================================
    
    async def log_system_performance(
        self,
        metric_name: str,
        metric_value: Decimal,
        metric_unit: Optional[str] = None,
        component: str = "api",
        severity: str = "info",
        tags: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Log system performance metric"""
        try:
            performance = SystemPerformance(
                metric_name=metric_name,
                metric_value=metric_value,
                metric_unit=metric_unit,
                component=component,
                severity=severity,
                tags=tags or {}
            )
            self.db.add(performance)
            self.db.commit()
            
            return {
                "success": True,
                "performance_id": str(performance.id),
                "message": "Performance metric logged successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging system performance: {e}")
            raise HTTPException(status_code=500, detail="Failed to log performance")
    
    async def get_system_performance_summary(
        self,
        hours: int = 24,
        component: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get system performance summary"""
        try:
            start_time = datetime.now() - timedelta(hours=hours)
            
            # Base query
            query = self.db.query(SystemPerformance).filter(
                SystemPerformance.recorded_at >= start_time
            )
            
            if component:
                query = query.filter(SystemPerformance.component == component)
            
            # Get latest metrics for each metric name
            latest_metrics = query.with_entities(
                SystemPerformance.metric_name,
                SystemPerformance.metric_value,
                SystemPerformance.metric_unit,
                SystemPerformance.component,
                SystemPerformance.severity,
                SystemPerformance.recorded_at
            ).order_by(
                SystemPerformance.metric_name,
                desc(SystemPerformance.recorded_at)
            ).distinct(SystemPerformance.metric_name).all()
            
            # Calculate averages for key metrics
            avg_response_time = query.filter(
                SystemPerformance.metric_name == "api_response_time"
            ).with_entities(
                func.avg(SystemPerformance.metric_value)
            ).scalar() or 0
            
            avg_cpu_usage = query.filter(
                SystemPerformance.metric_name == "cpu_usage"
            ).with_entities(
                func.avg(SystemPerformance.metric_value)
            ).scalar() or 0
            
            avg_memory_usage = query.filter(
                SystemPerformance.metric_name == "memory_usage"
            ).with_entities(
                func.avg(SystemPerformance.metric_value)
            ).scalar() or 0
            
            # Error count
            error_count = query.filter(
                SystemPerformance.severity.in_(["error", "critical"])
            ).count()
            
            # Performance trends
            performance_trends = query.with_entities(
                func.date_trunc('hour', SystemPerformance.recorded_at).label('hour'),
                func.avg(SystemPerformance.metric_value).label('avg_value')
            ).filter(
                SystemPerformance.metric_name == "api_response_time"
            ).group_by(text('hour')).order_by(text('hour')).all()
            
            return {
                "monitoring_period_hours": hours,
                "latest_metrics": [
                    {
                        "metric_name": metric.metric_name,
                        "value": float(metric.metric_value),
                        "unit": metric.metric_unit,
                        "component": metric.component,
                        "severity": metric.severity,
                        "recorded_at": metric.recorded_at.isoformat()
                    }
                    for metric in latest_metrics
                ],
                "averages": {
                    "response_time_ms": float(avg_response_time),
                    "cpu_usage_percent": float(avg_cpu_usage),
                    "memory_usage_percent": float(avg_memory_usage)
                },
                "error_count": error_count,
                "performance_trends": [
                    {
                        "hour": hour.isoformat(),
                        "avg_response_time": float(avg_value)
                    }
                    for hour, avg_value in performance_trends
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting system performance summary: {e}")
            raise HTTPException(status_code=500, detail="Failed to get performance summary")
    
    # ============================================================================
    # DASHBOARD OVERVIEW
    # ============================================================================
    
    async def get_admin_dashboard_overview(self) -> Dict[str, Any]:
        """Get comprehensive admin dashboard overview"""
        try:
            # User metrics
            total_users = self.db.query(User).count()
            active_users_30d = self.db.query(UserAnalytics.user_id).filter(
                UserAnalytics.created_at >= datetime.now() - timedelta(days=30)
            ).distinct().count()
            
            # Data quality metrics
            data_freshness_score = self.db.execute(
                text("SELECT calculate_data_freshness_score()")
            ).scalar() or 0
            
            # System health
            recent_errors = self.db.query(SystemPerformance).filter(
                and_(
                    SystemPerformance.severity.in_(["error", "critical"]),
                    SystemPerformance.recorded_at >= datetime.now() - timedelta(hours=24)
                )
            ).count()
            
            # Data ingestion health
            recent_ingestion_jobs = self.db.query(DataIngestionLog).filter(
                DataIngestionLog.started_at >= datetime.now() - timedelta(hours=24)
            ).count()
            
            successful_ingestion_jobs = self.db.query(DataIngestionLog).filter(
                and_(
                    DataIngestionLog.started_at >= datetime.now() - timedelta(hours=24),
                    DataIngestionLog.records_failed == 0
                )
            ).count()
            
            ingestion_success_rate = (
                successful_ingestion_jobs / recent_ingestion_jobs * 100
                if recent_ingestion_jobs > 0 else 100
            )
            
            return {
                "user_metrics": {
                    "total_users": total_users,
                    "active_users_30d": active_users_30d,
                    "user_growth_rate": 0  # Calculate from historical data
                },
                "data_quality": {
                    "freshness_score": float(data_freshness_score),
                    "overall_quality": "Good" if data_freshness_score > 80 else "Needs Attention"
                },
                "system_health": {
                    "recent_errors": recent_errors,
                    "status": "Healthy" if recent_errors < 5 else "Warning",
                    "uptime_percentage": 99.5  # Mock value
                },
                "data_ingestion": {
                    "recent_jobs": recent_ingestion_jobs,
                    "success_rate": float(ingestion_success_rate),
                    "status": "Good" if ingestion_success_rate > 95 else "Needs Attention"
                },
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting admin dashboard overview: {e}")
            raise HTTPException(status_code=500, detail="Failed to get dashboard overview") 