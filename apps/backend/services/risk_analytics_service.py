#!/usr/bin/env python3
"""
Risk Analytics Service

Features:
- Portfolio risk metrics calculation
- Watchlist risk analysis
- Stress testing scenarios
- VaR (Value at Risk) calculations
- Correlation analysis
- Sector concentration analysis
- Liquidity risk assessment
- Performance attribution
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

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
        logging.FileHandler('risk_analytics_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class StressTestScenario(Enum):
    MARKET_CRASH = "market_crash"
    INTEREST_RATE_SHOCK = "interest_rate_shock"
    SECTOR_DOWNTURN = "sector_downturn"
    CURRENCY_DEVALUATION = "currency_devaluation"
    LIQUIDITY_CRISIS = "liquidity_crisis"

@dataclass
class RiskMetrics:
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    var_95: float
    var_99: float
    cvar_95: float
    beta: float
    alpha: float
    information_ratio: float
    treynor_ratio: float
    calmar_ratio: float

@dataclass
class ConcentrationRisk:
    largest_position_weight: float
    top_5_positions_weight: float
    sector_concentration: float
    geographic_concentration: float
    risk_level: RiskLevel

@dataclass
class LiquidityRisk:
    average_daily_volume: float
    liquidity_score: float
    days_to_liquidate: float
    bid_ask_spread: float
    risk_level: RiskLevel

@dataclass
class StressTestResult:
    scenario: StressTestScenario
    portfolio_loss: float
    portfolio_loss_percent: float
    worst_affected_positions: List[str]
    recovery_time_days: int
    risk_level: RiskLevel

class RiskAnalyticsService:
    """Comprehensive risk analytics service"""
    
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
        
        # OHLCV data path
        self.ohlcv_path = Path("etl/data/ohlcv")
        
        # Risk-free rate (Morocco 10-year bond yield)
        self.risk_free_rate = 0.035  # 3.5%
        
        # Market data (MASI index)
        self.market_returns = self.load_market_returns()
        
        logger.info("✅ Risk Analytics Service initialized")
    
    def load_market_returns(self) -> pd.Series:
        """Load market returns for beta calculation"""
        try:
            # Mock market returns (in production, load actual MASI data)
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
            np.random.seed(42)  # For reproducible results
            market_returns = pd.Series(
                np.random.normal(0.0005, 0.015, len(dates)),  # 0.05% daily return, 1.5% volatility
                index=dates
            )
            return market_returns
        except Exception as e:
            logger.error(f"Error loading market returns: {e}")
            return pd.Series()
    
    def calculate_portfolio_returns(self, portfolio: Dict) -> pd.Series:
        """Calculate historical portfolio returns"""
        try:
            # This would need historical price data for all positions
            # For now, generate mock returns based on portfolio composition
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
            np.random.seed(42)
            
            # Generate returns based on portfolio weights
            total_value = sum(pos.get('market_value', 0) for pos in portfolio.get('positions', {}).values())
            if total_value == 0:
                return pd.Series()
            
            # Mock returns with some correlation to market
            portfolio_returns = pd.Series(
                np.random.normal(0.0003, 0.012, len(dates)),  # 0.03% daily return, 1.2% volatility
                index=dates
            )
            
            return portfolio_returns
        except Exception as e:
            logger.error(f"Error calculating portfolio returns: {e}")
            return pd.Series()
    
    def calculate_risk_metrics(self, portfolio: Dict) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        try:
            returns = self.calculate_portfolio_returns(portfolio)
            
            if len(returns) < 30:  # Need sufficient data
                return self.get_default_risk_metrics()
            
            # Basic metrics
            volatility = np.std(returns) * np.sqrt(252)  # Annualized
            avg_return = np.mean(returns) * 252  # Annualized
            
            # Risk-adjusted ratios
            sharpe_ratio = (avg_return - self.risk_free_rate) / volatility if volatility > 0 else 0
            
            # Sortino ratio (downside deviation)
            downside_returns = returns[returns < 0]
            downside_deviation = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino_ratio = (avg_return - self.risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
            
            # Maximum drawdown
            cumulative_returns = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdown)
            
            # Value at Risk
            var_95 = np.percentile(returns, 5)
            var_99 = np.percentile(returns, 1)
            
            # Conditional Value at Risk (Expected Shortfall)
            cvar_95 = np.mean(returns[returns <= var_95])
            
            # Beta calculation
            beta = self.calculate_beta(returns)
            
            # Alpha calculation
            alpha = avg_return - (self.risk_free_rate + beta * (np.mean(self.market_returns) * 252 - self.risk_free_rate))
            
            # Information ratio
            tracking_error = np.std(returns - self.market_returns[:len(returns)]) * np.sqrt(252)
            information_ratio = (avg_return - np.mean(self.market_returns) * 252) / tracking_error if tracking_error > 0 else 0
            
            # Treynor ratio
            treynor_ratio = (avg_return - self.risk_free_rate) / beta if beta > 0 else 0
            
            # Calmar ratio
            calmar_ratio = avg_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            return RiskMetrics(
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                max_drawdown=max_drawdown,
                var_95=var_95,
                var_99=var_99,
                cvar_95=cvar_95,
                beta=beta,
                alpha=alpha,
                information_ratio=information_ratio,
                treynor_ratio=treynor_ratio,
                calmar_ratio=calmar_ratio
            )
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return self.get_default_risk_metrics()
    
    def calculate_beta(self, portfolio_returns: pd.Series) -> float:
        """Calculate portfolio beta relative to market"""
        try:
            if len(portfolio_returns) < 30 or len(self.market_returns) < 30:
                return 1.0
            
            # Align returns
            market_returns_aligned = self.market_returns[:len(portfolio_returns)]
            
            # Calculate covariance and variance
            covariance = np.cov(portfolio_returns, market_returns_aligned)[0, 1]
            market_variance = np.var(market_returns_aligned)
            
            beta = covariance / market_variance if market_variance > 0 else 1.0
            return beta
        except Exception as e:
            logger.error(f"Error calculating beta: {e}")
            return 1.0
    
    def get_default_risk_metrics(self) -> RiskMetrics:
        """Return default risk metrics when insufficient data"""
        return RiskMetrics(
            volatility=0.15,
            sharpe_ratio=0.8,
            sortino_ratio=1.2,
            max_drawdown=-0.05,
            var_95=-0.02,
            var_99=-0.03,
            cvar_95=-0.025,
            beta=1.0,
            alpha=0.02,
            information_ratio=0.5,
            treynor_ratio=0.1,
            calmar_ratio=0.3
        )
    
    def calculate_concentration_risk(self, portfolio: Dict) -> ConcentrationRisk:
        """Calculate concentration risk metrics"""
        try:
            positions = portfolio.get('positions', {})
            if not positions:
                return ConcentrationRisk(
                    largest_position_weight=0.0,
                    top_5_positions_weight=0.0,
                    sector_concentration=0.0,
                    geographic_concentration=0.0,
                    risk_level=RiskLevel.LOW
                )
            
            # Calculate position weights
            total_value = sum(pos.get('market_value', 0) for pos in positions.values())
            if total_value == 0:
                return ConcentrationRisk(
                    largest_position_weight=0.0,
                    top_5_positions_weight=0.0,
                    sector_concentration=0.0,
                    geographic_concentration=0.0,
                    risk_level=RiskLevel.LOW
                )
            
            position_weights = []
            sector_weights = {}
            
            for ticker, position in positions.items():
                weight = position.get('market_value', 0) / total_value
                position_weights.append(weight)
                
                # Sector allocation
                sector = self.get_company_sector(ticker)
                sector_weights[sector] = sector_weights.get(sector, 0) + weight
            
            # Calculate concentration metrics
            position_weights.sort(reverse=True)
            largest_position_weight = position_weights[0] if position_weights else 0
            top_5_positions_weight = sum(position_weights[:5])
            
            # Sector concentration (Herfindahl index)
            sector_concentration = sum(weight ** 2 for weight in sector_weights.values())
            
            # Geographic concentration (all Morocco for now)
            geographic_concentration = 1.0  # 100% Morocco
            
            # Determine risk level
            risk_level = self.determine_concentration_risk_level(
                largest_position_weight, top_5_positions_weight, sector_concentration
            )
            
            return ConcentrationRisk(
                largest_position_weight=largest_position_weight,
                top_5_positions_weight=top_5_positions_weight,
                sector_concentration=sector_concentration,
                geographic_concentration=geographic_concentration,
                risk_level=risk_level
            )
        except Exception as e:
            logger.error(f"Error calculating concentration risk: {e}")
            return ConcentrationRisk(
                largest_position_weight=0.0,
                top_5_positions_weight=0.0,
                sector_concentration=0.0,
                geographic_concentration=0.0,
                risk_level=RiskLevel.LOW
            )
    
    def determine_concentration_risk_level(self, largest_weight: float, top5_weight: float, sector_concentration: float) -> RiskLevel:
        """Determine concentration risk level"""
        if largest_weight > 0.25 or top5_weight > 0.8 or sector_concentration > 0.4:
            return RiskLevel.HIGH
        elif largest_weight > 0.15 or top5_weight > 0.6 or sector_concentration > 0.25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def calculate_liquidity_risk(self, portfolio: Dict) -> LiquidityRisk:
        """Calculate liquidity risk metrics"""
        try:
            positions = portfolio.get('positions', {})
            if not positions:
                return LiquidityRisk(
                    average_daily_volume=0.0,
                    liquidity_score=1.0,
                    days_to_liquidate=0.0,
                    bid_ask_spread=0.0,
                    risk_level=RiskLevel.LOW
                )
            
            total_value = sum(pos.get('market_value', 0) for pos in positions.values())
            if total_value == 0:
                return LiquidityRisk(
                    average_daily_volume=0.0,
                    liquidity_score=1.0,
                    days_to_liquidate=0.0,
                    bid_ask_spread=0.0,
                    risk_level=RiskLevel.LOW
                )
            
            # Calculate liquidity metrics
            total_volume = 0
            total_spread = 0
            position_count = 0
            
            for ticker, position in positions.items():
                # Mock liquidity data (in production, get from market data)
                daily_volume = self.get_daily_volume(ticker)
                bid_ask_spread = self.get_bid_ask_spread(ticker)
                
                total_volume += daily_volume
                total_spread += bid_ask_spread
                position_count += 1
            
            average_daily_volume = total_volume / position_count if position_count > 0 else 0
            average_bid_ask_spread = total_spread / position_count if position_count > 0 else 0
            
            # Calculate liquidity score (0-1, higher is more liquid)
            liquidity_score = min(1.0, average_daily_volume / 1000000)  # Normalize to 1M MAD
            
            # Calculate days to liquidate
            days_to_liquidate = total_value / (average_daily_volume * 0.1) if average_daily_volume > 0 else 0
            
            # Determine risk level
            risk_level = self.determine_liquidity_risk_level(liquidity_score, days_to_liquidate, average_bid_ask_spread)
            
            return LiquidityRisk(
                average_daily_volume=average_daily_volume,
                liquidity_score=liquidity_score,
                days_to_liquidate=days_to_liquidate,
                bid_ask_spread=average_bid_ask_spread,
                risk_level=risk_level
            )
        except Exception as e:
            logger.error(f"Error calculating liquidity risk: {e}")
            return LiquidityRisk(
                average_daily_volume=0.0,
                liquidity_score=1.0,
                days_to_liquidate=0.0,
                bid_ask_spread=0.0,
                risk_level=RiskLevel.LOW
            )
    
    def get_daily_volume(self, ticker: str) -> float:
        """Get daily trading volume for a ticker"""
        # Mock implementation
        volume_mapping = {
            'ATW': 1500000,
            'BMCE': 1200000,
            'CIH': 800000,
            'BCP': 2000000,
            'IAM': 1800000,
            'CTM': 900000,
            'MNG': 600000,
            'GAZ': 700000,
            'LES': 500000,
            'WAA': 400000
        }
        return volume_mapping.get(ticker, 500000)
    
    def get_bid_ask_spread(self, ticker: str) -> float:
        """Get bid-ask spread for a ticker"""
        # Mock implementation (as percentage)
        spread_mapping = {
            'ATW': 0.001,  # 0.1%
            'BMCE': 0.0012,
            'CIH': 0.0015,
            'BCP': 0.0008,
            'IAM': 0.001,
            'CTM': 0.0013,
            'MNG': 0.002,
            'GAZ': 0.0018,
            'LES': 0.0025,
            'WAA': 0.003
        }
        return spread_mapping.get(ticker, 0.002)
    
    def determine_liquidity_risk_level(self, liquidity_score: float, days_to_liquidate: float, bid_ask_spread: float) -> RiskLevel:
        """Determine liquidity risk level"""
        if liquidity_score < 0.3 or days_to_liquidate > 10 or bid_ask_spread > 0.005:
            return RiskLevel.HIGH
        elif liquidity_score < 0.6 or days_to_liquidate > 5 or bid_ask_spread > 0.002:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def run_stress_tests(self, portfolio: Dict) -> List[StressTestResult]:
        """Run stress tests on portfolio"""
        try:
            results = []
            
            # Market crash scenario (-20% across all positions)
            market_crash_result = StressTestResult(
                scenario=StressTestScenario.MARKET_CRASH,
                portfolio_loss=portfolio.get('total_value', 0) * -0.20,
                portfolio_loss_percent=-20.0,
                worst_affected_positions=['ATW', 'BMCE', 'CIH'],
                recovery_time_days=180,
                risk_level=RiskLevel.HIGH
            )
            results.append(market_crash_result)
            
            # Interest rate shock (-5% for financial stocks)
            interest_rate_shock_result = StressTestResult(
                scenario=StressTestScenario.INTEREST_RATE_SHOCK,
                portfolio_loss=portfolio.get('total_value', 0) * -0.05,
                portfolio_loss_percent=-5.0,
                worst_affected_positions=['ATW', 'BMCE', 'CIH', 'BCP'],
                recovery_time_days=90,
                risk_level=RiskLevel.MEDIUM
            )
            results.append(interest_rate_shock_result)
            
            # Sector downturn (-15% for specific sectors)
            sector_downturn_result = StressTestResult(
                scenario=StressTestScenario.SECTOR_DOWNTURN,
                portfolio_loss=portfolio.get('total_value', 0) * -0.15,
                portfolio_loss_percent=-15.0,
                worst_affected_positions=['MNG', 'GAZ'],
                recovery_time_days=120,
                risk_level=RiskLevel.MEDIUM
            )
            results.append(sector_downturn_result)
            
            # Currency devaluation (-10% for export-oriented companies)
            currency_devaluation_result = StressTestResult(
                scenario=StressTestScenario.CURRENCY_DEVALUATION,
                portfolio_loss=portfolio.get('total_value', 0) * -0.10,
                portfolio_loss_percent=-10.0,
                worst_affected_positions=['IAM', 'CTM'],
                recovery_time_days=60,
                risk_level=RiskLevel.MEDIUM
            )
            results.append(currency_devaluation_result)
            
            # Liquidity crisis (-25% for illiquid positions)
            liquidity_crisis_result = StressTestResult(
                scenario=StressTestScenario.LIQUIDITY_CRISIS,
                portfolio_loss=portfolio.get('total_value', 0) * -0.25,
                portfolio_loss_percent=-25.0,
                worst_affected_positions=['LES', 'WAA'],
                recovery_time_days=240,
                risk_level=RiskLevel.CRITICAL
            )
            results.append(liquidity_crisis_result)
            
            return results
        except Exception as e:
            logger.error(f"Error running stress tests: {e}")
            return []
    
    def get_company_sector(self, ticker: str) -> str:
        """Get company sector"""
        sector_mapping = {
            'ATW': 'Banking',
            'BMCE': 'Banking',
            'CIH': 'Banking',
            'BCP': 'Banking',
            'IAM': 'Telecommunications',
            'CTM': 'Telecommunications',
            'MNG': 'Mining',
            'GAZ': 'Energy',
            'LES': 'Real Estate',
            'WAA': 'Insurance'
        }
        return sector_mapping.get(ticker, 'Other')
    
    def analyze_watchlist_risk(self, watchlist: List[str]) -> Dict[str, Any]:
        """Analyze risk metrics for a watchlist"""
        try:
            # Calculate watchlist metrics
            sector_allocation = {}
            total_market_cap = 0
            
            for ticker in watchlist:
                sector = self.get_company_sector(ticker)
                market_cap = self.get_market_cap(ticker)
                
                sector_allocation[sector] = sector_allocation.get(sector, 0) + market_cap
                total_market_cap += market_cap
            
            # Calculate sector weights
            sector_weights = {sector: weight / total_market_cap for sector, weight in sector_allocation.items()}
            
            # Calculate concentration metrics
            sector_concentration = sum(weight ** 2 for weight in sector_weights.values())
            
            # Calculate average liquidity
            total_volume = sum(self.get_daily_volume(ticker) for ticker in watchlist)
            average_volume = total_volume / len(watchlist) if watchlist else 0
            
            # Calculate average volatility (mock)
            average_volatility = 0.15  # 15% annualized
            
            return {
                'watchlist_size': len(watchlist),
                'total_market_cap': total_market_cap,
                'sector_allocation': sector_weights,
                'sector_concentration': sector_concentration,
                'average_daily_volume': average_volume,
                'average_volatility': average_volatility,
                'risk_level': self.determine_watchlist_risk_level(sector_concentration, average_volume)
            }
        except Exception as e:
            logger.error(f"Error analyzing watchlist risk: {e}")
            return {}
    
    def get_market_cap(self, ticker: str) -> float:
        """Get market cap for a ticker (in MAD)"""
        # Mock market caps
        market_caps = {
            'ATW': 45000000000,  # 45B MAD
            'BMCE': 28000000000,  # 28B MAD
            'CIH': 15000000000,   # 15B MAD
            'BCP': 35000000000,   # 35B MAD
            'IAM': 65000000000,   # 65B MAD
            'CTM': 25000000000,   # 25B MAD
            'MNG': 12000000000,   # 12B MAD
            'GAZ': 8000000000,    # 8B MAD
            'LES': 5000000000,    # 5B MAD
            'WAA': 3000000000     # 3B MAD
        }
        return market_caps.get(ticker, 1000000000)  # 1B MAD default
    
    def determine_watchlist_risk_level(self, sector_concentration: float, average_volume: float) -> RiskLevel:
        """Determine watchlist risk level"""
        if sector_concentration > 0.4 or average_volume < 500000:
            return RiskLevel.HIGH
        elif sector_concentration > 0.25 or average_volume < 1000000:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def generate_risk_report(self, portfolio: Dict) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        try:
            # Calculate all risk metrics
            risk_metrics = self.calculate_risk_metrics(portfolio)
            concentration_risk = self.calculate_concentration_risk(portfolio)
            liquidity_risk = self.calculate_liquidity_risk(portfolio)
            stress_test_results = self.run_stress_tests(portfolio)
            
            # Overall risk assessment
            overall_risk_level = self.determine_overall_risk_level(
                risk_metrics, concentration_risk, liquidity_risk
            )
            
            return {
                'portfolio_id': portfolio.get('id'),
                'analysis_date': datetime.now().isoformat(),
                'overall_risk_level': overall_risk_level.value,
                'risk_metrics': {
                    'volatility': risk_metrics.volatility,
                    'sharpe_ratio': risk_metrics.sharpe_ratio,
                    'sortino_ratio': risk_metrics.sortino_ratio,
                    'max_drawdown': risk_metrics.max_drawdown,
                    'var_95': risk_metrics.var_95,
                    'var_99': risk_metrics.var_99,
                    'cvar_95': risk_metrics.cvar_95,
                    'beta': risk_metrics.beta,
                    'alpha': risk_metrics.alpha,
                    'information_ratio': risk_metrics.information_ratio,
                    'treynor_ratio': risk_metrics.treynor_ratio,
                    'calmar_ratio': risk_metrics.calmar_ratio
                },
                'concentration_risk': {
                    'largest_position_weight': concentration_risk.largest_position_weight,
                    'top_5_positions_weight': concentration_risk.top_5_positions_weight,
                    'sector_concentration': concentration_risk.sector_concentration,
                    'geographic_concentration': concentration_risk.geographic_concentration,
                    'risk_level': concentration_risk.risk_level.value
                },
                'liquidity_risk': {
                    'average_daily_volume': liquidity_risk.average_daily_volume,
                    'liquidity_score': liquidity_risk.liquidity_score,
                    'days_to_liquidate': liquidity_risk.days_to_liquidate,
                    'bid_ask_spread': liquidity_risk.bid_ask_spread,
                    'risk_level': liquidity_risk.risk_level.value
                },
                'stress_test_results': [
                    {
                        'scenario': result.scenario.value,
                        'portfolio_loss': result.portfolio_loss,
                        'portfolio_loss_percent': result.portfolio_loss_percent,
                        'worst_affected_positions': result.worst_affected_positions,
                        'recovery_time_days': result.recovery_time_days,
                        'risk_level': result.risk_level.value
                    }
                    for result in stress_test_results
                ],
                'recommendations': self.generate_risk_recommendations(
                    risk_metrics, concentration_risk, liquidity_risk
                )
            }
        except Exception as e:
            logger.error(f"Error generating risk report: {e}")
            return {}
    
    def determine_overall_risk_level(self, risk_metrics: RiskMetrics, concentration_risk: ConcentrationRisk, liquidity_risk: LiquidityRisk) -> RiskLevel:
        """Determine overall portfolio risk level"""
        risk_scores = []
        
        # Volatility score
        if risk_metrics.volatility > 0.25:
            risk_scores.append(3)  # High
        elif risk_metrics.volatility > 0.15:
            risk_scores.append(2)  # Medium
        else:
            risk_scores.append(1)  # Low
        
        # Concentration score
        if concentration_risk.risk_level == RiskLevel.HIGH:
            risk_scores.append(3)
        elif concentration_risk.risk_level == RiskLevel.MEDIUM:
            risk_scores.append(2)
        else:
            risk_scores.append(1)
        
        # Liquidity score
        if liquidity_risk.risk_level == RiskLevel.HIGH:
            risk_scores.append(3)
        elif liquidity_risk.risk_level == RiskLevel.MEDIUM:
            risk_scores.append(2)
        else:
            risk_scores.append(1)
        
        # Calculate average risk score
        avg_score = sum(risk_scores) / len(risk_scores)
        
        if avg_score >= 2.5:
            return RiskLevel.HIGH
        elif avg_score >= 1.5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def generate_risk_recommendations(self, risk_metrics: RiskMetrics, concentration_risk: ConcentrationRisk, liquidity_risk: LiquidityRisk) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        # Volatility recommendations
        if risk_metrics.volatility > 0.25:
            recommendations.append("Consider reducing portfolio volatility through diversification")
        
        # Concentration recommendations
        if concentration_risk.largest_position_weight > 0.20:
            recommendations.append("Reduce concentration in largest position")
        if concentration_risk.sector_concentration > 0.30:
            recommendations.append("Diversify across more sectors")
        
        # Liquidity recommendations
        if liquidity_risk.days_to_liquidate > 5:
            recommendations.append("Consider more liquid positions for better exit flexibility")
        
        # Risk-adjusted return recommendations
        if risk_metrics.sharpe_ratio < 0.5:
            recommendations.append("Consider strategies to improve risk-adjusted returns")
        
        if not recommendations:
            recommendations.append("Portfolio risk profile appears well-balanced")
        
        return recommendations

# Initialize service
risk_analytics_service = RiskAnalyticsService() 