import pdfplumber
import fitz  # PyMuPDF
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import re
import logging
from pathlib import Path

from models.financials import FinancialData, FinancialLine, ReportType

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Extracts financial data from PDF reports"""
    
    def __init__(self):
        self.number_patterns = [
            r'[\d\s,]+\.?\d*',  # Basic number pattern
            r'[\d\s,]+',        # Numbers with spaces/commas
            r'[\d]+\.?[\d]*',   # Decimal numbers
        ]
        
        # Common French financial terms to look for
        self.financial_terms = [
            "Revenus nets", "Chiffre d'affaires", "Ventes",
            "Charges d'exploitation", "Frais de personnel",
            "Résultat d'exploitation", "Résultat net",
            "Actif", "Passif", "Capitaux propres",
            "Trésorerie", "Dettes", "Créances"
        ]
    
    def extract_from_pdf(self, pdf_path: str, company: str, year: int, 
                        report_type: ReportType, quarter: Optional[int] = None) -> FinancialData:
        """Main extraction method"""
        try:
            # Try pdfplumber first (better for tables)
            data = self._extract_with_pdfplumber(pdf_path, company, year, report_type, quarter)
            if data and data.lines:
                return data
            
            # Fallback to PyMuPDF
            data = self._extract_with_pymupdf(pdf_path, company, year, report_type, quarter)
            if data and data.lines:
                return data
            
            # If both fail, return empty data
            return FinancialData(
                company=company,
                year=year,
                quarter=quarter,
                report_type=report_type,
                lines=[],
                extraction_metadata={"method": "failed", "error": "No data extracted"}
            )
            
        except Exception as e:
            logger.error(f"Error extracting from {pdf_path}: {e}")
            return FinancialData(
                company=company,
                year=year,
                quarter=quarter,
                report_type=report_type,
                lines=[],
                extraction_metadata={"method": "error", "error": str(e)}
            )
    
    def _extract_with_pdfplumber(self, pdf_path: str, company: str, year: int,
                                report_type: ReportType, quarter: Optional[int] = None) -> Optional[FinancialData]:
        """Extract using pdfplumber (better for tabular data)"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                all_lines = []
                extraction_metadata = {
                    "method": "pdfplumber",
                    "total_pages": len(pdf.pages),
                    "extracted_pages": 0
                }
                
                for page_num, page in enumerate(pdf.pages):
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            lines = self._process_table(table, page_num)
                            all_lines.extend(lines)
                    
                    # Extract text and look for financial data
                    text = page.extract_text()
                    if text:
                        text_lines = self._extract_from_text(text, page_num)
                        all_lines.extend(text_lines)
                    
                    extraction_metadata["extracted_pages"] += 1
                
                if all_lines:
                    return FinancialData(
                        company=company,
                        year=year,
                        quarter=quarter,
                        report_type=report_type,
                        lines=all_lines,
                        extraction_metadata=extraction_metadata
                    )
        
        except Exception as e:
            logger.error(f"Error with pdfplumber extraction: {e}")
        
        return None
    
    def _extract_with_pymupdf(self, pdf_path: str, company: str, year: int,
                             report_type: ReportType, quarter: Optional[int] = None) -> Optional[FinancialData]:
        """Extract using PyMuPDF (fallback method)"""
        try:
            doc = fitz.open(pdf_path)
            all_lines = []
            extraction_metadata = {
                "method": "pymupdf",
                "total_pages": len(doc),
                "extracted_pages": 0
            }
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text:
                    lines = self._extract_from_text(text, page_num)
                    all_lines.extend(lines)
                
                extraction_metadata["extracted_pages"] += 1
            
            doc.close()
            
            if all_lines:
                return FinancialData(
                    company=company,
                    year=year,
                    quarter=quarter,
                    report_type=report_type,
                    lines=all_lines,
                    extraction_metadata=extraction_metadata
                )
        
        except Exception as e:
            logger.error(f"Error with PyMuPDF extraction: {e}")
        
        return None
    
    def _process_table(self, table: List[List[str]], page_num: int) -> List[FinancialLine]:
        """Process extracted table data"""
        lines = []
        
        for row in table:
            if not row or len(row) < 2:
                continue
            
            # Clean row data
            cleaned_row = [str(cell).strip() if cell else "" for cell in row]
            
            # Look for label-value pairs
            for i in range(len(cleaned_row) - 1):
                label = cleaned_row[i]
                value_str = cleaned_row[i + 1]
                
                if self._is_financial_label(label) and self._is_number(value_str):
                    value = self._parse_number(value_str)
                    if value is not None:
                        lines.append(FinancialLine(
                            label=label,
                            value=value,
                            unit="MAD",
                            confidence=0.8
                        ))
        
        return lines
    
    def _extract_from_text(self, text: str, page_num: int) -> List[FinancialLine]:
        """Extract financial data from text"""
        lines = []
        
        # Split text into lines
        text_lines = text.split('\n')
        
        for line in text_lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for patterns like "Label: Value" or "Label Value"
            patterns = [
                r'([^:]+):\s*([\d\s,\.]+)',  # Label: Value
                r'([^0-9]+)\s+([\d\s,\.]+)',  # Label Value
                r'([^=]+)=\s*([\d\s,\.]+)',   # Label=Value
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, line)
                for label, value_str in matches:
                    label = label.strip()
                    if self._is_financial_label(label) and self._is_number(value_str):
                        value = self._parse_number(value_str)
                        if value is not None:
                            lines.append(FinancialLine(
                                label=label,
                                value=value,
                                unit="MAD",
                                confidence=0.6
                            ))
        
        return lines
    
    def _is_financial_label(self, text: str) -> bool:
        """Check if text contains financial terms"""
        text_lower = text.lower()
        
        # Check against known financial terms
        for term in self.financial_terms:
            if term.lower() in text_lower:
                return True
        
        # Check for common patterns
        patterns = [
            r'revenu', r'chiffre', r'vente',
            r'charge', r'frais', r'coût',
            r'résultat', r'bénéfice', r'perte',
            r'actif', r'passif', r'capital',
            r'trésorerie', r'dette', r'créance'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _is_number(self, text: str) -> bool:
        """Check if text represents a number"""
        if not text:
            return False
        
        # Remove common non-numeric characters
        cleaned = re.sub(r'[^\d\s,\.\-]', '', text)
        cleaned = cleaned.strip()
        
        if not cleaned:
            return False
        
        # Check if it matches number patterns
        for pattern in self.number_patterns:
            if re.fullmatch(pattern, cleaned):
                return True
        
        return False
    
    def _parse_number(self, text: str) -> Optional[float]:
        """Parse number from text"""
        try:
            # Remove non-numeric characters except digits, commas, dots, and minus
            cleaned = re.sub(r'[^\d\s,\.\-]', '', text)
            cleaned = cleaned.strip()
            
            # Handle French number format (comma as decimal separator)
            if ',' in cleaned and '.' in cleaned:
                # Both comma and dot present - assume comma is thousands separator
                cleaned = cleaned.replace(',', '')
            elif ',' in cleaned and '.' not in cleaned:
                # Only comma present - check if it's decimal separator
                parts = cleaned.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Likely decimal separator
                    cleaned = cleaned.replace(',', '.')
                else:
                    # Likely thousands separator
                    cleaned = cleaned.replace(',', '')
            
            # Convert to float
            value = float(cleaned)
            
            # Handle common multipliers (millions, billions)
            text_lower = text.lower()
            if 'milliard' in text_lower or 'billion' in text_lower:
                value *= 1_000_000_000
            elif 'million' in text_lower:
                value *= 1_000_000
            elif 'mille' in text_lower or 'thousand' in text_lower:
                value *= 1_000
            
            return value
        
        except (ValueError, TypeError):
            return None
    
    def extract_multiple_pdfs(self, pdf_paths: List[str], company: str, year: int,
                            report_types: Optional[List[ReportType]] = None) -> List[FinancialData]:
        """Extract data from multiple PDFs"""
        results = []
        
        for pdf_path in pdf_paths:
            # Try to determine report type from filename
            filename = Path(pdf_path).stem
            report_type = self._guess_report_type_from_filename(filename)
            
            if report_types and report_type not in report_types:
                continue
            
            # Try to extract quarter from filename
            quarter = self._extract_quarter_from_filename(filename)
            
            data = self.extract_from_pdf(pdf_path, company, year, report_type, quarter)
            if data and data.lines:
                results.append(data)
        
        return results
    
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

# Example usage
def main():
    """Example usage of the PDF Extractor"""
    extractor = PDFExtractor()
    
    # Example PDF path
    pdf_path = "data/raw_pdfs/ATW/2024/ATW_2024_Q1_pnl.pdf"
    
    if Path(pdf_path).exists():
        data = extractor.extract_from_pdf(
            pdf_path=pdf_path,
            company="ATW",
            year=2024,
            report_type=ReportType.PNL,
            quarter=1
        )
        
        print(f"Extracted {len(data.lines)} lines from {pdf_path}")
        for line in data.lines[:5]:  # Show first 5 lines
            print(f"  {line.label}: {line.value} {line.unit}")
    else:
        print(f"PDF file not found: {pdf_path}")

if __name__ == "__main__":
    main() 