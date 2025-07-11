import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import json

from storage.local_fs import LocalFileStorage
from etl.fetch_ir_reports import IRReportFetcher
from etl.extract_from_pdf import PDFExtractor
from etl.translate_labels import LabelTranslator
from etl.compute_ratios import RatioCalculator
from models.financials import (
    FinancialData, GAAPFinancialData, ETLJob, JobType, JobStatus,
    ReportType
)

logger = logging.getLogger(__name__)

class ETLOrchestrator:
    """Main ETL pipeline orchestrator"""
    
    def __init__(self, storage: LocalFileStorage):
        self.storage = storage
        self.fetcher = IRReportFetcher(storage)
        self.extractor = PDFExtractor()
        self.translator = LabelTranslator()
        self.ratio_calculator = RatioCalculator()
        
        # Job tracking
        self.jobs: List[ETLJob] = []
    
    async def run_full_pipeline(self, companies: Optional[List[str]] = None, 
                               year: Optional[int] = None) -> Dict[str, Any]:
        """Run the complete ETL pipeline"""
        pipeline_start = datetime.now()
        results = {
            "start_time": pipeline_start,
            "companies_processed": [],
            "total_reports": 0,
            "successful_extractions": 0,
            "successful_translations": 0,
            "errors": []
        }
        
        try:
            # Step 1: Fetch reports
            logger.info("Starting report fetching...")
            fetch_job = ETLJob(
                job_type=JobType.FETCH,
                status=JobStatus.RUNNING,
                metadata={"companies": companies, "year": year}
            )
            self.jobs.append(fetch_job)
            
            reports = await self.fetcher.fetch_all_reports(companies, year)
            results["total_reports"] = len(reports)
            
            fetch_job.status = JobStatus.COMPLETED
            fetch_job.completed_at = datetime.now()
            
            # Step 2: Download reports
            logger.info(f"Downloading {len(reports)} reports...")
            downloaded_files = await self.fetcher.download_all_reports(reports)
            
            # Step 3: Process each company
            for company in set(report["company"] for report in reports):
                try:
                    company_results = await self._process_company(
                        company, year, downloaded_files
                    )
                    results["companies_processed"].append(company_results)
                    results["successful_extractions"] += company_results["extractions"]
                    results["successful_translations"] += company_results["translations"]
                    
                except Exception as e:
                    error_msg = f"Error processing company {company}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
            
            results["end_time"] = datetime.now()
            results["duration"] = (results["end_time"] - pipeline_start).total_seconds()
            
            logger.info(f"Pipeline completed in {results['duration']:.2f} seconds")
            
        except Exception as e:
            error_msg = f"Pipeline failed: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            results["end_time"] = datetime.now()
        
        return results
    
    async def _process_company(self, company: str, year: Optional[int], 
                             downloaded_files: List[str]) -> Dict[str, Any]:
        """Process all reports for a single company"""
        company_results = {
            "company": company,
            "year": year,
            "extractions": 0,
            "translations": 0,
            "reports_processed": []
        }
        
        # Get company-specific PDF files
        company_files = [f for f in downloaded_files if company in f]
        
        for pdf_path in company_files:
            try:
                report_result = await self._process_single_report(pdf_path, company, year)
                if report_result:
                    company_results["reports_processed"].append(report_result)
                    if report_result["extraction_success"]:
                        company_results["extractions"] += 1
                    if report_result["translation_success"]:
                        company_results["translations"] += 1
                        
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
        
        return company_results
    
    async def _process_single_report(self, pdf_path: str, company: str, 
                                   year: Optional[int]) -> Optional[Dict[str, Any]]:
        """Process a single PDF report"""
        try:
            # Determine report type and quarter from filename
            filename = Path(pdf_path).stem
            report_type = self._guess_report_type_from_filename(filename)
            quarter = self._extract_quarter_from_filename(filename)
            
            # Extract data from PDF
            logger.info(f"Extracting data from {pdf_path}")
            raw_data = self.extractor.extract_from_pdf(
                pdf_path=pdf_path,
                company=company,
                year=year or datetime.now().year,
                report_type=report_type,
                quarter=quarter
            )
            
            if not raw_data or not raw_data.lines:
                logger.warning(f"No data extracted from {pdf_path}")
                return {
                    "pdf_path": pdf_path,
                    "extraction_success": False,
                    "translation_success": False,
                    "error": "No data extracted"
                }
            
            # Save raw data
            raw_data_path = await self._save_raw_data(raw_data, company, year, quarter, report_type)
            
            # Translate to GAAP
            logger.info(f"Translating data for {company}")
            gaap_data = self.translator.translate_financial_data(raw_data)
            
            if not gaap_data.data:
                logger.warning(f"No data translated for {pdf_path}")
                return {
                    "pdf_path": pdf_path,
                    "extraction_success": True,
                    "translation_success": False,
                    "raw_data_path": raw_data_path,
                    "error": "No data translated"
                }
            
            # Compute ratios
            ratios = self.ratio_calculator.compute_ratios(gaap_data)
            gaap_data.ratios = ratios
            
            # Save GAAP data
            gaap_data_path = await self._save_gaap_data(gaap_data, raw_data_path)
            
            return {
                "pdf_path": pdf_path,
                "extraction_success": True,
                "translation_success": True,
                "raw_data_path": raw_data_path,
                "gaap_data_path": gaap_data_path,
                "lines_extracted": len(raw_data.lines),
                "lines_translated": len(gaap_data.data),
                "confidence_score": gaap_data.confidence_score,
                "ratios_computed": len(ratios)
            }
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            return {
                "pdf_path": pdf_path,
                "extraction_success": False,
                "translation_success": False,
                "error": str(e)
            }
    
    async def _save_raw_data(self, data: FinancialData, company: str, year: Optional[int],
                           quarter: Optional[int], report_type: ReportType) -> str:
        """Save raw extracted data"""
        filename = f"{company}_{year}"
        if quarter:
            filename += f"_Q{quarter}"
        filename += f"_{report_type.value}_raw.json"
        
        # Convert to dict for JSON serialization
        data_dict = {
            "company": data.company,
            "year": data.year,
            "quarter": data.quarter,
            "report_type": data.report_type.value,
            "language": data.language,
            "lines": [line.dict() for line in data.lines],
            "extraction_metadata": data.extraction_metadata
        }
        
        return await self.storage.save_processed_data(data_dict, filename)
    
    async def _save_gaap_data(self, data: GAAPFinancialData, raw_data_path: str) -> str:
        """Save GAAP translated data"""
        filename = f"{data.company}_{data.year}"
        if data.quarter:
            filename += f"_Q{data.quarter}"
        filename += f"_{data.report_type.value}_gaap.json"
        
        data_dict = {
            "company": data.company,
            "year": data.year,
            "quarter": data.quarter,
            "report_type": data.report_type.value,
            "raw_data_path": raw_data_path,
            "data": data.data,
            "ratios": data.ratios,
            "ai_summary": data.ai_summary,
            "confidence_score": data.confidence_score
        }
        
        return await self.storage.save_processed_data(data_dict, filename)
    
    def _guess_report_type_from_filename(self, filename: str) -> ReportType:
        """Guess report type from filename"""
        filename_lower = filename.lower()
        
        if any(term in filename_lower for term in ['pnl', 'resultat', 'compte']):
            return ReportType.PNL
        elif any(term in filename_lower for term in ['bilan', 'balance']):
            return ReportType.BALANCE
        elif any(term in filename_lower for term in ['flux', 'cashflow']):
            return ReportType.CASHFLOW
        else:
            return ReportType.OTHER
    
    def _extract_quarter_from_filename(self, filename: str) -> Optional[int]:
        """Extract quarter from filename"""
        import re
        
        quarter_patterns = [
            r'Q(\d)',  # Q1, Q2, Q3, Q4
            r'T(\d)',  # T1, T2, T3, T4
            r'(\d)er.*trimestre',  # 1er trimestre
            r'(\d)ème.*trimestre',  # 2ème trimestre
        ]
        
        for pattern in quarter_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                quarter = int(match.group(1))
                if 1 <= quarter <= 4:
                    return quarter
        
        return None
    
    def get_job_status(self, job_id: str) -> Optional[ETLJob]:
        """Get status of a specific job"""
        for job in self.jobs:
            if str(job.id) == job_id:
                return job
        return None
    
    def get_all_jobs(self) -> List[ETLJob]:
        """Get all jobs"""
        return self.jobs
    
    async def cleanup_old_data(self, days_old: int = 30):
        """Clean up old temporary files and data"""
        await self.storage.cleanup_temp_files(days_old * 24)

# Example usage
async def main():
    """Example usage of the ETL Orchestrator"""
    storage = LocalFileStorage()
    orchestrator = ETLOrchestrator(storage)
    
    # Run pipeline for ATW in 2024
    results = await orchestrator.run_full_pipeline(
        companies=["ATW"],
        year=2024
    )
    
    print(f"Pipeline completed in {results['duration']:.2f} seconds")
    print(f"Processed {len(results['companies_processed'])} companies")
    print(f"Total reports: {results['total_reports']}")
    print(f"Successful extractions: {results['successful_extractions']}")
    print(f"Successful translations: {results['successful_translations']}")
    
    if results['errors']:
        print(f"Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")

if __name__ == "__main__":
    asyncio.run(main()) 