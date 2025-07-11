from typing import Dict, Optional, List
import logging
from dataclasses import dataclass

from models.financials import GAAPFinancialData, ReportType

logger = logging.getLogger(__name__)

@dataclass
class FinancialRatios:
    """Container for computed financial ratios"""
    # Profitability ratios
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    
    # Liquidity ratios
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None
    
    # Solvency ratios
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    interest_coverage: Optional[float] = None
    
    # Efficiency ratios
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None

class RatioCalculator:
    """Calculates financial ratios from GAAP financial data"""
    
    def __init__(self):
        self.ratio_definitions = {
            # Profitability ratios
            "gross_margin": {
                "formula": "gross_profit / revenue",
                "description": "Gross profit margin percentage"
            },
            "operating_margin": {
                "formula": "operating_income / revenue",
                "description": "Operating profit margin percentage"
            },
            "net_margin": {
                "formula": "net_income / revenue",
                "description": "Net profit margin percentage"
            },
            "roe": {
                "formula": "net_income / shareholders_equity",
                "description": "Return on equity"
            },
            "roa": {
                "formula": "net_income / total_assets",
                "description": "Return on assets"
            },
            
            # Liquidity ratios
            "current_ratio": {
                "formula": "current_assets / current_liabilities",
                "description": "Current ratio"
            },
            "quick_ratio": {
                "formula": "(current_assets - inventory) / current_liabilities",
                "description": "Quick ratio (acid test)"
            },
            "cash_ratio": {
                "formula": "cash_and_cash_equivalents / current_liabilities",
                "description": "Cash ratio"
            },
            
            # Solvency ratios
            "debt_to_equity": {
                "formula": "total_debt / shareholders_equity",
                "description": "Debt to equity ratio"
            },
            "debt_to_assets": {
                "formula": "total_debt / total_assets",
                "description": "Debt to assets ratio"
            },
            "interest_coverage": {
                "formula": "operating_income / interest_expense",
                "description": "Interest coverage ratio"
            },
            
            # Efficiency ratios
            "asset_turnover": {
                "formula": "revenue / total_assets",
                "description": "Asset turnover ratio"
            },
            "inventory_turnover": {
                "formula": "cost_of_goods_sold / inventory",
                "description": "Inventory turnover ratio"
            },
            "receivables_turnover": {
                "formula": "revenue / accounts_receivable",
                "description": "Receivables turnover ratio"
            }
        }
    
    def compute_ratios(self, gaap_data: GAAPFinancialData) -> Dict[str, float]:
        """Compute financial ratios from GAAP data"""
        ratios = {}
        
        try:
            if gaap_data.report_type == ReportType.PNL:
                ratios.update(self._compute_profitability_ratios(gaap_data.data))
            elif gaap_data.report_type == ReportType.BALANCE:
                ratios.update(self._compute_balance_sheet_ratios(gaap_data.data))
            
            # Some ratios require both P&L and balance sheet data
            # In a real implementation, you'd need to combine data from multiple reports
            
        except Exception as e:
            logger.error(f"Error computing ratios for {gaap_data.company}: {e}")
        
        return ratios
    
    def _compute_profitability_ratios(self, data: Dict[str, float]) -> Dict[str, float]:
        """Compute profitability ratios from P&L data"""
        ratios = {}
        
        revenue = data.get('Revenue', 0)
        gross_profit = data.get('Gross Profit', 0)
        operating_income = data.get('Operating Income', 0)
        net_income = data.get('Net Income', 0)
        
        if revenue and revenue > 0:
            if gross_profit:
                ratios['gross_margin'] = (gross_profit / revenue) * 100
            
            if operating_income:
                ratios['operating_margin'] = (operating_income / revenue) * 100
            
            if net_income:
                ratios['net_margin'] = (net_income / revenue) * 100
        
        return ratios
    
    def _compute_balance_sheet_ratios(self, data: Dict[str, float]) -> Dict[str, float]:
        """Compute balance sheet ratios"""
        ratios = {}
        
        current_assets = data.get('Current Assets', 0)
        current_liabilities = data.get('Current Liabilities', 0)
        inventory = data.get('Inventory', 0)
        cash = data.get('Cash and Cash Equivalents', 0)
        total_assets = data.get('Total Assets', 0)
        shareholders_equity = data.get('Shareholders Equity', 0)
        total_debt = data.get('Total Debt', 0)
        
        # Liquidity ratios
        if current_liabilities and current_liabilities > 0:
            if current_assets:
                ratios['current_ratio'] = current_assets / current_liabilities
            
            if current_assets and inventory:
                ratios['quick_ratio'] = (current_assets - inventory) / current_liabilities
            
            if cash:
                ratios['cash_ratio'] = cash / current_liabilities
        
        # Solvency ratios
        if shareholders_equity and shareholders_equity > 0:
            if total_debt:
                ratios['debt_to_equity'] = total_debt / shareholders_equity
        
        if total_assets and total_assets > 0:
            if total_debt:
                ratios['debt_to_assets'] = total_debt / total_assets
        
        return ratios
    
    def compute_combined_ratios(self, pnl_data: GAAPFinancialData, 
                              balance_data: GAAPFinancialData) -> Dict[str, float]:
        """Compute ratios that require both P&L and balance sheet data"""
        ratios = {}
        
        try:
            # ROE and ROA require both P&L and balance sheet
            net_income = pnl_data.data.get('Net Income', 0)
            total_assets = balance_data.data.get('Total Assets', 0)
            shareholders_equity = balance_data.data.get('Shareholders Equity', 0)
            revenue = pnl_data.data.get('Revenue', 0)
            
            if net_income and shareholders_equity and shareholders_equity > 0:
                ratios['roe'] = (net_income / shareholders_equity) * 100
            
            if net_income and total_assets and total_assets > 0:
                ratios['roa'] = (net_income / total_assets) * 100
            
            if revenue and total_assets and total_assets > 0:
                ratios['asset_turnover'] = revenue / total_assets
            
            # Interest coverage
            operating_income = pnl_data.data.get('Operating Income', 0)
            interest_expense = pnl_data.data.get('Interest Expense', 0)
            
            if operating_income and interest_expense and interest_expense > 0:
                ratios['interest_coverage'] = operating_income / interest_expense
            
        except Exception as e:
            logger.error(f"Error computing combined ratios: {e}")
        
        return ratios
    
    def get_ratio_definition(self, ratio_name: str) -> Optional[Dict[str, str]]:
        """Get the definition and formula for a specific ratio"""
        return self.ratio_definitions.get(ratio_name)
    
    def list_available_ratios(self) -> List[str]:
        """List all available ratios"""
        return list(self.ratio_definitions.keys())
    
    def validate_ratio(self, ratio_name: str, value: float) -> bool:
        """Validate if a ratio value makes sense"""
        validation_rules = {
            'gross_margin': lambda x: 0 <= x <= 100,
            'operating_margin': lambda x: -100 <= x <= 100,
            'net_margin': lambda x: -100 <= x <= 100,
            'roe': lambda x: -1000 <= x <= 1000,
            'roa': lambda x: -100 <= x <= 100,
            'current_ratio': lambda x: x >= 0,
            'quick_ratio': lambda x: x >= 0,
            'cash_ratio': lambda x: x >= 0,
            'debt_to_equity': lambda x: x >= 0,
            'debt_to_assets': lambda x: 0 <= x <= 1,
            'interest_coverage': lambda x: x >= 0,
            'asset_turnover': lambda x: x >= 0,
            'inventory_turnover': lambda x: x >= 0,
            'receivables_turnover': lambda x: x >= 0,
        }
        
        validator = validation_rules.get(ratio_name)
        if validator:
            return validator(value)
        
        return True  # Default to valid if no specific rule
    
    def format_ratio(self, ratio_name: str, value: float) -> str:
        """Format ratio value for display"""
        if value is None:
            return "N/A"
        
        # Percentages
        percentage_ratios = ['gross_margin', 'operating_margin', 'net_margin', 'roe', 'roa']
        if ratio_name in percentage_ratios:
            return f"{value:.2f}%"
        
        # Multipliers
        multiplier_ratios = ['current_ratio', 'quick_ratio', 'cash_ratio', 'debt_to_equity', 
                           'debt_to_assets', 'interest_coverage', 'asset_turnover', 
                           'inventory_turnover', 'receivables_turnover']
        if ratio_name in multiplier_ratios:
            return f"{value:.2f}x"
        
        return f"{value:.2f}"
    
    def get_ratio_category(self, ratio_name: str) -> str:
        """Get the category of a ratio"""
        categories = {
            'profitability': ['gross_margin', 'operating_margin', 'net_margin', 'roe', 'roa'],
            'liquidity': ['current_ratio', 'quick_ratio', 'cash_ratio'],
            'solvency': ['debt_to_equity', 'debt_to_assets', 'interest_coverage'],
            'efficiency': ['asset_turnover', 'inventory_turnover', 'receivables_turnover']
        }
        
        for category, ratios in categories.items():
            if ratio_name in ratios:
                return category
        
        return 'other'

# Example usage
def main():
    """Example usage of the Ratio Calculator"""
    calculator = RatioCalculator()
    
    # Example P&L data
    pnl_data = GAAPFinancialData(
        company="ATW",
        year=2024,
        quarter=1,
        report_type=ReportType.PNL,
        data={
            'Revenue': 13940000000,
            'Gross Profit': 8500000000,
            'Operating Income': 3600000000,
            'Net Income': 2800000000,
            'Interest Expense': 150000000
        }
    )
    
    # Example balance sheet data
    balance_data = GAAPFinancialData(
        company="ATW",
        year=2024,
        quarter=1,
        report_type=ReportType.BALANCE,
        data={
            'Total Assets': 45000000000,
            'Current Assets': 12000000000,
            'Current Liabilities': 8000000000,
            'Inventory': 2000000000,
            'Cash and Cash Equivalents': 3000000000,
            'Shareholders Equity': 25000000000,
            'Total Debt': 12000000000
        }
    )
    
    # Compute ratios
    pnl_ratios = calculator.compute_ratios(pnl_data)
    balance_ratios = calculator.compute_ratios(balance_data)
    combined_ratios = calculator.compute_combined_ratios(pnl_data, balance_data)
    
    print("Profitability Ratios:")
    for ratio, value in pnl_ratios.items():
        formatted = calculator.format_ratio(ratio, value)
        print(f"  {ratio}: {formatted}")
    
    print("\nBalance Sheet Ratios:")
    for ratio, value in balance_ratios.items():
        formatted = calculator.format_ratio(ratio, value)
        print(f"  {ratio}: {formatted}")
    
    print("\nCombined Ratios:")
    for ratio, value in combined_ratios.items():
        formatted = calculator.format_ratio(ratio, value)
        print(f"  {ratio}: {formatted}")

if __name__ == "__main__":
    main() 