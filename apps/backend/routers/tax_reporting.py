from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date, datetime, timedelta
from enum import Enum
import uuid

from pydantic import BaseModel
from utils.auth import get_current_user

router = APIRouter(prefix="/tax-reporting", tags=["tax-reporting"])

class AssetType(str, Enum):
    STOCK = "stock"
    BOND = "bond"
    SUKUK = "sukuk"
    REIT = "reit"
    DIVIDEND = "dividend"
    INTEREST = "interest"

class TaxResidencyStatus(str, Enum):
    RESIDENT = "resident"
    NON_RESIDENT = "non_resident"

class Transaction(BaseModel):
    id: str
    user_id: str
    asset_type: AssetType
    ticker: str
    transaction_type: str  # 'buy', 'sell', 'dividend', 'interest'
    quantity: Decimal
    price: Decimal
    transaction_date: date
    proceeds: Optional[Decimal] = None
    cost_basis: Optional[Decimal] = None
    fees: Decimal = Decimal('0')

class TaxCalculation(BaseModel):
    asset_type: AssetType
    gross_amount: Decimal
    tax_rate: Decimal
    tax_owed: Decimal
    net_amount: Decimal
    description: str

class CapitalGainsTaxReport(BaseModel):
    year: int
    total_gains: Decimal
    total_losses: Decimal
    net_gains: Decimal
    tax_rate: Decimal
    tax_owed: Decimal
    transactions_count: int
    recommendations: List[str]

class DividendTaxReport(BaseModel):
    year: int
    total_dividends: Decimal
    domestic_dividends: Decimal
    foreign_dividends: Decimal
    withholding_tax: Decimal
    net_dividends: Decimal
    tax_rate: Decimal

class MoroccanTaxReport(BaseModel):
    user_id: str
    tax_year: int
    residency_status: TaxResidencyStatus
    capital_gains_report: CapitalGainsTaxReport
    dividend_report: DividendTaxReport
    total_tax_owed: Decimal
    filing_deadline: date
    recommendations: List[str]
    generated_at: datetime

class TaxOptimizationSuggestion(BaseModel):
    suggestion_type: str
    description: str
    potential_savings: Decimal
    action_required: str
    deadline: Optional[date] = None

# Mock data storage
mock_transactions = {}
mock_tax_reports = {}

@router.get("/calculate/{tax_year}", response_model=MoroccanTaxReport)
async def calculate_moroccan_tax(
    tax_year: int,
    residency_status: TaxResidencyStatus = Query(TaxResidencyStatus.RESIDENT),
    current_user = Depends(get_current_user)
):
    """Calculate Moroccan tax obligations for a given year"""
    try:
        # Get user's transactions for the tax year
        user_transactions = get_user_transactions(current_user.id, tax_year)
        
        # Calculate capital gains tax
        capital_gains_report = calculate_capital_gains_tax(user_transactions, residency_status)
        
        # Calculate dividend tax
        dividend_report = calculate_dividend_tax(user_transactions, residency_status)
        
        # Calculate total tax owed
        total_tax_owed = capital_gains_report.tax_owed + dividend_report.withholding_tax
        
        # Generate recommendations
        recommendations = generate_tax_recommendations(capital_gains_report, dividend_report, residency_status)
        
        # Determine filing deadline (March 31st of following year)
        filing_deadline = date(tax_year + 1, 3, 31)
        
        tax_report = MoroccanTaxReport(
            user_id=current_user.id,
            tax_year=tax_year,
            residency_status=residency_status,
            capital_gains_report=capital_gains_report,
            dividend_report=dividend_report,
            total_tax_owed=total_tax_owed,
            filing_deadline=filing_deadline,
            recommendations=recommendations,
            generated_at=datetime.now()
        )
        
        # Store report
        report_id = str(uuid.uuid4())
        mock_tax_reports[report_id] = tax_report
        
        return tax_report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating tax: {str(e)}")

@router.get("/capital-gains/{tax_year}", response_model=CapitalGainsTaxReport)
async def get_capital_gains_report(
    tax_year: int,
    residency_status: TaxResidencyStatus = Query(TaxResidencyStatus.RESIDENT),
    current_user = Depends(get_current_user)
):
    """Get detailed capital gains tax report"""
    try:
        user_transactions = get_user_transactions(current_user.id, tax_year)
        return calculate_capital_gains_tax(user_transactions, residency_status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating capital gains report: {str(e)}")

@router.get("/dividend-tax/{tax_year}", response_model=DividendTaxReport)
async def get_dividend_tax_report(
    tax_year: int,
    residency_status: TaxResidencyStatus = Query(TaxResidencyStatus.RESIDENT),
    current_user = Depends(get_current_user)
):
    """Get detailed dividend tax report"""
    try:
        user_transactions = get_user_transactions(current_user.id, tax_year)
        return calculate_dividend_tax(user_transactions, residency_status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dividend tax report: {str(e)}")

@router.get("/optimization-suggestions", response_model=List[TaxOptimizationSuggestion])
async def get_tax_optimization_suggestions(
    current_user = Depends(get_current_user)
):
    """Get tax optimization suggestions"""
    try:
        current_year = datetime.now().year
        user_transactions = get_user_transactions(current_user.id, current_year)
        
        suggestions = []
        
        # Tax-loss harvesting suggestion
        unrealized_losses = calculate_unrealized_losses(user_transactions)
        if unrealized_losses > 0:
            suggestions.append(TaxOptimizationSuggestion(
                suggestion_type="tax_loss_harvesting",
                description=f"Consider realizing {unrealized_losses} MAD in losses to offset capital gains",
                potential_savings=unrealized_losses * Decimal('0.20'),  # 20% tax rate
                action_required="Sell losing positions before year-end",
                deadline=date(current_year, 12, 31)
            ))
        
        # Dividend timing suggestion
        if datetime.now().month >= 10:  # Q4
            suggestions.append(TaxOptimizationSuggestion(
                suggestion_type="dividend_timing",
                description="Consider dividend-paying stocks for tax-efficient income",
                potential_savings=Decimal('500'),  # Estimated savings
                action_required="Review dividend calendar and tax implications",
                deadline=date(current_year, 12, 31)
            ))
        
        # Sukuk investment suggestion for tax-free income
        suggestions.append(TaxOptimizationSuggestion(
            suggestion_type="sukuk_investment",
            description="Consider Sukuk investments for tax-exempt income under Islamic finance rules",
            potential_savings=Decimal('1000'),  # Estimated savings
            action_required="Evaluate Sukuk investment opportunities",
            deadline=None
        ))
        
        return suggestions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating optimization suggestions: {str(e)}")

@router.get("/tax-brackets", response_model=Dict[str, Any])
async def get_moroccan_tax_brackets(
    tax_year: int = Query(datetime.now().year),
    asset_type: AssetType = Query(AssetType.STOCK)
):
    """Get Moroccan tax brackets and rates"""
    try:
        # Moroccan tax rates (as of 2024)
        tax_brackets = {
            "capital_gains": {
                "stocks": {
                    "rate": 0.20,  # 20% for stocks
                    "description": "Capital gains on stock sales",
                    "exemptions": [
                        "Holdings > 4 years may qualify for reduced rates",
                        "First 40,000 MAD may be exempt (check current rules)"
                    ]
                },
                "bonds": {
                    "rate": 0.15,  # 15% for bonds
                    "description": "Capital gains on bond sales",
                    "exemptions": [
                        "Government bonds may be exempt",
                        "Holding period affects taxation"
                    ]
                },
                "sukuk": {
                    "rate": 0.00,  # Tax-free under Islamic finance
                    "description": "Sukuk gains are typically tax-exempt",
                    "exemptions": [
                        "Sharia-compliant instruments",
                        "Subject to Islamic finance regulations"
                    ]
                }
            },
            "dividends": {
                "domestic": {
                    "rate": 0.15,  # 15% withholding tax
                    "description": "Dividends from Moroccan companies",
                    "exemptions": [
                        "Certain exemptions may apply"
                    ]
                },
                "foreign": {
                    "rate": 0.30,  # 30% withholding tax
                    "description": "Dividends from foreign companies",
                    "exemptions": [
                        "Double taxation treaties may reduce rate"
                    ]
                }
            },
            "interest": {
                "domestic": {
                    "rate": 0.30,  # 30% withholding tax
                    "description": "Interest from Moroccan sources",
                    "exemptions": [
                        "Bank deposits may have different rates"
                    ]
                },
                "foreign": {
                    "rate": 0.30,  # 30% withholding tax
                    "description": "Interest from foreign sources",
                    "exemptions": [
                        "Double taxation treaties may apply"
                    ]
                }
            }
        }
        
        return {
            "tax_year": tax_year,
            "tax_brackets": tax_brackets,
            "important_dates": {
                "tax_year_end": f"{tax_year}-12-31",
                "filing_deadline": f"{tax_year + 1}-03-31",
                "payment_deadline": f"{tax_year + 1}-03-31"
            },
            "disclaimers": [
                "Tax rates may change based on government policy",
                "Consult with a qualified tax advisor for specific situations",
                "Double taxation treaties may affect foreign income taxation"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tax brackets: {str(e)}")

@router.post("/transactions", response_model=Transaction)
async def add_transaction(
    transaction: Transaction,
    current_user = Depends(get_current_user)
):
    """Add a transaction for tax reporting"""
    try:
        transaction.user_id = current_user.id
        transaction.id = str(uuid.uuid4())
        
        # Store transaction
        mock_transactions[transaction.id] = transaction
        
        return transaction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding transaction: {str(e)}")

@router.get("/transactions/{tax_year}", response_model=List[Transaction])
async def get_transactions(
    tax_year: int,
    asset_type: Optional[AssetType] = Query(None),
    current_user = Depends(get_current_user)
):
    """Get user's transactions for a tax year"""
    try:
        user_transactions = get_user_transactions(current_user.id, tax_year)
        
        if asset_type:
            user_transactions = [t for t in user_transactions if t.asset_type == asset_type]
        
        return user_transactions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")

def get_user_transactions(user_id: str, tax_year: int) -> List[Transaction]:
    """Get user's transactions for a specific tax year"""
    user_transactions = [
        t for t in mock_transactions.values()
        if t.user_id == user_id and t.transaction_date.year == tax_year
    ]
    
    # Add mock transactions for demonstration
    if not user_transactions:
        user_transactions = generate_mock_transactions(user_id, tax_year)
    
    return user_transactions

def calculate_capital_gains_tax(transactions: List[Transaction], residency_status: TaxResidencyStatus) -> CapitalGainsTaxReport:
    """Calculate capital gains tax for Moroccan residents"""
    total_gains = Decimal('0')
    total_losses = Decimal('0')
    transactions_count = 0
    
    for transaction in transactions:
        if transaction.transaction_type == 'sell':
            if transaction.proceeds and transaction.cost_basis:
                gain_loss = transaction.proceeds - transaction.cost_basis - transaction.fees
                
                if gain_loss > 0:
                    total_gains += gain_loss
                else:
                    total_losses += abs(gain_loss)
                
                transactions_count += 1
    
    net_gains = total_gains - total_losses
    
    # Apply Moroccan tax rates
    tax_rate = Decimal('0.20')  # 20% for stocks
    if residency_status == TaxResidencyStatus.NON_RESIDENT:
        tax_rate = Decimal('0.30')  # 30% for non-residents
    
    tax_owed = max(Decimal('0'), net_gains * tax_rate)
    
    # Generate recommendations
    recommendations = []
    if total_losses > 0:
        recommendations.append("Consider tax-loss harvesting strategies")
    if net_gains > Decimal('40000'):  # Threshold for higher scrutiny
        recommendations.append("Consider spreading gains across multiple years")
    
    return CapitalGainsTaxReport(
        year=datetime.now().year,
        total_gains=total_gains,
        total_losses=total_losses,
        net_gains=net_gains,
        tax_rate=tax_rate,
        tax_owed=tax_owed,
        transactions_count=transactions_count,
        recommendations=recommendations
    )

def calculate_dividend_tax(transactions: List[Transaction], residency_status: TaxResidencyStatus) -> DividendTaxReport:
    """Calculate dividend tax for Moroccan residents"""
    total_dividends = Decimal('0')
    domestic_dividends = Decimal('0')
    foreign_dividends = Decimal('0')
    
    for transaction in transactions:
        if transaction.transaction_type == 'dividend':
            if transaction.proceeds:
                total_dividends += transaction.proceeds
                
                # Determine if domestic or foreign (simplified)
                if is_domestic_company(transaction.ticker):
                    domestic_dividends += transaction.proceeds
                else:
                    foreign_dividends += transaction.proceeds
    
    # Calculate withholding tax
    domestic_tax_rate = Decimal('0.15')  # 15% for domestic dividends
    foreign_tax_rate = Decimal('0.30')   # 30% for foreign dividends
    
    if residency_status == TaxResidencyStatus.NON_RESIDENT:
        domestic_tax_rate = Decimal('0.30')  # 30% for non-residents
    
    withholding_tax = (domestic_dividends * domestic_tax_rate) + (foreign_dividends * foreign_tax_rate)
    net_dividends = total_dividends - withholding_tax
    
    return DividendTaxReport(
        year=datetime.now().year,
        total_dividends=total_dividends,
        domestic_dividends=domestic_dividends,
        foreign_dividends=foreign_dividends,
        withholding_tax=withholding_tax,
        net_dividends=net_dividends,
        tax_rate=domestic_tax_rate
    )

def calculate_unrealized_losses(transactions: List[Transaction]) -> Decimal:
    """Calculate unrealized losses for tax-loss harvesting"""
    # Mock calculation - in production, this would use current market prices
    return Decimal('5000')  # Mock unrealized losses

def is_domestic_company(ticker: str) -> bool:
    """Check if a company is Moroccan (domestic)"""
    moroccan_tickers = ["ATW", "IAM", "BCP", "BMCE", "OCP", "CMT", "LAFA", "CIH", "MNG", "TMA"]
    return ticker in moroccan_tickers

def generate_tax_recommendations(capital_gains: CapitalGainsTaxReport, dividends: DividendTaxReport, residency_status: TaxResidencyStatus) -> List[str]:
    """Generate tax optimization recommendations"""
    recommendations = []
    
    if capital_gains.net_gains > Decimal('0'):
        recommendations.append("Consider holding assets for longer periods to benefit from potential rate reductions")
    
    if dividends.total_dividends > Decimal('10000'):
        recommendations.append("Consider dividend timing strategies to optimize tax efficiency")
    
    if residency_status == TaxResidencyStatus.NON_RESIDENT:
        recommendations.append("Review double taxation treaties that may reduce your tax burden")
    
    recommendations.append("Consider Sukuk investments for tax-exempt income under Islamic finance rules")
    recommendations.append("Maintain detailed records of all transactions for accurate tax reporting")
    
    return recommendations

def generate_mock_transactions(user_id: str, tax_year: int) -> List[Transaction]:
    """Generate mock transactions for demonstration"""
    transactions = []
    
    # Mock stock transactions
    transactions.append(Transaction(
        id=str(uuid.uuid4()),
        user_id=user_id,
        asset_type=AssetType.STOCK,
        ticker="ATW",
        transaction_type="sell",
        quantity=Decimal('100'),
        price=Decimal('410'),
        transaction_date=date(tax_year, 6, 15),
        proceeds=Decimal('41000'),
        cost_basis=Decimal('38000'),
        fees=Decimal('41')
    ))
    
    # Mock dividend transaction
    transactions.append(Transaction(
        id=str(uuid.uuid4()),
        user_id=user_id,
        asset_type=AssetType.DIVIDEND,
        ticker="IAM",
        transaction_type="dividend",
        quantity=Decimal('50'),
        price=Decimal('25'),
        transaction_date=date(tax_year, 4, 10),
        proceeds=Decimal('1250'),
        cost_basis=None,
        fees=Decimal('0')
    ))
    
    return transactions