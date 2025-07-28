"""
Premium Analytics Service
Handles ML-based signals, portfolio optimization, and predictive models
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from models.premium_analytics import (
    MLModel, MLPrediction, PortfolioOptimization
)
from models.market_data import Quote, Company

logger = logging.getLogger(__name__)


class PremiumAnalyticsService:
    """Service for premium analytics and ML-based signals"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================================
    # ML MODEL MANAGEMENT
    # ============================================================================
    
    async def create_ml_model(
        self,
        model_name: str,
        model_type: str,
        version: str,
        hyperparameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new ML model"""
        try:
            model = MLModel(
                model_name=model_name,
                model_type=model_type,
                version=version,
                hyperparameters=hyperparameters or {}
            )
            self.db.add(model)
            self.db.commit()
            
            return {
                "success": True,
                "model_id": str(model.id),
                "message": "ML model created successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating ML model: {e}")
            raise HTTPException(status_code=500, detail="Failed to create ML model")
    
    async def update_model_status(
        self, 
        model_id: str, 
        status: str, 
        accuracy_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """Update ML model status"""
        try:
            model = self.db.query(MLModel).filter(MLModel.id == model_id).first()
            if not model:
                raise HTTPException(status_code=404, detail="Model not found")
            
            model.status = status
            if accuracy_score is not None:
                model.accuracy_score = accuracy_score
            model.last_trained = datetime.now()
            model.updated_at = datetime.now()
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Model status updated successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating model status: {e}")
            raise HTTPException(status_code=500, detail="Failed to update model status")
    
    async def get_active_models(self, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active ML models"""
        try:
            query = self.db.query(MLModel).filter(MLModel.status == "active")
            if model_type:
                query = query.filter(MLModel.model_type == model_type)
            
            models = query.all()
            
            model_data = []
            for model in models:
                model_data.append({
                    "id": str(model.id),
                    "name": model.model_name,
                    "type": model.model_type,
                    "version": model.version,
                    "accuracy_score": float(model.accuracy_score) if model.accuracy_score else None,
                    "last_trained": model.last_trained.isoformat() if model.last_trained else None
                })
            
            return model_data
            
        except Exception as e:
            logger.error(f"Error getting active models: {e}")
            raise HTTPException(status_code=500, detail="Failed to get active models")
    
    # ============================================================================
    # PREDICTIVE MODELS
    # ============================================================================
    
    async def generate_price_prediction(
        self,
        ticker: str,
        prediction_horizon: int = 30,
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Generate price prediction for a ticker"""
        try:
            # Get historical data
            historical_data = await self._get_historical_data(ticker, days=365)
            if not historical_data:
                raise HTTPException(status_code=404, detail="No historical data available")
            
            # Simple moving average prediction (replace with actual ML model)
            prices = [float(quote['close']) for quote in historical_data]
            current_price = prices[-1]
            
            # Calculate technical indicators
            sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else current_price
            sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else current_price
            
            # Simple trend prediction
            trend = (sma_20 - sma_50) / sma_50
            volatility = np.std(prices[-30:]) / current_price if len(prices) >= 30 else 0.02
            
            # Generate prediction
            predicted_return = trend * 0.5  # Conservative prediction
            predicted_price = current_price * (1 + predicted_return)
            
            # Calculate confidence based on volatility and trend strength
            confidence = max(0.5, min(0.95, 1 - volatility * 10))
            
            if confidence < confidence_threshold:
                raise HTTPException(status_code=400, detail="Confidence too low for reliable prediction")
            
            # Store prediction
            prediction = MLPrediction(
                model_id=None,  # Will be set when ML model is available
                ticker=ticker,
                prediction_type="price_target",
                predicted_value=Decimal(str(predicted_price)),
                confidence_score=Decimal(str(confidence)),
                prediction_horizon=prediction_horizon,
                prediction_date=datetime.now().date(),
                features_used={
                    "sma_20": float(sma_20),
                    "sma_50": float(sma_50),
                    "trend": float(trend),
                    "volatility": float(volatility)
                }
            )
            self.db.add(prediction)
            self.db.commit()
            
            return {
                "ticker": ticker,
                "current_price": current_price,
                "predicted_price": float(predicted_price),
                "predicted_return": float(predicted_return),
                "confidence": float(confidence),
                "horizon_days": prediction_horizon,
                "prediction_id": str(prediction.id)
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating price prediction: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate prediction")
    
    async def generate_volatility_forecast(
        self,
        ticker: str,
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """Generate volatility forecast for a ticker"""
        try:
            # Get historical data
            historical_data = await self._get_historical_data(ticker, days=90)
            if not historical_data:
                raise HTTPException(status_code=404, detail="No historical data available")
            
            # Calculate historical volatility
            returns = []
            for i in range(1, len(historical_data)):
                prev_close = float(historical_data[i-1]['close'])
                curr_close = float(historical_data[i]['close'])
                returns.append((curr_close - prev_close) / prev_close)
            
            current_volatility = np.std(returns) * np.sqrt(252)  # Annualized
            
            # Simple volatility forecast (GARCH-like)
            recent_volatility = np.std(returns[-20:]) * np.sqrt(252) if len(returns) >= 20 else current_volatility
            forecast_volatility = recent_volatility * 1.1  # Slight increase assumption
            
            # Store prediction
            prediction = MLPrediction(
                model_id=None,
                ticker=ticker,
                prediction_type="volatility",
                predicted_value=Decimal(str(forecast_volatility)),
                confidence_score=Decimal("0.75"),
                prediction_horizon=forecast_days,
                prediction_date=datetime.now().date(),
                features_used={
                    "current_volatility": float(current_volatility),
                    "recent_volatility": float(recent_volatility),
                    "returns_count": len(returns)
                }
            )
            self.db.add(prediction)
            self.db.commit()
            
            return {
                "ticker": ticker,
                "current_volatility": float(current_volatility),
                "forecast_volatility": float(forecast_volatility),
                "confidence": 0.75,
                "forecast_days": forecast_days,
                "prediction_id": str(prediction.id)
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating volatility forecast: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate volatility forecast")
    
    # ============================================================================
    # PORTFOLIO OPTIMIZATION
    # ============================================================================
    
    async def optimize_portfolio_markowitz(
        self,
        user_id: str,
        tickers: List[str],
        target_return: Optional[float] = None,
        risk_tolerance: float = 0.5,
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Optimize portfolio using Markowitz mean-variance optimization"""
        try:
            # Get historical data for all tickers
            returns_data = {}
            for ticker in tickers:
                historical_data = await self._get_historical_data(ticker, days=252)
                if historical_data:
                    prices = [float(quote['close']) for quote in historical_data]
                    returns = []
                    for i in range(1, len(prices)):
                        returns.append((prices[i] - prices[i-1]) / prices[i-1])
                    returns_data[ticker] = returns
            
            if len(returns_data) < 2:
                raise HTTPException(status_code=400, detail="Need at least 2 assets for optimization")
            
            # Calculate expected returns and covariance matrix
            expected_returns = {}
            returns_matrix = []
            
            for ticker, returns in returns_data.items():
                expected_returns[ticker] = np.mean(returns) * 252  # Annualized
                returns_matrix.append(returns)
            
            # Pad shorter return series with zeros
            max_length = max(len(returns) for returns in returns_matrix)
            padded_returns = []
            for returns in returns_matrix:
                padded = returns + [0] * (max_length - len(returns))
                padded_returns.append(padded)
            
            covariance_matrix = np.cov(padded_returns) * 252  # Annualized
            
            # Optimization function
            def portfolio_variance(weights):
                return np.dot(weights.T, np.dot(covariance_matrix, weights))
            
            def portfolio_return(weights):
                return np.sum([weights[i] * expected_returns[ticker] 
                             for i, ticker in enumerate(returns_data.keys())])
            
            # Constraints
            n_assets = len(tickers)
            constraints_list = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
            ]
            
            if target_return is not None:
                constraints_list.append({
                    'type': 'eq', 
                    'fun': lambda x: portfolio_return(x) - target_return
                })
            
            # Bounds (no short selling)
            bounds = [(0, 1) for _ in range(n_assets)]
            
            # Initial guess (equal weights)
            initial_weights = np.array([1/n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                portfolio_variance,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list
            )
            
            if not result.success:
                raise HTTPException(status_code=400, detail="Optimization failed")
            
            optimal_weights = result.x
            optimal_weights_dict = {ticker: float(weight) for ticker, weight in zip(tickers, optimal_weights)}
            
            # Calculate portfolio metrics
            expected_portfolio_return = portfolio_return(optimal_weights)
            expected_portfolio_volatility = np.sqrt(portfolio_variance(optimal_weights))
            sharpe_ratio = expected_portfolio_return / expected_portfolio_volatility if expected_portfolio_volatility > 0 else 0
            
            # Store optimization result
            optimization = PortfolioOptimization(
                user_id=user_id,
                optimization_type="markowitz",
                target_return=Decimal(str(target_return)) if target_return else None,
                risk_tolerance=Decimal(str(risk_tolerance)),
                constraints=constraints or {},
                optimal_weights=optimal_weights_dict,
                expected_return=Decimal(str(expected_portfolio_return)),
                expected_volatility=Decimal(str(expected_portfolio_volatility)),
                sharpe_ratio=Decimal(str(sharpe_ratio))
            )
            self.db.add(optimization)
            self.db.commit()
            
            return {
                "optimization_id": str(optimization.id),
                "optimal_weights": optimal_weights_dict,
                "expected_return": float(expected_portfolio_return),
                "expected_volatility": float(expected_portfolio_volatility),
                "sharpe_ratio": float(sharpe_ratio),
                "target_return": target_return,
                "risk_tolerance": risk_tolerance
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error optimizing portfolio: {e}")
            raise HTTPException(status_code=500, detail="Failed to optimize portfolio")
    
    async def optimize_portfolio_black_litterman(
        self,
        user_id: str,
        tickers: List[str],
        views: List[Dict[str, Any]],  # [{"ticker": "ATW", "expected_return": 0.15, "confidence": 0.8}]
        risk_aversion: float = 2.5,
        tau: float = 0.05
    ) -> Dict[str, Any]:
        """Optimize portfolio using Black-Litterman model"""
        try:
            # Get market data
            returns_data = {}
            for ticker in tickers:
                historical_data = await self._get_historical_data(ticker, days=252)
                if historical_data:
                    prices = [float(quote['close']) for quote in historical_data]
                    returns = []
                    for i in range(1, len(prices)):
                        returns.append((prices[i] - prices[i-1]) / prices[i-1])
                    returns_data[ticker] = returns
            
            if len(returns_data) < 2:
                raise HTTPException(status_code=400, detail="Need at least 2 assets for optimization")
            
            # Calculate market equilibrium returns (reverse optimization)
            returns_matrix = []
            for ticker, returns in returns_data.items():
                returns_matrix.append(returns)
            
            # Pad shorter return series
            max_length = max(len(returns) for returns in returns_matrix)
            padded_returns = []
            for returns in returns_matrix:
                padded = returns + [0] * (max_length - len(returns))
                padded_returns.append(padded)
            
            covariance_matrix = np.cov(padded_returns) * 252
            
            # Market cap weights (simplified - equal weights)
            market_weights = np.array([1/len(tickers)] * len(tickers))
            
            # Equilibrium returns (Π = δΣw)
            equilibrium_returns = risk_aversion * np.dot(covariance_matrix, market_weights)
            
            # Process views
            if views:
                # Create view matrix P and view returns Q
                P = np.zeros((len(views), len(tickers)))
                Q = np.zeros(len(views))
                Omega = np.zeros((len(views), len(views)))
                
                for i, view in enumerate(views):
                    ticker_idx = tickers.index(view['ticker'])
                    P[i, ticker_idx] = 1
                    Q[i] = view['expected_return']
                    Omega[i, i] = 1 / view['confidence']
                
                # Black-Litterman formula
                tau_sigma = tau * covariance_matrix
                M1 = np.linalg.inv(tau_sigma)
                M2 = np.dot(P.T, np.dot(np.linalg.inv(Omega), P))
                M3 = np.dot(P.T, np.dot(np.linalg.inv(Omega), Q))
                
                # Posterior returns
                posterior_returns = np.linalg.inv(M1 + M2).dot(M1.dot(equilibrium_returns) + M3)
                posterior_covariance = np.linalg.inv(M1 + M2)
            else:
                posterior_returns = equilibrium_returns
                posterior_covariance = tau * covariance_matrix
            
            # Optimize with posterior returns
            def portfolio_variance(weights):
                return np.dot(weights.T, np.dot(posterior_covariance, weights))
            
            def portfolio_return(weights):
                return np.sum(weights * posterior_returns)
            
            # Constraints
            n_assets = len(tickers)
            constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
            bounds = [(0, 1) for _ in range(n_assets)]
            initial_weights = np.array([1/n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                portfolio_variance,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if not result.success:
                raise HTTPException(status_code=400, detail="Black-Litterman optimization failed")
            
            optimal_weights = result.x
            optimal_weights_dict = {ticker: float(weight) for ticker, weight in zip(tickers, optimal_weights)}
            
            # Calculate metrics
            expected_return = portfolio_return(optimal_weights)
            expected_volatility = np.sqrt(portfolio_variance(optimal_weights))
            sharpe_ratio = expected_return / expected_volatility if expected_volatility > 0 else 0
            
            # Store result
            optimization = PortfolioOptimization(
                user_id=user_id,
                optimization_type="black_litterman",
                optimal_weights=optimal_weights_dict,
                expected_return=Decimal(str(expected_return)),
                expected_volatility=Decimal(str(expected_volatility)),
                sharpe_ratio=Decimal(str(sharpe_ratio)),
                constraints={"views": views, "risk_aversion": risk_aversion, "tau": tau}
            )
            self.db.add(optimization)
            self.db.commit()
            
            return {
                "optimization_id": str(optimization.id),
                "optimal_weights": optimal_weights_dict,
                "expected_return": float(expected_return),
                "expected_volatility": float(expected_volatility),
                "sharpe_ratio": float(sharpe_ratio),
                "views": views,
                "risk_aversion": risk_aversion
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error in Black-Litterman optimization: {e}")
            raise HTTPException(status_code=500, detail="Failed to optimize portfolio")
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    async def _get_historical_data(self, ticker: str, days: int = 365) -> List[Dict[str, Any]]:
        """Get historical price data for a ticker"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            quotes = self.db.query(Quote).filter(
                and_(
                    Quote.ticker == ticker,
                    Quote.timestamp >= start_date,
                    Quote.timestamp <= end_date
                )
            ).order_by(Quote.timestamp).all()
            
            return [
                {
                    "date": quote.timestamp.date().isoformat(),
                    "open": float(quote.open_price),
                    "high": float(quote.high_24h),
                    "low": float(quote.low_24h),
                    "close": float(quote.price),
                    "volume": quote.volume
                }
                for quote in quotes
            ]
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []
    
    async def get_user_optimizations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's portfolio optimizations"""
        try:
            optimizations = self.db.query(PortfolioOptimization).filter(
                PortfolioOptimization.user_id == user_id
            ).order_by(desc(PortfolioOptimization.created_at)).all()
            
            optimization_data = []
            for opt in optimizations:
                optimization_data.append({
                    "id": str(opt.id),
                    "optimization_type": opt.optimization_type,
                    "expected_return": float(opt.expected_return) if opt.expected_return else None,
                    "expected_volatility": float(opt.expected_volatility) if opt.expected_volatility else None,
                    "sharpe_ratio": float(opt.sharpe_ratio) if opt.sharpe_ratio else None,
                    "created_at": opt.created_at.isoformat()
                })
            
            return optimization_data
            
        except Exception as e:
            logger.error(f"Error getting user optimizations: {e}")
            raise HTTPException(status_code=500, detail="Failed to get optimizations") 