from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

from models.financials import (
    ETLJobResponse, FinancialSummary, JobType, JobStatus,
    ReportType
)
from etl.etl_orchestrator import ETLOrchestrator
from storage.local_fs import LocalFileStorage
from utils.auth import verify_token

logger = logging.getLogger(__name__)

router = APIRouter()

# Global orchestrator instance
orchestrator: Optional[ETLOrchestrator] = None

def get_orchestrator() -> ETLOrchestrator:
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        storage = LocalFileStorage()
        orchestrator = ETLOrchestrator(storage)
    return orchestrator

@router.post("/trigger-pipeline", response_model=Dict[str, Any])
async def trigger_pipeline(
    companies: Optional[List[str]] = None,
    year: Optional[int] = None,
    background_tasks: BackgroundTasks = None,
    orchestrator: ETLOrchestrator = Depends(get_orchestrator),
    user: dict = Depends(verify_token)
):
    """Trigger the ETL pipeline for specified companies and year"""
    try:
        # Validate input
        if companies and not all(isinstance(c, str) for c in companies):
            raise HTTPException(status_code=400, detail="Companies must be strings")
        
        if year and (year < 2000 or year > datetime.now().year + 1):
            raise HTTPException(status_code=400, detail="Invalid year")
        
        # Create job tracking
        job = ETLJobResponse(
            id=str(len(orchestrator.jobs) + 1),  # Simple ID generation
            job_type=JobType.FETCH,
            status=JobStatus.PENDING,
            company=", ".join(companies) if companies else "All",
            year=year,
            quarter=None,
            created_at=datetime.now()
        )
        
        # Add to background tasks if available
        if background_tasks:
            background_tasks.add_task(
                run_pipeline_background,
                orchestrator,
                companies,
                year,
                job.id
            )
        else:
            # Run synchronously
            await run_pipeline_background(orchestrator, companies, year, job.id)
        
        return {
            "message": "Pipeline triggered successfully",
            "job_id": job.id,
            "companies": companies,
            "year": year,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Error triggering pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs", response_model=List[ETLJobResponse])
async def get_jobs(
    orchestrator: ETLOrchestrator = Depends(get_orchestrator),
    user: dict = Depends(verify_token)
):
    """Get all ETL jobs"""
    try:
        jobs = orchestrator.get_all_jobs()
        return [
            ETLJobResponse(
                id=str(i),
                job_type=job.job_type,
                status=job.status,
                company=job.company,
                year=job.year,
                quarter=job.quarter,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at
            )
            for i, job in enumerate(jobs)
        ]
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}", response_model=ETLJobResponse)
async def get_job_status(
    job_id: str,
    orchestrator: ETLOrchestrator = Depends(get_orchestrator),
    user: dict = Depends(verify_token)
):
    """Get status of a specific job"""
    try:
        job = orchestrator.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return ETLJobResponse(
            id=job_id,
            job_type=job.job_type,
            status=job.status,
            company=job.company,
            year=job.year,
            quarter=job.quarter,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/financials/{company}", response_model=List[FinancialSummary])
async def get_company_financials(
    company: str,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    report_type: Optional[ReportType] = None,
    orchestrator: ETLOrchestrator = Depends(get_orchestrator),
    user: dict = Depends(verify_token)
):
    """Get financial data for a specific company"""
    try:
        # This would typically query the database
        # For now, return mock data
        summaries = []
        
        # Mock data - in real implementation, query database
        if year:
            years = [year]
        else:
            years = [2023, 2024]
        
        for y in years:
            if quarter:
                quarters = [quarter]
            else:
                quarters = [1, 2, 3, 4]
            
            for q in quarters:
                if report_type:
                    types = [report_type]
                else:
                    types = [ReportType.PNL, ReportType.BALANCE]
                
                for rt in types:
                    summary = FinancialSummary(
                        company=company,
                        year=y,
                        quarter=q,
                        report_type=rt,
                        revenue=13940000000 if rt == ReportType.PNL else None,
                        net_income=3600000000 if rt == ReportType.PNL else None,
                        total_assets=45000000000 if rt == ReportType.BALANCE else None,
                        total_liabilities=20000000000 if rt == ReportType.BALANCE else None,
                        ratios={
                            "roe": 14.4,
                            "roa": 8.0,
                            "debt_to_equity": 0.8
                        } if rt == ReportType.PNL else None,
                        summary=f"Strong performance in {y} Q{q}",
                        last_updated=datetime.now()
                    )
                    summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        logger.error(f"Error getting financials for {company}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies", response_model=List[str])
async def get_available_companies(
    orchestrator: ETLOrchestrator = Depends(get_orchestrator),
    user: dict = Depends(verify_token)
):
    """Get list of available companies"""
    try:
        # Return companies from the fetcher configuration
        fetcher = orchestrator.fetcher
        return list(fetcher.company_ir_pages.keys())
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_old_data(
    days_old: int = 30,
    orchestrator: ETLOrchestrator = Depends(get_orchestrator),
    user: dict = Depends(verify_token)
):
    """Clean up old temporary files and data"""
    try:
        await orchestrator.cleanup_old_data(days_old)
        return {
            "message": f"Cleanup completed for files older than {days_old} days",
            "days_old": days_old
        }
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def etl_health_check(
    orchestrator: ETLOrchestrator = Depends(get_orchestrator),
    user: dict = Depends(verify_token)
):
    """Health check for ETL pipeline"""
    try:
        # Check if orchestrator is working
        storage = orchestrator.storage
        companies = list(orchestrator.fetcher.company_ir_pages.keys())
        
        return {
            "status": "healthy",
            "orchestrator": "running",
            "storage": "available",
            "available_companies": len(companies),
            "active_jobs": len([j for j in orchestrator.jobs if j.status == JobStatus.RUNNING]),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_pipeline_background(
    orchestrator: ETLOrchestrator,
    companies: Optional[List[str]],
    year: Optional[int],
    job_id: str
):
    """Run pipeline in background"""
    try:
        logger.info(f"Starting background pipeline for job {job_id}")
        
        # Update job status
        job = orchestrator.get_job_status(job_id)
        if job:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()
        
        # Run pipeline
        results = await orchestrator.run_full_pipeline(companies, year)
        
        # Update job status
        if job:
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.metadata = results
        
        logger.info(f"Background pipeline completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Background pipeline failed for job {job_id}: {e}")
        
        # Update job status
        job = orchestrator.get_job_status(job_id)
        if job:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            job.error_message = str(e) 