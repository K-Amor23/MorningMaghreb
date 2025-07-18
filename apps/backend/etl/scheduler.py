import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import json
import os

from etl.etl_orchestrator import ETLOrchestrator
from storage.local_fs import LocalFileStorage
from models.financials import ETLJob, JobType, JobStatus
from database.database import get_db_session

logger = logging.getLogger(__name__)

class PipelineScheduler:
    """Scheduler for automated ETL pipeline execution"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.orchestrator = ETLOrchestrator(LocalFileStorage())
        self.jobs: Dict[str, ETLJob] = {}
        
        # Pipeline configuration
        self.config = {
            "daily_scrape": {
                "enabled": True,
                "time": "06:00",  # 6 AM
                "companies": ["ATW", "IAM", "BCP", "BMCE"],
                "max_age_days": 7
            },
            "weekly_cleanup": {
                "enabled": True,
                "day": "sunday",
                "time": "02:00",  # 2 AM
                "retention_days": 30
            },
            "monthly_full_sync": {
                "enabled": True,
                "day": 1,
                "time": "03:00",  # 3 AM
                "companies": ["ATW", "IAM", "BCP", "BMCE", "CIH", "WAA"]
            },
            "cache_refresh": {
                "enabled": True,
                "interval_minutes": 30
            }
        }
    
    async def start(self):
        """Start the scheduler"""
        try:
            # Add scheduled jobs
            await self._add_daily_scrape_job()
            await self._add_weekly_cleanup_job()
            await self._add_monthly_full_sync_job()
            await self._add_cache_refresh_job()
            
            # Start scheduler
            self.scheduler.start()
            logger.info("Pipeline scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Pipeline scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def _add_daily_scrape_job(self):
        """Add daily scraping job"""
        if not self.config["daily_scrape"]["enabled"]:
            return
        
        trigger = CronTrigger(
            hour=self.config["daily_scrape"]["time"].split(":")[0],
            minute=self.config["daily_scrape"]["time"].split(":")[1]
        )
        
        self.scheduler.add_job(
            func=self._run_daily_scrape,
            trigger=trigger,
            id="daily_scrape",
            name="Daily Financial Report Scraping",
            replace_existing=True
        )
        logger.info(f"Added daily scrape job at {self.config['daily_scrape']['time']}")
    
    async def _add_weekly_cleanup_job(self):
        """Add weekly cleanup job"""
        if not self.config["weekly_cleanup"]["enabled"]:
            return
        
        trigger = CronTrigger(
            day_of_week=self.config["weekly_cleanup"]["day"],
            hour=self.config["weekly_cleanup"]["time"].split(":")[0],
            minute=self.config["weekly_cleanup"]["time"].split(":")[1]
        )
        
        self.scheduler.add_job(
            func=self._run_weekly_cleanup,
            trigger=trigger,
            id="weekly_cleanup",
            name="Weekly Data Cleanup",
            replace_existing=True
        )
        logger.info(f"Added weekly cleanup job on {self.config['weekly_cleanup']['day']} at {self.config['weekly_cleanup']['time']}")
    
    async def _add_monthly_full_sync_job(self):
        """Add monthly full sync job"""
        if not self.config["monthly_full_sync"]["enabled"]:
            return
        
        trigger = CronTrigger(
            day=self.config["monthly_full_sync"]["day"],
            hour=self.config["monthly_full_sync"]["time"].split(":")[0],
            minute=self.config["monthly_full_sync"]["time"].split(":")[1]
        )
        
        self.scheduler.add_job(
            func=self._run_monthly_full_sync,
            trigger=trigger,
            id="monthly_full_sync",
            name="Monthly Full Data Sync",
            replace_existing=True
        )
        logger.info(f"Added monthly full sync job on day {self.config['monthly_full_sync']['day']} at {self.config['monthly_full_sync']['time']}")
    
    async def _add_cache_refresh_job(self):
        """Add cache refresh job"""
        if not self.config["cache_refresh"]["enabled"]:
            return
        
        trigger = IntervalTrigger(
            minutes=self.config["cache_refresh"]["interval_minutes"]
        )
        
        self.scheduler.add_job(
            func=self._run_cache_refresh,
            trigger=trigger,
            id="cache_refresh",
            name="Cache Refresh",
            replace_existing=True
        )
        logger.info(f"Added cache refresh job every {self.config['cache_refresh']['interval_minutes']} minutes")
    
    async def _run_daily_scrape(self):
        """Run daily scraping job"""
        job_id = f"daily_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        job = ETLJob(
            job_type=JobType.FETCH,
            status=JobStatus.RUNNING,
            metadata={
                "trigger": "daily_schedule",
                "companies": self.config["daily_scrape"]["companies"],
                "max_age_days": self.config["daily_scrape"]["max_age_days"]
            }
        )
        self.jobs[job_id] = job
        
        try:
            logger.info(f"Starting daily scrape job {job_id}")
            
            # Get companies that need updates
            companies_to_update = await self._get_companies_needing_updates(
                self.config["daily_scrape"]["max_age_days"]
            )
            
            if companies_to_update:
                results = await self.orchestrator.run_full_pipeline(
                    companies=companies_to_update,
                    year=datetime.now().year
                )
                
                job.status = JobStatus.COMPLETED
                job.metadata["results"] = results
                logger.info(f"Daily scrape completed: {len(companies_to_update)} companies updated")
            else:
                job.status = JobStatus.COMPLETED
                job.metadata["results"] = {"message": "No companies needed updates"}
                logger.info("Daily scrape completed: No updates needed")
                
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            logger.error(f"Daily scrape failed: {e}")
        
        finally:
            job.completed_at = datetime.now()
            await self._save_job_to_db(job_id, job)
    
    async def _run_weekly_cleanup(self):
        """Run weekly cleanup job"""
        job_id = f"weekly_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        job = ETLJob(
            job_type=JobType.CLEAN,
            status=JobStatus.RUNNING,
            metadata={
                "trigger": "weekly_schedule",
                "retention_days": self.config["weekly_cleanup"]["retention_days"]
            }
        )
        self.jobs[job_id] = job
        
        try:
            logger.info(f"Starting weekly cleanup job {job_id}")
            
            # Clean up old data
            await self.orchestrator.cleanup_old_data(
                self.config["weekly_cleanup"]["retention_days"]
            )
            
            job.status = JobStatus.COMPLETED
            logger.info("Weekly cleanup completed")
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            logger.error(f"Weekly cleanup failed: {e}")
        
        finally:
            job.completed_at = datetime.now()
            await self._save_job_to_db(job_id, job)
    
    async def _run_monthly_full_sync(self):
        """Run monthly full sync job"""
        job_id = f"monthly_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        job = ETLJob(
            job_type=JobType.FETCH,
            status=JobStatus.RUNNING,
            metadata={
                "trigger": "monthly_schedule",
                "companies": self.config["monthly_full_sync"]["companies"]
            }
        )
        self.jobs[job_id] = job
        
        try:
            logger.info(f"Starting monthly full sync job {job_id}")
            
            # Run full pipeline for all companies
            results = await self.orchestrator.run_full_pipeline(
                companies=self.config["monthly_full_sync"]["companies"],
                year=datetime.now().year
            )
            
            job.status = JobStatus.COMPLETED
            job.metadata["results"] = results
            logger.info("Monthly full sync completed")
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            logger.error(f"Monthly full sync failed: {e}")
        
        finally:
            job.completed_at = datetime.now()
            await self._save_job_to_db(job_id, job)
    
    async def _run_cache_refresh(self):
        """Run cache refresh job"""
        try:
            logger.info("Refreshing API cache")
            
            # Refresh Redis cache for frequently accessed data
            await self._refresh_api_cache()
            
            logger.info("Cache refresh completed")
            
        except Exception as e:
            logger.error(f"Cache refresh failed: {e}")
    
    async def _get_companies_needing_updates(self, max_age_days: int) -> List[str]:
        """Get companies that need data updates"""
        try:
            # Check last update time for each company
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # This would query your database to check last update times
            # For now, return all companies
            return self.config["daily_scrape"]["companies"]
            
        except Exception as e:
            logger.error(f"Error checking companies needing updates: {e}")
            return []
    
    async def _refresh_api_cache(self):
        """Refresh Redis cache for API endpoints"""
        try:
            # Import Redis client
            from cache.redis_client import redis_client
            
            # Refresh cache for key endpoints
            cache_keys_to_refresh = [
                "api:markets:overview",
                "api:financials:latest",
                "api:economic:indicators"
            ]
            
            for key in cache_keys_to_refresh:
                await redis_client.delete(key)
                logger.debug(f"Cleared cache key: {key}")
                
        except ImportError:
            logger.warning("Redis client not available, skipping cache refresh")
        except Exception as e:
            logger.error(f"Error refreshing cache: {e}")
    
    async def _save_job_to_db(self, job_id: str, job: ETLJob):
        """Save job to database"""
        try:
            # This would save to your database
            # For now, just log it
            logger.info(f"Job {job_id} completed with status: {job.status}")
            
        except Exception as e:
            logger.error(f"Error saving job to database: {e}")
    
    def get_job_status(self, job_id: str) -> Optional[ETLJob]:
        """Get job status by ID"""
        return self.jobs.get(job_id)
    
    def get_all_jobs(self) -> List[ETLJob]:
        """Get all jobs"""
        return list(self.jobs.values())
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self.scheduler.running,
            "jobs": len(self.scheduler.get_jobs()),
            "next_run": self._get_next_run_times()
        }
    
    def _get_next_run_times(self) -> Dict[str, str]:
        """Get next run times for all jobs"""
        next_runs = {}
        for job in self.scheduler.get_jobs():
            next_runs[job.id] = job.next_run_time.isoformat() if job.next_run_time else None
        return next_runs

# Global scheduler instance
scheduler = PipelineScheduler()

async def start_scheduler():
    """Start the global scheduler"""
    await scheduler.start()

async def stop_scheduler():
    """Stop the global scheduler"""
    await scheduler.stop() 