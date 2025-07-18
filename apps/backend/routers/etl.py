from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from etl.etl_orchestrator import ETLOrchestrator
from etl.scheduler import scheduler
from storage.local_fs import LocalFileStorage
from models.financials import (
    ETLJob, JobType, JobStatus, ETLJobResponse, 
    FinancialSummary, GAAPFinancialData
)
from cache.redis_client import redis_client, cache_response, CacheKeys, CacheTTL
from monitoring.health_checks import health_monitor

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Initialize components
orchestrator = ETLOrchestrator(LocalFileStorage())

@router.post("/trigger-pipeline", response_model=Dict[str, Any])
@cache_response(ttl=CacheTTL.ETL_JOBS, key_prefix="etl")
async def trigger_pipeline(
    companies: Optional[List[str]] = None,
    year: Optional[int] = None,
    background_tasks: BackgroundTasks = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Trigger ETL pipeline for specified companies"""
    try:
        # Validate input
        if companies and not all(isinstance(c, str) for c in companies):
            raise HTTPException(status_code=400, detail="Invalid company format")
        
        if year and (year < 2020 or year > datetime.now().year + 1):
            raise HTTPException(status_code=400, detail="Invalid year")
        
        # Run pipeline in background
        if background_tasks:
            background_tasks.add_task(
                orchestrator.run_full_pipeline,
                companies=companies,
                year=year
            )
            
            return {
                "message": "Pipeline triggered successfully",
                "job_id": f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "companies": companies or ["all"],
                "year": year,
                "status": "running"
            }
        else:
            # Run synchronously
            results = await orchestrator.run_full_pipeline(companies, year)
            return {
                "message": "Pipeline completed",
                "results": results,
                "status": "completed"
            }
            
    except Exception as e:
        logger.error(f"Pipeline trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs", response_model=List[ETLJobResponse])
@cache_response(ttl=CacheTTL.ETL_JOBS, key_prefix="etl")
async def get_jobs(
    status: Optional[JobStatus] = None,
    job_type: Optional[JobType] = None,
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get ETL jobs with optional filtering"""
    try:
        jobs = orchestrator.get_all_jobs()
        
        # Apply filters
        if status:
            jobs = [job for job in jobs if job.status == status]
        if job_type:
            jobs = [job for job in jobs if job.job_type == job_type]
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda x: x.started_at or datetime.min, reverse=True)
        
        # Apply limit
        jobs = jobs[:limit]
        
        return jobs
        
    except Exception as e:
        logger.error(f"Failed to get jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}", response_model=ETLJobResponse)
@cache_response(ttl=CacheTTL.ETL_JOBS, key_prefix="etl")
async def get_job_status(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get specific job status"""
    try:
        job = orchestrator.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=Dict[str, Any])
async def get_etl_health(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get ETL pipeline health status"""
    try:
        health_report = await health_monitor.run_all_checks()
        return health_report
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard", response_model=Dict[str, Any])
@cache_response(ttl=300, key_prefix="etl")  # 5 minutes cache
async def get_etl_dashboard(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get ETL dashboard data"""
    try:
        dashboard_data = await health_monitor.get_dashboard_data()
        
        # Add ETL-specific metrics
        recent_jobs = orchestrator.get_all_jobs()
        etl_metrics = {
            "total_jobs": len(recent_jobs),
            "successful_jobs": len([j for j in recent_jobs if j.status == JobStatus.COMPLETED]),
            "failed_jobs": len([j for j in recent_jobs if j.status == JobStatus.FAILED]),
            "running_jobs": len([j for j in recent_jobs if j.status == JobStatus.RUNNING]),
            "success_rate": len([j for j in recent_jobs if j.status == JobStatus.COMPLETED]) / len(recent_jobs) * 100 if recent_jobs else 0
        }
        
        dashboard_data["etl_metrics"] = etl_metrics
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Dashboard data failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies", response_model=List[str])
@cache_response(ttl=CacheTTL.FINANCIAL_HISTORY, key_prefix="etl")
async def get_available_companies(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get list of available companies"""
    try:
        # This would query your database for companies with data
        # For now, return configured companies
        companies = ["ATW", "IAM", "BCP", "BMCE", "CIH", "WAA"]
        return companies
        
    except Exception as e:
        logger.error(f"Failed to get companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/financials/{company}", response_model=List[FinancialSummary])
@cache_response(ttl=CacheTTL.FINANCIAL_LATEST, key_prefix="etl")
async def get_company_financials(
    company: str,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    report_type: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get financial data for a company"""
    try:
        # This would query your database for financial data
        # For now, return mock data
        mock_data = [
            FinancialSummary(
                company=company,
                year=year or 2024,
                quarter=quarter or 1,
                report_type="pnl",
                revenue=15000000000,
                net_income=2500000000,
                total_assets=200000000000,
                total_liabilities=150000000000,
                ratios={
                    "roe": 0.15,
                    "roa": 0.08,
                    "debt_to_equity": 0.75
                },
                summary="Strong financial performance with solid profitability ratios",
                last_updated=datetime.now()
            )
        ]
        
        return mock_data
        
    except Exception as e:
        logger.error(f"Failed to get financials for {company}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup", response_model=Dict[str, Any])
async def cleanup_old_data(
    days_old: int = 30,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Clean up old data"""
    try:
        if days_old < 1 or days_old > 365:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
        
        await orchestrator.cleanup_old_data(days_old)
        
        return {
            "message": f"Cleanup completed for data older than {days_old} days",
            "days_old": days_old,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scheduler/status", response_model=Dict[str, Any])
@cache_response(ttl=60, key_prefix="etl")  # 1 minute cache
async def get_scheduler_status(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get scheduler status"""
    try:
        return scheduler.get_scheduler_status()
        
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scheduler/start")
async def start_scheduler(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Start the scheduler"""
    try:
        await scheduler.start()
        return {"message": "Scheduler started successfully"}
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scheduler/stop")
async def stop_scheduler(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Stop the scheduler"""
    try:
        await scheduler.stop()
        return {"message": "Scheduler stopped successfully"}
        
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/stats", response_model=Dict[str, Any])
async def get_cache_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get Redis cache statistics"""
    try:
        stats = await redis_client.get_cache_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Clear cache entries"""
    try:
        if pattern:
            cleared_count = await redis_client.clear_pattern(pattern)
            return {
                "message": f"Cleared {cleared_count} cache entries matching pattern: {pattern}",
                "cleared_count": cleared_count,
                "pattern": pattern
            }
        else:
            # Clear all cache
            cleared_count = await redis_client.clear_pattern("api:*")
            return {
                "message": f"Cleared {cleared_count} cache entries",
                "cleared_count": cleared_count
            }
        
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=Dict[str, Any])
@cache_response(ttl=300, key_prefix="etl")  # 5 minutes cache
async def get_etl_metrics(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get ETL pipeline metrics"""
    try:
        jobs = orchestrator.get_all_jobs()
        
        # Calculate metrics
        total_jobs = len(jobs)
        successful_jobs = len([j for j in jobs if j.status == JobStatus.COMPLETED])
        failed_jobs = len([j for j in jobs if j.status == JobStatus.FAILED])
        running_jobs = len([j for j in jobs if j.status == JobStatus.RUNNING])
        
        # Calculate success rate
        success_rate = (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Get recent jobs (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_jobs = [j for j in jobs if j.started_at and j.started_at > cutoff_time]
        
        # Calculate average job duration
        completed_jobs = [j for j in jobs if j.status == JobStatus.COMPLETED and j.started_at and j.completed_at]
        avg_duration = 0
        if completed_jobs:
            durations = [(j.completed_at - j.started_at).total_seconds() for j in completed_jobs]
            avg_duration = sum(durations) / len(durations)
        
        return {
            "total_jobs": total_jobs,
            "successful_jobs": successful_jobs,
            "failed_jobs": failed_jobs,
            "running_jobs": running_jobs,
            "success_rate": round(success_rate, 2),
            "recent_jobs_24h": len(recent_jobs),
            "average_job_duration_seconds": round(avg_duration, 2),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_alerts(
    severity: Optional[str] = None,
    limit: int = 20,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get recent alerts"""
    try:
        # This would query your alert storage
        # For now, return mock alerts
        mock_alerts = [
            {
                "id": "alert_001",
                "severity": "warning",
                "message": "Data freshness check: Data is 25 hours old",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "component": "data_freshness"
            },
            {
                "id": "alert_002", 
                "severity": "info",
                "message": "ETL pipeline completed successfully",
                "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                "component": "etl_pipeline"
            }
        ]
        
        # Filter by severity if specified
        if severity:
            mock_alerts = [alert for alert in mock_alerts if alert["severity"] == severity]
        
        return mock_alerts[:limit]
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 