"""
Data Expansion Service
Handles additional financial instruments: bonds, ETFs, and commodities data management.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from models.data_expansion import (
    Bond, BondPrice, ETF, ETFHolding, Commodity, CommodityPrice
)

logger = logging.getLogger(__name__)


class DataExpansionService:
    """Service for additional financial instruments"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================================
    # BONDS MANAGEMENT
    # ============================================================================
    
    async def add_bond(
        self,
        bond_code: str,
        issuer_name: str,
        issuer_type: str,
        bond_type: str,
        face_value: Decimal,
        coupon_rate: Optional[Decimal],
        maturity_date: datetime.date,
        issue_date: Optional[datetime.date] = None,
        yield_to_maturity: Optional[Decimal] = None,
        credit_rating: Optional[str] = None,
        currency: str = "MAD"
    ) -> Dict[str, Any]:
        """Add a new bond to the database"""
        try:
            # Check if bond already exists
            existing_bond = self.db.query(Bond).filter(Bond.bond_code == bond_code).first()
            if existing_bond:
                raise HTTPException(status_code=400, detail="Bond already exists")
            
            bond = Bond(
                bond_code=bond_code,
                issuer_name=issuer_name,
                issuer_type=issuer_type,
                bond_type=bond_type,
                face_value=face_value,
                coupon_rate=coupon_rate,
                maturity_date=maturity_date,
                issue_date=issue_date,
                yield_to_maturity=yield_to_maturity,
                credit_rating=credit_rating,
                currency=currency
            )
            self.db.add(bond)
            self.db.commit()
            
            return {
                "success": True,
                "bond_id": str(bond.id),
                "bond_code": bond.bond_code,
                "message": "Bond added successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding bond: {e}")
            raise HTTPException(status_code=500, detail="Failed to add bond")
    
    async def update_bond_price(
        self,
        bond_code: str,
        price: Decimal,
        yield_value: Optional[Decimal] = None,
        volume: Optional[int] = None,
        trade_date: Optional[datetime.date] = None
    ) -> Dict[str, Any]:
        """Update bond price data"""
        try:
            # Check if bond exists
            bond = self.db.query(Bond).filter(Bond.bond_code == bond_code).first()
            if not bond:
                raise HTTPException(status_code=404, detail="Bond not found")
            
            # Use current date if not provided
            if trade_date is None:
                trade_date = datetime.now().date()
            
            # Check if price already exists for this date
            existing_price = self.db.query(BondPrice).filter(
                and_(
                    BondPrice.bond_code == bond_code,
                    BondPrice.trade_date == trade_date
                )
            ).first()
            
            if existing_price:
                # Update existing price
                existing_price.price = price
                if yield_value is not None:
                    existing_price.yield_value = yield_value
                if volume is not None:
                    existing_price.volume = volume
            else:
                # Create new price record
                bond_price = BondPrice(
                    bond_code=bond_code,
                    price=price,
                    yield_value=yield_value,
                    volume=volume,
                    trade_date=trade_date
                )
                self.db.add(bond_price)
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Bond price updated successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating bond price: {e}")
            raise HTTPException(status_code=500, detail="Failed to update bond price")
    
    async def get_bonds(
        self,
        issuer_type: Optional[str] = None,
        bond_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get bonds with optional filtering"""
        try:
            query = self.db.query(Bond)
            
            if issuer_type:
                query = query.filter(Bond.issuer_type == issuer_type)
            if bond_type:
                query = query.filter(Bond.bond_type == bond_type)
            if active_only:
                query = query.filter(Bond.is_active == True)
            
            bonds = query.all()
            
            bond_data = []
            for bond in bonds:
                # Get latest price
                latest_price = self.db.query(BondPrice).filter(
                    BondPrice.bond_code == bond.bond_code
                ).order_by(desc(BondPrice.trade_date)).first()
                
                bond_data.append({
                    "id": str(bond.id),
                    "bond_code": bond.bond_code,
                    "issuer_name": bond.issuer_name,
                    "issuer_type": bond.issuer_type,
                    "bond_type": bond.bond_type,
                    "face_value": float(bond.face_value),
                    "coupon_rate": float(bond.coupon_rate) if bond.coupon_rate else None,
                    "maturity_date": bond.maturity_date.isoformat(),
                    "yield_to_maturity": float(bond.yield_to_maturity) if bond.yield_to_maturity else None,
                    "credit_rating": bond.credit_rating,
                    "currency": bond.currency,
                    "latest_price": float(latest_price.price) if latest_price else None,
                    "latest_yield": float(latest_price.yield_value) if latest_price and latest_price.yield_value else None,
                    "days_to_maturity": (bond.maturity_date - datetime.now().date()).days
                })
            
            return bond_data
            
        except Exception as e:
            logger.error(f"Error getting bonds: {e}")
            raise HTTPException(status_code=500, detail="Failed to get bonds")
    
    async def get_bond_prices(
        self,
        bond_code: str,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None
    ) -> List[Dict[str, Any]]:
        """Get bond price history"""
        try:
            query = self.db.query(BondPrice).filter(BondPrice.bond_code == bond_code)
            
            if start_date:
                query = query.filter(BondPrice.trade_date >= start_date)
            if end_date:
                query = query.filter(BondPrice.trade_date <= end_date)
            
            prices = query.order_by(BondPrice.trade_date).all()
            
            price_data = []
            for price in prices:
                price_data.append({
                    "trade_date": price.trade_date.isoformat(),
                    "price": float(price.price),
                    "yield": float(price.yield_value) if price.yield_value else None,
                    "volume": price.volume
                })
            
            return price_data
            
        except Exception as e:
            logger.error(f"Error getting bond prices: {e}")
            raise HTTPException(status_code=500, detail="Failed to get bond prices")
    
    # ============================================================================
    # ETFs MANAGEMENT
    # ============================================================================
    
    async def add_etf(
        self,
        ticker: str,
        name: str,
        description: Optional[str] = None,
        asset_class: str = "equity",
        investment_strategy: Optional[str] = None,
        expense_ratio: Optional[Decimal] = None,
        total_assets: Optional[Decimal] = None,
        inception_date: Optional[datetime.date] = None,
        benchmark_index: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a new ETF to the database"""
        try:
            # Check if ETF already exists
            existing_etf = self.db.query(ETF).filter(ETF.ticker == ticker).first()
            if existing_etf:
                raise HTTPException(status_code=400, detail="ETF already exists")
            
            etf = ETF(
                ticker=ticker,
                name=name,
                description=description,
                asset_class=asset_class,
                investment_strategy=investment_strategy,
                expense_ratio=expense_ratio,
                total_assets=total_assets,
                inception_date=inception_date,
                benchmark_index=benchmark_index
            )
            self.db.add(etf)
            self.db.commit()
            
            return {
                "success": True,
                "etf_id": str(etf.id),
                "ticker": etf.ticker,
                "message": "ETF added successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding ETF: {e}")
            raise HTTPException(status_code=500, detail="Failed to add ETF")
    
    async def add_etf_holding(
        self,
        etf_ticker: str,
        holding_ticker: str,
        holding_name: str,
        weight: Decimal,
        shares_held: Optional[int] = None,
        market_value: Optional[Decimal] = None,
        as_of_date: Optional[datetime.date] = None
    ) -> Dict[str, Any]:
        """Add a holding to an ETF"""
        try:
            # Check if ETF exists
            etf = self.db.query(ETF).filter(ETF.ticker == etf_ticker).first()
            if not etf:
                raise HTTPException(status_code=404, detail="ETF not found")
            
            # Use current date if not provided
            if as_of_date is None:
                as_of_date = datetime.now().date()
            
            # Check if holding already exists for this date
            existing_holding = self.db.query(ETFHolding).filter(
                and_(
                    ETFHolding.etf_ticker == etf_ticker,
                    ETFHolding.holding_ticker == holding_ticker,
                    ETFHolding.as_of_date == as_of_date
                )
            ).first()
            
            if existing_holding:
                # Update existing holding
                existing_holding.weight = weight
                existing_holding.holding_name = holding_name
                if shares_held is not None:
                    existing_holding.shares_held = shares_held
                if market_value is not None:
                    existing_holding.market_value = market_value
            else:
                # Create new holding
                holding = ETFHolding(
                    etf_ticker=etf_ticker,
                    holding_ticker=holding_ticker,
                    holding_name=holding_name,
                    weight=weight,
                    shares_held=shares_held,
                    market_value=market_value,
                    as_of_date=as_of_date
                )
                self.db.add(holding)
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "ETF holding added successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding ETF holding: {e}")
            raise HTTPException(status_code=500, detail="Failed to add ETF holding")
    
    async def get_etfs(
        self,
        asset_class: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get ETFs with optional filtering"""
        try:
            query = self.db.query(ETF)
            
            if asset_class:
                query = query.filter(ETF.asset_class == asset_class)
            if active_only:
                query = query.filter(ETF.is_active == True)
            
            etfs = query.all()
            
            etf_data = []
            for etf in etfs:
                # Get latest holdings count
                holdings_count = self.db.query(ETFHolding).filter(
                    ETFHolding.etf_ticker == etf.ticker
                ).count()
                
                etf_data.append({
                    "id": str(etf.id),
                    "ticker": etf.ticker,
                    "name": etf.name,
                    "description": etf.description,
                    "asset_class": etf.asset_class,
                    "investment_strategy": etf.investment_strategy,
                    "expense_ratio": float(etf.expense_ratio) if etf.expense_ratio else None,
                    "total_assets": float(etf.total_assets) if etf.total_assets else None,
                    "inception_date": etf.inception_date.isoformat() if etf.inception_date else None,
                    "benchmark_index": etf.benchmark_index,
                    "holdings_count": holdings_count
                })
            
            return etf_data
            
        except Exception as e:
            logger.error(f"Error getting ETFs: {e}")
            raise HTTPException(status_code=500, detail="Failed to get ETFs")
    
    async def get_etf_holdings(
        self,
        etf_ticker: str,
        as_of_date: Optional[datetime.date] = None
    ) -> List[Dict[str, Any]]:
        """Get ETF holdings"""
        try:
            query = self.db.query(ETFHolding).filter(ETFHolding.etf_ticker == etf_ticker)
            
            if as_of_date:
                query = query.filter(ETFHolding.as_of_date == as_of_date)
            else:
                # Get latest holdings
                latest_date = self.db.query(func.max(ETFHolding.as_of_date)).filter(
                    ETFHolding.etf_ticker == etf_ticker
                ).scalar()
                if latest_date:
                    query = query.filter(ETFHolding.as_of_date == latest_date)
            
            holdings = query.order_by(desc(ETFHolding.weight)).all()
            
            holdings_data = []
            for holding in holdings:
                holdings_data.append({
                    "holding_ticker": holding.holding_ticker,
                    "holding_name": holding.holding_name,
                    "weight": float(holding.weight),
                    "shares_held": holding.shares_held,
                    "market_value": float(holding.market_value) if holding.market_value else None,
                    "as_of_date": holding.as_of_date.isoformat()
                })
            
            return holdings_data
            
        except Exception as e:
            logger.error(f"Error getting ETF holdings: {e}")
            raise HTTPException(status_code=500, detail="Failed to get ETF holdings")
    
    # ============================================================================
    # COMMODITIES MANAGEMENT
    # ============================================================================
    
    async def add_commodity(
        self,
        commodity_code: str,
        name: str,
        category: str,
        unit: str,
        exchange: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a new commodity to the database"""
        try:
            # Check if commodity already exists
            existing_commodity = self.db.query(Commodity).filter(
                Commodity.commodity_code == commodity_code
            ).first()
            if existing_commodity:
                raise HTTPException(status_code=400, detail="Commodity already exists")
            
            commodity = Commodity(
                commodity_code=commodity_code,
                name=name,
                category=category,
                unit=unit,
                exchange=exchange
            )
            self.db.add(commodity)
            self.db.commit()
            
            return {
                "success": True,
                "commodity_id": str(commodity.id),
                "commodity_code": commodity.commodity_code,
                "message": "Commodity added successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding commodity: {e}")
            raise HTTPException(status_code=500, detail="Failed to add commodity")
    
    async def update_commodity_price(
        self,
        commodity_code: str,
        price: Decimal,
        volume: Optional[int] = None,
        open_interest: Optional[int] = None,
        trade_date: Optional[datetime.date] = None
    ) -> Dict[str, Any]:
        """Update commodity price data"""
        try:
            # Check if commodity exists
            commodity = self.db.query(Commodity).filter(
                Commodity.commodity_code == commodity_code
            ).first()
            if not commodity:
                raise HTTPException(status_code=404, detail="Commodity not found")
            
            # Use current date if not provided
            if trade_date is None:
                trade_date = datetime.now().date()
            
            # Check if price already exists for this date
            existing_price = self.db.query(CommodityPrice).filter(
                and_(
                    CommodityPrice.commodity_code == commodity_code,
                    CommodityPrice.trade_date == trade_date
                )
            ).first()
            
            if existing_price:
                # Update existing price
                existing_price.price = price
                if volume is not None:
                    existing_price.volume = volume
                if open_interest is not None:
                    existing_price.open_interest = open_interest
            else:
                # Create new price record
                commodity_price = CommodityPrice(
                    commodity_code=commodity_code,
                    price=price,
                    volume=volume,
                    open_interest=open_interest,
                    trade_date=trade_date
                )
                self.db.add(commodity_price)
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Commodity price updated successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating commodity price: {e}")
            raise HTTPException(status_code=500, detail="Failed to update commodity price")
    
    async def get_commodities(
        self,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get commodities with optional filtering"""
        try:
            query = self.db.query(Commodity)
            
            if category:
                query = query.filter(Commodity.category == category)
            if active_only:
                query = query.filter(Commodity.is_active == True)
            
            commodities = query.all()
            
            commodity_data = []
            for commodity in commodities:
                # Get latest price
                latest_price = self.db.query(CommodityPrice).filter(
                    CommodityPrice.commodity_code == commodity.commodity_code
                ).order_by(desc(CommodityPrice.trade_date)).first()
                
                commodity_data.append({
                    "id": str(commodity.id),
                    "commodity_code": commodity.commodity_code,
                    "name": commodity.name,
                    "category": commodity.category,
                    "unit": commodity.unit,
                    "exchange": commodity.exchange,
                    "latest_price": float(latest_price.price) if latest_price else None,
                    "latest_volume": latest_price.volume if latest_price else None,
                    "latest_open_interest": latest_price.open_interest if latest_price else None
                })
            
            return commodity_data
            
        except Exception as e:
            logger.error(f"Error getting commodities: {e}")
            raise HTTPException(status_code=500, detail="Failed to get commodities")
    
    async def get_commodity_prices(
        self,
        commodity_code: str,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None
    ) -> List[Dict[str, Any]]:
        """Get commodity price history"""
        try:
            query = self.db.query(CommodityPrice).filter(
                CommodityPrice.commodity_code == commodity_code
            )
            
            if start_date:
                query = query.filter(CommodityPrice.trade_date >= start_date)
            if end_date:
                query = query.filter(CommodityPrice.trade_date <= end_date)
            
            prices = query.order_by(CommodityPrice.trade_date).all()
            
            price_data = []
            for price in prices:
                price_data.append({
                    "trade_date": price.trade_date.isoformat(),
                    "price": float(price.price),
                    "volume": price.volume,
                    "open_interest": price.open_interest
                })
            
            return price_data
            
        except Exception as e:
            logger.error(f"Error getting commodity prices: {e}")
            raise HTTPException(status_code=500, detail="Failed to get commodity prices")
    
    # ============================================================================
    # MARKET DATA INTEGRATION
    # ============================================================================
    
    async def get_expanded_market_data(self) -> Dict[str, Any]:
        """Get comprehensive market data including all instrument types"""
        try:
            # Get equity data (existing)
            equity_count = self.db.query(func.count(Company.id)).scalar()
            
            # Get bond data
            bond_count = self.db.query(func.count(Bond.id)).filter(Bond.is_active == True).scalar()
            
            # Get ETF data
            etf_count = self.db.query(func.count(ETF.id)).filter(ETF.is_active == True).scalar()
            
            # Get commodity data
            commodity_count = self.db.query(func.count(Commodity.id)).filter(Commodity.is_active == True).scalar()
            
            return {
                "equities": {
                    "count": equity_count,
                    "description": "Casablanca Stock Exchange listed companies"
                },
                "bonds": {
                    "count": bond_count,
                    "description": "Government and corporate bonds"
                },
                "etfs": {
                    "count": etf_count,
                    "description": "Exchange-traded funds"
                },
                "commodities": {
                    "count": commodity_count,
                    "description": "Energy, metals, and agricultural commodities"
                },
                "total_instruments": equity_count + bond_count + etf_count + commodity_count
            }
            
        except Exception as e:
            logger.error(f"Error getting expanded market data: {e}")
            raise HTTPException(status_code=500, detail="Failed to get market data") 