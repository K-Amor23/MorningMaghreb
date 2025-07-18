#!/usr/bin/env python3
"""
Mock Data Generator for Casablanca Insights ETL Pipeline

This module generates realistic mock financial data for testing the pipeline
when real IR websites are not accessible.
"""

import json
import random
from datetime import datetime, date
from typing import List, Dict, Optional
from pathlib import Path
import csv
from decimal import Decimal

class MockDataGenerator:
    """Generates mock financial data for testing"""
    
    def __init__(self):
        self.companies = [
            {"ticker": "ATW", "name": "Attijariwafa Bank", "sector": "Banking"},
            {"ticker": "IAM", "name": "Maroc Telecom", "sector": "Telecommunications"},
            {"ticker": "BCP", "name": "Banque Centrale Populaire", "sector": "Banking"},
            {"ticker": "BMCE", "name": "BMCE Bank", "sector": "Banking"},
            {"ticker": "CIH", "name": "CIH Bank", "sector": "Banking"},
            {"ticker": "WAA", "name": "Wafa Assurance", "sector": "Insurance"},
            {"ticker": "LBV", "name": "Label'Vie", "sector": "Distribution"},
            {"ticker": "TMA", "name": "Taqa Morocco", "sector": "Energy"},
            {"ticker": "ADH", "name": "Addoha", "sector": "Real Estate"},
            {"ticker": "LES", "name": "Lesieur Cristal", "sector": "Food & Beverage"}
        ]
        
        # Financial statement templates
        self.pnl_template = [
            "Revenus nets",
            "Chiffre d'affaires",
            "Coût des ventes",
            "Marge brute",
            "Charges d'exploitation",
            "Résultat d'exploitation",
            "Charges financières",
            "Produits financiers",
            "Résultat avant impôts",
            "Impôts sur les bénéfices",
            "Résultat net"
        ]
        
        self.balance_template = [
            "Actifs immobilisés",
            "Immobilisations incorporelles",
            "Immobilisations corporelles",
            "Immobilisations financières",
            "Actifs circulants",
            "Stocks",
            "Créances clients",
            "Trésorerie",
            "Total Actif",
            "Capitaux propres",
            "Capital social",
            "Réserves",
            "Résultat de l'exercice",
            "Dettes long terme",
            "Dettes court terme",
            "Total Passif"
        ]
        
        self.cashflow_template = [
            "Flux de trésorerie d'exploitation",
            "Résultat net",
            "Amortissements",
            "Variation du BFR",
            "Flux de trésorerie d'investissement",
            "Acquisitions d'immobilisations",
            "Cessions d'immobilisations",
            "Flux de trésorerie de financement",
            "Émission d'emprunts",
            "Remboursement d'emprunts",
            "Dividendes versés",
            "Variation nette de trésorerie"
        ]
    
    def generate_mock_reports(self, companies: List[str], year: int = 2024) -> List[Dict]:
        """Generate mock IR reports for specified companies"""
        reports = []
        
        for company in companies:
            company_info = next((c for c in self.companies if c["ticker"] == company), None)
            if not company_info:
                continue
                
            # Generate annual reports
            for report_type in ["pnl", "balance", "cashflow"]:
                report = {
                    "company": company,
                    "year": year,
                    "quarter": None,
                    "report_type": report_type,
                    "title": f"{company_info['name']} - {report_type.upper()} {year}",
                    "url": f"https://mock-ir.com/{company}/{report_type}_{year}.pdf",
                    "filename": f"{company}_{report_type}_{year}.pdf"
                }
                reports.append(report)
                
            # Generate quarterly reports (Q1-Q3)
            for quarter in [1, 2, 3]:
                report = {
                    "company": company,
                    "year": year,
                    "quarter": quarter,
                    "report_type": "pnl",
                    "title": f"{company_info['name']} - Q{quarter} {year}",
                    "url": f"https://mock-ir.com/{company}/Q{quarter}_{year}.pdf",
                    "filename": f"{company}_Q{quarter}_{year}.pdf"
                }
                reports.append(report)
        
        return reports
    
    def generate_mock_financial_data(self, company: str, year: int, report_type: str) -> Dict:
        """Generate mock financial data for a company"""
        company_info = next((c for c in self.companies if c["ticker"] == company), None)
        if not company_info:
            return {}
        
        # Base multipliers by sector
        sector_multipliers = {
            "Banking": 10000000000,  # 10B MAD
            "Telecommunications": 5000000000,  # 5B MAD
            "Insurance": 3000000000,  # 3B MAD
            "Distribution": 2000000000,  # 2B MAD
            "Energy": 4000000000,  # 4B MAD
            "Real Estate": 1000000000,  # 1B MAD
            "Food & Beverage": 1500000000  # 1.5B MAD
        }
        
        base_multiplier = sector_multipliers.get(company_info["sector"], 1000000000)
        
        # Generate financial lines based on report type
        if report_type == "pnl":
            lines = self._generate_pnl_lines(base_multiplier)
        elif report_type == "balance":
            lines = self._generate_balance_lines(base_multiplier)
        elif report_type == "cashflow":
            lines = self._generate_cashflow_lines(base_multiplier)
        else:
            lines = []
        
        return {
            "company": company,
            "year": year,
            "quarter": None,
            "report_type": report_type,
            "language": "fr",
            "lines": lines,
            "extraction_metadata": {
                "method": "mock_generation",
                "confidence": 1.0,
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def _generate_pnl_lines(self, base_multiplier: float) -> List[Dict]:
        """Generate P&L statement lines"""
        lines = []
        
        # Revenue
        revenue = base_multiplier * random.uniform(0.8, 1.2)
        lines.append({
            "label": "Revenus nets",
            "value": revenue,
            "unit": "MAD",
            "category": "revenue",
            "confidence": 0.95
        })
        
        # Cost of sales (60-80% of revenue)
        cost_of_sales = revenue * random.uniform(0.6, 0.8)
        lines.append({
            "label": "Coût des ventes",
            "value": cost_of_sales,
            "unit": "MAD",
            "category": "expense",
            "confidence": 0.95
        })
        
        # Gross margin
        gross_margin = revenue - cost_of_sales
        lines.append({
            "label": "Marge brute",
            "value": gross_margin,
            "unit": "MAD",
            "category": "margin",
            "confidence": 0.95
        })
        
        # Operating expenses (15-25% of revenue)
        operating_expenses = revenue * random.uniform(0.15, 0.25)
        lines.append({
            "label": "Charges d'exploitation",
            "value": operating_expenses,
            "unit": "MAD",
            "category": "expense",
            "confidence": 0.95
        })
        
        # Operating result
        operating_result = gross_margin - operating_expenses
        lines.append({
            "label": "Résultat d'exploitation",
            "value": operating_result,
            "unit": "MAD",
            "category": "result",
            "confidence": 0.95
        })
        
        # Financial charges (2-5% of revenue)
        financial_charges = revenue * random.uniform(0.02, 0.05)
        lines.append({
            "label": "Charges financières",
            "value": financial_charges,
            "unit": "MAD",
            "category": "expense",
            "confidence": 0.95
        })
        
        # Net result
        net_result = operating_result - financial_charges
        lines.append({
            "label": "Résultat net",
            "value": net_result,
            "unit": "MAD",
            "category": "result",
            "confidence": 0.95
        })
        
        return lines
    
    def _generate_balance_lines(self, base_multiplier: float) -> List[Dict]:
        """Generate balance sheet lines"""
        lines = []
        
        # Total assets
        total_assets = base_multiplier * random.uniform(1.5, 2.0)
        
        # Fixed assets (40-60% of total)
        fixed_assets = total_assets * random.uniform(0.4, 0.6)
        lines.append({
            "label": "Actifs immobilisés",
            "value": fixed_assets,
            "unit": "MAD",
            "category": "asset",
            "confidence": 0.95
        })
        
        # Current assets
        current_assets = total_assets - fixed_assets
        lines.append({
            "label": "Actifs circulants",
            "value": current_assets,
            "unit": "MAD",
            "category": "asset",
            "confidence": 0.95
        })
        
        # Cash (10-20% of current assets)
        cash = current_assets * random.uniform(0.1, 0.2)
        lines.append({
            "label": "Trésorerie",
            "value": cash,
            "unit": "MAD",
            "category": "asset",
            "confidence": 0.95
        })
        
        # Total assets
        lines.append({
            "label": "Total Actif",
            "value": total_assets,
            "unit": "MAD",
            "category": "total",
            "confidence": 0.95
        })
        
        # Equity (30-50% of total assets)
        equity = total_assets * random.uniform(0.3, 0.5)
        lines.append({
            "label": "Capitaux propres",
            "value": equity,
            "unit": "MAD",
            "category": "equity",
            "confidence": 0.95
        })
        
        # Total liabilities
        total_liabilities = total_assets - equity
        lines.append({
            "label": "Total Passif",
            "value": total_assets,
            "unit": "MAD",
            "category": "total",
            "confidence": 0.95
        })
        
        return lines
    
    def _generate_cashflow_lines(self, base_multiplier: float) -> List[Dict]:
        """Generate cash flow statement lines"""
        lines = []
        
        # Operating cash flow
        operating_cf = base_multiplier * random.uniform(0.1, 0.3)
        lines.append({
            "label": "Flux de trésorerie d'exploitation",
            "value": operating_cf,
            "unit": "MAD",
            "category": "cash_flow",
            "confidence": 0.95
        })
        
        # Investment cash flow (usually negative)
        investment_cf = -base_multiplier * random.uniform(0.05, 0.15)
        lines.append({
            "label": "Flux de trésorerie d'investissement",
            "value": investment_cf,
            "unit": "MAD",
            "category": "cash_flow",
            "confidence": 0.95
        })
        
        # Financing cash flow
        financing_cf = base_multiplier * random.uniform(-0.1, 0.1)
        lines.append({
            "label": "Flux de trésorerie de financement",
            "value": financing_cf,
            "unit": "MAD",
            "category": "cash_flow",
            "confidence": 0.95
        })
        
        # Net cash flow
        net_cf = operating_cf + investment_cf + financing_cf
        lines.append({
            "label": "Variation nette de trésorerie",
            "value": net_cf,
            "unit": "MAD",
            "category": "cash_flow",
            "confidence": 0.95
        })
        
        return lines
    
    def save_mock_data(self, output_dir: str = "data/mock"):
        """Save mock data to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate mock reports
        all_reports = self.generate_mock_reports([c["ticker"] for c in self.companies])
        
        # Save reports metadata
        with open(output_path / "mock_reports.json", "w", encoding="utf-8") as f:
            json.dump(all_reports, f, indent=2, ensure_ascii=False, default=str)
        
        # Generate and save financial data
        financial_data = []
        for company in self.companies:
            for report_type in ["pnl", "balance", "cashflow"]:
                data = self.generate_mock_financial_data(company["ticker"], 2024, report_type)
                financial_data.append(data)
        
        with open(output_path / "mock_financial_data.json", "w", encoding="utf-8") as f:
            json.dump(financial_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Mock data saved to {output_path}")
        print(f"  • Reports: {len(all_reports)}")
        print(f"  • Financial datasets: {len(financial_data)}")
        
        return {
            "reports": all_reports,
            "financial_data": financial_data,
            "output_path": str(output_path)
        }

if __name__ == "__main__":
    generator = MockDataGenerator()
    result = generator.save_mock_data()
    print(f"\n🎯 Mock data generation complete!")
    print(f"📊 Generated {len(result['reports'])} mock reports")
    print(f"💰 Generated {len(result['financial_data'])} financial datasets") 