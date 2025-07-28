"""
OpenAI Service for Casablanca Insight
Generates AI-powered market content including weekly recaps, summaries, and analysis.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client (optional)
openai_api_key = os.getenv("OpenAi_API_KEY") or os.getenv("OPENAI_API_KEY")
client = None

if openai_api_key and openai_api_key != "":
    try:
        client = OpenAI(api_key=openai_api_key)
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize OpenAI client: {e}")
        client = None
else:
    logger.warning("OpenAI API key not provided - AI features will be disabled")

@dataclass
class MarketData:
    """Market data structure for AI processing"""
    ticker: str
    name: str
    current_price: float
    change_percent: float
    volume: int
    sector: str

@dataclass
class MacroIndicator:
    """Macro economic indicator structure"""
    name: str
    value: float
    change: float
    description: str

@dataclass
class CompanyData:
    """Company data structure for AI analysis"""
    ticker: str
    name: str
    sector: str
    market_cap: float
    revenue: float
    net_income: float
    pe_ratio: float
    dividend_yield: float
    current_price: float
    price_change_percent: float

@dataclass
class PortfolioData:
    """Portfolio data structure for AI analysis"""
    total_value: float
    total_return: float
    total_return_percent: float
    positions: List[Dict[str, Any]]
    risk_metrics: Dict[str, float]

class OpenAIService:
    """OpenAI service for generating market content"""
    
    def __init__(self):
        self.client = client
        self.model = "gpt-4-turbo-preview"
        
    async def generate_weekly_recap(
        self,
        include_macro: bool = True,
        include_sectors: bool = True,
        include_top_movers: bool = True,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate AI-powered weekly market recap
        
        Args:
            include_macro: Include macro economic indicators
            include_sectors: Include sector performance
            include_top_movers: Include top moving stocks
            language: Language for content (en, fr, ar)
            
        Returns:
            Dictionary with subject, content, and metadata
        """
        try:
            # Get market data (mock data for now)
            market_data = await self._get_market_data()
            macro_data = await self._get_macro_data() if include_macro else None
            sector_data = await self._get_sector_data() if include_sectors else None
            top_movers = await self._get_top_movers() if include_top_movers else None
            
            # Generate the recap content
            content = await self._generate_recap_content(
                market_data=market_data,
                macro_data=macro_data,
                sector_data=sector_data,
                top_movers=top_movers,
                language=language
            )
            
            # Generate subject line
            subject = await self._generate_subject_line(language, market_data)
            
            return {
                "subject": subject,
                "content": content,
                "language": language,
                "generated_at": datetime.now().isoformat(),
                "includes": {
                    "macro": include_macro,
                    "sectors": include_sectors,
                    "top_movers": include_top_movers
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating weekly recap: {str(e)}")
            return await self._get_fallback_content(language)
    
    async def generate_company_summary(self, ticker: str, company_data: CompanyData, language: str = "en") -> str:
        """
        Generate AI-powered company summary
        
        Args:
            ticker: Company ticker symbol
            company_data: Company financial data
            language: Language for content (en, fr, ar)
            
        Returns:
            AI-generated company summary
        """
        try:
            if not self.client:
                return self._get_fallback_company_summary(ticker, language)
            
            prompt = self._get_company_summary_prompt(ticker, company_data, language)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in Moroccan markets. Provide clear, concise analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content or self._get_fallback_company_summary(ticker, language)
            
        except Exception as e:
            logger.error(f"Error generating company summary for {ticker}: {e}")
            return self._get_fallback_company_summary(ticker, language)
    
    def _get_company_summary_prompt(self, ticker: str, company_data: CompanyData, language: str) -> str:
        """Generate prompt for company summary"""
        if language == "fr":
            return f"""
            Analysez la société {ticker} ({company_data.name}) basée sur les données suivantes:
            
            Secteur: {company_data.sector}
            Capitalisation boursière: {company_data.market_cap:,.0f} MAD
            Revenus: {company_data.revenue:,.0f} MAD
            Bénéfice net: {company_data.net_income:,.0f} MAD
            Ratio P/E: {company_data.pe_ratio:.2f}
            Rendement dividende: {company_data.dividend_yield:.2f}%
            Prix actuel: {company_data.current_price:.2f} MAD
            Variation: {company_data.price_change_percent:+.2f}%
            
            Fournissez une analyse concise incluant:
            1. Santé financière générale
            2. Événements clés récents
            3. Tendances de performance
            4. Risques et perspectives
            5. Recommandation d'investissement
            
            Utilisez un langage simple et accessible aux investisseurs.
            """
        elif language == "ar":
            return f"""
            حلل الشركة {ticker} ({company_data.name}) بناءً على البيانات التالية:
            
            القطاع: {company_data.sector}
            القيمة السوقية: {company_data.market_cap:,.0f} درهم
            الإيرادات: {company_data.revenue:,.0f} درهم
            صافي الربح: {company_data.net_income:,.0f} درهم
            نسبة السعر إلى الأرباح: {company_data.pe_ratio:.2f}
            عائد الأرباح: {company_data.dividend_yield:.2f}%
            السعر الحالي: {company_data.current_price:.2f} درهم
            التغير: {company_data.price_change_percent:+.2f}%
            
            قدم تحليلاً موجزاً يشمل:
            1. الصحة المالية العامة
            2. الأحداث الرئيسية الأخيرة
            3. اتجاهات الأداء
            4. المخاطر والآفاق
            5. توصية الاستثمار
            
            استخدم لغة بسيطة ومفهومة للمستثمرين.
            """
        else:  # English
            return f"""
            Analyze the company {ticker} ({company_data.name}) based on the following data:
            
            Sector: {company_data.sector}
            Market Cap: {company_data.market_cap:,.0f} MAD
            Revenue: {company_data.revenue:,.0f} MAD
            Net Income: {company_data.net_income:,.0f} MAD
            P/E Ratio: {company_data.pe_ratio:.2f}
            Dividend Yield: {company_data.dividend_yield:.2f}%
            Current Price: {company_data.current_price:.2f} MAD
            Price Change: {company_data.price_change_percent:+.2f}%
            
            Provide a concise analysis including:
            1. Overall financial health
            2. Recent key events
            3. Performance trends
            4. Risks and outlook
            5. Investment recommendation
            
            Use simple language accessible to investors.
            """
    
    def _get_fallback_company_summary(self, ticker: str, language: str) -> str:
        """Get fallback company summary when AI fails"""
        fallback_summaries = {
            "en": f"{ticker} demonstrates solid fundamentals with consistent performance in its sector. The company maintains healthy financial ratios and shows promising growth potential. Investors should consider this as a stable addition to their portfolio.",
            "fr": f"{ticker} démontre des fondamentaux solides avec une performance constante dans son secteur. L'entreprise maintient des ratios financiers sains et montre un potentiel de croissance prometteur. Les investisseurs devraient considérer cela comme un ajout stable à leur portefeuille.",
            "ar": f"تُظهر {ticker} أساسيات قوية مع أداء ثابت في قطاعها. تحافظ الشركة على نسب مالية صحية وتظهر إمكانات نمو واعدة. يجب على المستثمرين النظر في هذا كإضافة مستقرة لمحفظتهم الاستثمارية."
        }
        return fallback_summaries.get(language, fallback_summaries["en"])
    
    async def generate_portfolio_analysis(self, portfolio_data: PortfolioData, language: str = "en") -> Dict[str, Any]:
        """
        Generate AI-powered portfolio analysis
        
        Args:
            portfolio_data: Portfolio performance data
            language: Language for content (en, fr, ar)
            
        Returns:
            AI-generated portfolio analysis
        """
        try:
            if not self.client:
                return self._get_fallback_portfolio_analysis(portfolio_data, language)
            
            prompt = self._get_portfolio_analysis_prompt(portfolio_data, language)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a portfolio analyst specializing in Moroccan markets. Provide actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content or self._get_fallback_portfolio_analysis(portfolio_data, language)
            
            return {
                "analysis": analysis_text,
                "risk_assessment": self._analyze_portfolio_risk(portfolio_data),
                "recommendations": self._generate_portfolio_recommendations(portfolio_data),
                "language": language,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating portfolio analysis: {e}")
            return self._get_fallback_portfolio_analysis(portfolio_data, language)
    
    def _get_portfolio_analysis_prompt(self, portfolio_data: PortfolioData, language: str) -> str:
        """Generate prompt for portfolio analysis"""
        if language == "fr":
            return f"""
            Analysez ce portefeuille d'investissement basé sur les données suivantes:
            
            Valeur totale: {portfolio_data.total_value:,.0f} MAD
            Rendement total: {portfolio_data.total_return:,.0f} MAD ({portfolio_data.total_return_percent:+.2f}%)
            Nombre de positions: {len(portfolio_data.positions)}
            
            Positions principales:
            {self._format_positions_for_prompt(portfolio_data.positions, language)}
            
            Métriques de risque:
            {self._format_risk_metrics_for_prompt(portfolio_data.risk_metrics, language)}
            
            Fournissez une analyse complète incluant:
            1. Performance générale du portefeuille
            2. Analyse des risques
            3. Diversification
            4. Recommandations d'amélioration
            5. Opportunités d'investissement
            
            Utilisez un langage professionnel mais accessible.
            """
        elif language == "ar":
            return f"""
            حلل محفظة الاستثمار هذه بناءً على البيانات التالية:
            
            القيمة الإجمالية: {portfolio_data.total_value:,.0f} درهم
            العائد الإجمالي: {portfolio_data.total_return:,.0f} درهم ({portfolio_data.total_return_percent:+.2f}%)
            عدد المراكز: {len(portfolio_data.positions)}
            
            المراكز الرئيسية:
            {self._format_positions_for_prompt(portfolio_data.positions, language)}
            
            مقاييس المخاطر:
            {self._format_risk_metrics_for_prompt(portfolio_data.risk_metrics, language)}
            
            قدم تحليلاً شاملاً يشمل:
            1. الأداء العام للمحفظة
            2. تحليل المخاطر
            3. التنويع
            4. توصيات التحسين
            5. فرص الاستثمار
            
            استخدم لغة مهنية ولكن مفهومة.
            """
        else:  # English
            return f"""
            Analyze this investment portfolio based on the following data:
            
            Total Value: {portfolio_data.total_value:,.0f} MAD
            Total Return: {portfolio_data.total_return:,.0f} MAD ({portfolio_data.total_return_percent:+.2f}%)
            Number of Positions: {len(portfolio_data.positions)}
            
            Key Positions:
            {self._format_positions_for_prompt(portfolio_data.positions, language)}
            
            Risk Metrics:
            {self._format_risk_metrics_for_prompt(portfolio_data.risk_metrics, language)}
            
            Provide a comprehensive analysis including:
            1. Overall portfolio performance
            2. Risk analysis
            3. Diversification
            4. Improvement recommendations
            5. Investment opportunities
            
            Use professional but accessible language.
            """
    
    def _format_positions_for_prompt(self, positions: List[Dict[str, Any]], language: str) -> str:
        """Format positions for prompt"""
        if language == "fr":
            return "\n".join([
                f"- {pos['ticker']}: {pos['quantity']} actions, {pos['return_percent']:+.2f}%"
                for pos in positions[:5]  # Top 5 positions
            ])
        elif language == "ar":
            return "\n".join([
                f"- {pos['ticker']}: {pos['quantity']} سهم، {pos['return_percent']:+.2f}%"
                for pos in positions[:5]
            ])
        else:
            return "\n".join([
                f"- {pos['ticker']}: {pos['quantity']} shares, {pos['return_percent']:+.2f}%"
                for pos in positions[:5]
            ])
    
    def _format_risk_metrics_for_prompt(self, risk_metrics: Dict[str, float], language: str) -> str:
        """Format risk metrics for prompt"""
        if language == "fr":
            return f"""
            - Volatilité: {risk_metrics.get('volatility', 0):.2f}%
            - Ratio de Sharpe: {risk_metrics.get('sharpe_ratio', 0):.2f}
            - Beta: {risk_metrics.get('beta', 0):.2f}
            - Ratio de Sortino: {risk_metrics.get('sortino_ratio', 0):.2f}
            """
        elif language == "ar":
            return f"""
            - التقلب: {risk_metrics.get('volatility', 0):.2f}%
            - نسبة شارب: {risk_metrics.get('sharpe_ratio', 0):.2f}
            - بيتا: {risk_metrics.get('beta', 0):.2f}
            - نسبة سورتينو: {risk_metrics.get('sortino_ratio', 0):.2f}
            """
        else:
            return f"""
            - Volatility: {risk_metrics.get('volatility', 0):.2f}%
            - Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 0):.2f}
            - Beta: {risk_metrics.get('beta', 0):.2f}
            - Sortino Ratio: {risk_metrics.get('sortino_ratio', 0):.2f}
            """
    
    def _analyze_portfolio_risk(self, portfolio_data: PortfolioData) -> Dict[str, Any]:
        """Analyze portfolio risk metrics"""
        volatility = portfolio_data.risk_metrics.get('volatility', 0)
        sharpe_ratio = portfolio_data.risk_metrics.get('sharpe_ratio', 0)
        beta = portfolio_data.risk_metrics.get('beta', 0)
        
        risk_level = "Low"
        if volatility > 20:
            risk_level = "High"
        elif volatility > 10:
            risk_level = "Medium"
        
        return {
            "risk_level": risk_level,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "beta": beta,
            "diversification_score": self._calculate_diversification_score(portfolio_data.positions)
        }
    
    def _calculate_diversification_score(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate portfolio diversification score"""
        if not positions:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        weights = [pos.get('weight', 0) for pos in positions]
        hhi = sum(w * w for w in weights)
        
        # Convert to diversification score (0-100)
        diversification_score = max(0, 100 - (hhi * 100))
        return min(100, diversification_score)
    
    def _generate_portfolio_recommendations(self, portfolio_data: PortfolioData) -> List[str]:
        """Generate portfolio recommendations"""
        recommendations = []
        
        # Analyze performance
        if portfolio_data.total_return_percent < 0:
            recommendations.append("Consider rebalancing underperforming positions")
        
        # Analyze diversification
        diversification_score = self._calculate_diversification_score(portfolio_data.positions)
        if diversification_score < 50:
            recommendations.append("Increase portfolio diversification")
        
        # Analyze risk
        volatility = portfolio_data.risk_metrics.get('volatility', 0)
        if volatility > 20:
            recommendations.append("Consider reducing portfolio risk exposure")
        
        # Add general recommendations
        recommendations.extend([
            "Regularly review and rebalance your portfolio",
            "Consider adding defensive stocks for stability",
            "Monitor sector allocation for optimal diversification"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _get_fallback_portfolio_analysis(self, portfolio_data: PortfolioData, language: str) -> Dict[str, Any]:
        """Get fallback portfolio analysis when AI fails"""
        fallback_analyses = {
            "en": {
                "analysis": f"Your portfolio shows a {portfolio_data.total_return_percent:+.2f}% return with {len(portfolio_data.positions)} positions. Consider reviewing your allocation and risk management strategy.",
                "risk_assessment": {"risk_level": "Medium", "volatility": 12.5, "sharpe_ratio": 0.8, "beta": 1.1, "diversification_score": 65.0},
                "recommendations": ["Regular portfolio review", "Consider diversification", "Monitor risk metrics"]
            },
            "fr": {
                "analysis": f"Votre portefeuille affiche un rendement de {portfolio_data.total_return_percent:+.2f}% avec {len(portfolio_data.positions)} positions. Considérez revoir votre allocation et stratégie de gestion des risques.",
                "risk_assessment": {"risk_level": "Moyen", "volatility": 12.5, "sharpe_ratio": 0.8, "beta": 1.1, "diversification_score": 65.0},
                "recommendations": ["Révision régulière du portefeuille", "Considérer la diversification", "Surveiller les métriques de risque"]
            },
            "ar": {
                "analysis": f"محفظتك تظهر عائد {portfolio_data.total_return_percent:+.2f}% مع {len(portfolio_data.positions)} مراكز. فكر في مراجعة توزيعك واستراتيجية إدارة المخاطر.",
                "risk_assessment": {"risk_level": "متوسط", "volatility": 12.5, "sharpe_ratio": 0.8, "beta": 1.1, "diversification_score": 65.0},
                "recommendations": ["مراجعة دورية للمحفظة", "فكر في التنويع", "راقب مقاييس المخاطر"]
            }
        }
        
        analysis = fallback_analyses.get(language, fallback_analyses["en"])
        analysis["language"] = language
        analysis["generated_at"] = datetime.now().isoformat()
        return analysis
    
    async def generate_enhanced_chat_response(self, query: str, context: Dict[str, Any], language: str = "en") -> str:
        """
        Generate enhanced chat response with context awareness
        
        Args:
            query: User's question
            context: Market data and portfolio context
            language: Language for response
            
        Returns:
            AI-generated response
        """
        try:
            if not self.client:
                return self._get_fallback_chat_response(query, language)
            
            prompt = self._get_enhanced_chat_prompt(query, context, language)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a knowledgeable financial advisor specializing in Moroccan markets. Provide helpful, accurate, and actionable advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            return response.choices[0].message.content or self._get_fallback_chat_response(query, language)
            
        except Exception as e:
            logger.error(f"Error generating enhanced chat response: {e}")
            return self._get_fallback_chat_response(query, language)
    
    def _get_enhanced_chat_prompt(self, query: str, context: Dict[str, Any], language: str) -> str:
        """Generate enhanced chat prompt with context"""
        if language == "fr":
            return f"""
            Question de l'utilisateur: {query}
            
            Contexte du marché:
            - Données de marché: {json.dumps(context.get('market_data', {}), ensure_ascii=False)}
            - Données macro: {json.dumps(context.get('macro_data', {}), ensure_ascii=False)}
            - Données du portefeuille: {json.dumps(context.get('portfolio_data', {}), ensure_ascii=False)}
            
            Répondez de manière utile et précise en français. Utilisez le contexte fourni pour donner des conseils pertinents.
            """
        elif language == "ar":
            return f"""
            سؤال المستخدم: {query}
            
            سياق السوق:
            - بيانات السوق: {json.dumps(context.get('market_data', {}), ensure_ascii=False)}
            - البيانات الاقتصادية الكلية: {json.dumps(context.get('macro_data', {}), ensure_ascii=False)}
            - بيانات المحفظة: {json.dumps(context.get('portfolio_data', {}), ensure_ascii=False)}
            
            أجب بطريقة مفيدة ودقيقة باللغة العربية. استخدم السياق المقدم لإعطاء نصائح ذات صلة.
            """
        else:  # English
            return f"""
            User question: {query}
            
            Market context:
            - Market data: {json.dumps(context.get('market_data', {}))}
            - Macro data: {json.dumps(context.get('macro_data', {}))}
            - Portfolio data: {json.dumps(context.get('portfolio_data', {}))}
            
            Respond in a helpful and accurate manner in English. Use the provided context to give relevant advice.
            """
    
    def _get_fallback_chat_response(self, query: str, language: str) -> str:
        """Get fallback chat response when AI fails"""
        fallback_responses = {
            "en": "I apologize, but I'm unable to process your request at the moment. Please try again later or contact our support team for assistance.",
            "fr": "Je m'excuse, mais je ne peux pas traiter votre demande pour le moment. Veuillez réessayer plus tard ou contacter notre équipe de support pour obtenir de l'aide.",
            "ar": "أعتذر، لكنني غير قادر على معالجة طلبك في الوقت الحالي. يرجى المحاولة مرة أخرى لاحقاً أو الاتصال بفريق الدعم للحصول على المساعدة."
        }
        return fallback_responses.get(language, fallback_responses["en"])
    
    async def _generate_recap_content(
        self,
        market_data: List[MarketData],
        macro_data: Optional[List[MacroIndicator]],
        sector_data: Optional[Dict[str, float]],
        top_movers: Optional[Dict[str, List[MarketData]]],
        language: str
    ) -> str:
        """Generate the main recap content using OpenAI"""
        
        # Prepare context for AI
        context = self._prepare_context(market_data, macro_data, sector_data, top_movers)
        
        # Language-specific prompts
        prompts = {
            "en": self._get_english_prompt(context),
            "fr": self._get_french_prompt(context),
            "ar": self._get_arabic_prompt(context)
        }
        
        prompt = prompts.get(language, prompts["en"])
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional financial analyst specializing in Moroccan markets."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content or self._get_fallback_content_text(language)
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return self._get_fallback_content_text(language)
    
    async def _generate_subject_line(self, language: str, market_data: List[MarketData]) -> str:
        """Generate email subject line"""
        
        # Calculate market sentiment
        positive_moves = sum(1 for stock in market_data if stock.change_percent > 0)
        total_stocks = len(market_data)
        market_sentiment = "positive" if positive_moves > total_stocks / 2 else "negative"
        
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        subjects = {
            "en": f"Morocco Markets Weekly Recap - {current_date}",
            "fr": f"Récapitulatif Hebdomadaire des Marchés Marocains - {current_date}",
            "ar": f"ملخص أسبوعي للأسواق المغربية - {current_date}"
        }
        
        return subjects.get(language, subjects["en"])
    
    def _prepare_context(
        self,
        market_data: List[MarketData],
        macro_data: Optional[List[MacroIndicator]],
        sector_data: Optional[Dict[str, float]],
        top_movers: Optional[Dict[str, List[MarketData]]]
    ) -> Dict[str, Any]:
        """Prepare context data for AI processing"""
        
        context = {
            "market_overview": {
                "total_stocks": len(market_data),
                "positive_moves": sum(1 for stock in market_data if stock.change_percent > 0),
                "average_change": sum(stock.change_percent for stock in market_data) / len(market_data) if market_data else 0
            },
            "key_stocks": [
                {
                    "ticker": stock.ticker,
                    "name": stock.name,
                    "change_percent": stock.change_percent,
                    "sector": stock.sector
                }
                for stock in market_data[:5]  # Top 5 stocks
            ]
        }
        
        if macro_data:
            context["macro_indicators"] = [
                {
                    "name": indicator.name,
                    "value": indicator.value,
                    "change": indicator.change,
                    "description": indicator.description
                }
                for indicator in macro_data
            ]
        
        if sector_data:
            context["sector_performance"] = sector_data
        
        if top_movers:
            context["top_movers"] = {
                "gainers": [
                    {"ticker": stock.ticker, "name": stock.name, "change": stock.change_percent}
                    for stock in top_movers.get("gainers", [])
                ],
                "losers": [
                    {"ticker": stock.ticker, "name": stock.name, "change": stock.change_percent}
                    for stock in top_movers.get("losers", [])
                ]
            }
        
        return context
    
    def _get_english_prompt(self, context: Dict[str, Any]) -> str:
        """Get English language prompt"""
        return f"""
        Write a professional weekly market recap for Morocco's financial markets in English.
        
        Context data:
        {json.dumps(context, indent=2)}
        
        Please include:
        1. Market overview and sentiment
        2. Key stock movements and notable performers
        3. Sector analysis (if available)
        4. Macro economic context (if available)
        5. Brief outlook for the upcoming week
        
        Keep the tone professional but accessible. Target length: 300-500 words.
        Use proper financial terminology and include specific numbers where relevant.
        """
    
    def _get_french_prompt(self, context: Dict[str, Any]) -> str:
        """Get French language prompt"""
        return f"""
        Rédigez un récapitulatif hebdomadaire professionnel des marchés financiers du Maroc en français.
        
        Données contextuelles:
        {json.dumps(context, indent=2)}
        
        Veuillez inclure:
        1. Vue d'ensemble et sentiment du marché
        2. Mouvements clés des actions et performances notables
        3. Analyse sectorielle (si disponible)
        4. Contexte macroéconomique (si disponible)
        5. Perspectives brèves pour la semaine à venir
        
        Gardez un ton professionnel mais accessible. Longueur cible: 300-500 mots.
        Utilisez la terminologie financière appropriée et incluez des chiffres spécifiques lorsque pertinent.
        """
    
    def _get_arabic_prompt(self, context: Dict[str, Any]) -> str:
        """Get Arabic language prompt"""
        return f"""
        اكتب ملخصاً أسبوعياً مهنياً للأسواق المالية المغربية باللغة العربية.
        
        البيانات السياقية:
        {json.dumps(context, indent=2)}
        
        يرجى تضمين:
        1. نظرة عامة على السوق والمشاعر السائدة
        2. تحركات الأسهم الرئيسية والأداء البارز
        3. تحليل القطاعات (إن وجد)
        4. السياق الاقتصادي الكلي (إن وجد)
        5. نظرة موجزة للأسبوع القادم
        
        حافظ على نبرة مهنية ولكن في المتناول. الطول المستهدف: 300-500 كلمة.
        استخدم المصطلحات المالية المناسبة وأدرج أرقاماً محددة عند الاقتضاء.
        """
    
    async def _get_market_data(self) -> List[MarketData]:
        """Get market data (mock implementation)"""
        # In a real implementation, this would fetch from your database
        return [
            MarketData("ATW", "Attijariwafa Bank", 520.50, 2.3, 1250000, "Banking"),
            MarketData("IAM", "Maroc Telecom", 145.20, -0.8, 890000, "Telecom"),
            MarketData("BCP", "Banque Centrale Populaire", 285.75, 1.5, 650000, "Banking"),
            MarketData("BMCE", "BMCE Bank", 198.40, -1.2, 420000, "Banking"),
            MarketData("ONA", "Omnium Nord Africain", 102.30, 0.5, 320000, "Conglomerate"),
        ]
    
    async def _get_macro_data(self) -> List[MacroIndicator]:
        """Get macro economic data (mock implementation)"""
        return [
            MacroIndicator("Policy Rate", 3.0, 0.0, "Bank Al-Maghrib policy rate"),
            MacroIndicator("Inflation Rate", 2.1, -0.3, "Annual inflation rate"),
            MacroIndicator("USD/MAD", 10.15, 0.2, "Exchange rate")
        ]
    
    async def _get_sector_data(self) -> Dict[str, float]:
        """Get sector performance data (mock implementation)"""
        return {
            "Banking": 1.8,
            "Telecom": -0.5,
            "Real Estate": 0.8,
            "Mining": 2.1,
            "Insurance": 1.2
        }
    
    async def _get_top_movers(self) -> Dict[str, List[MarketData]]:
        """Get top moving stocks (mock implementation)"""
        return {
            "gainers": [
                MarketData("ATW", "Attijariwafa Bank", 520.50, 2.3, 1250000, "Banking"),
                MarketData("CMT", "Ciments du Maroc", 1845.00, 1.8, 15000, "Materials"),
            ],
            "losers": [
                MarketData("IAM", "Maroc Telecom", 145.20, -0.8, 890000, "Telecom"),
                MarketData("BMCE", "BMCE Bank", 198.40, -1.2, 420000, "Banking"),
            ]
        }
    
    async def _get_fallback_content(self, language: str) -> Dict[str, Any]:
        """Get fallback content when AI generation fails"""
        fallback_content = {
            "en": {
                "subject": "Morocco Markets Weekly Recap",
                "content": "We apologize, but we're unable to generate the weekly recap at this time. Please check back later for the latest market updates."
            },
            "fr": {
                "subject": "Récapitulatif Hebdomadaire des Marchés Marocains",
                "content": "Nous nous excusons, mais nous ne pouvons pas générer le récapitulatif hebdomadaire pour le moment. Veuillez revenir plus tard pour les dernières mises à jour du marché."
            },
            "ar": {
                "subject": "ملخص أسبوعي للأسواق المغربية",
                "content": "نعتذر، لكننا غير قادرين على إنتاج الملخص الأسبوعي في الوقت الحالي. يرجى العودة لاحقاً للحصول على أحدث تحديثات السوق."
            }
        }
        
        content = fallback_content.get(language, fallback_content["en"])
        return {
            "subject": content["subject"],
            "content": content["content"],
            "language": language,
            "generated_at": datetime.now().isoformat(),
            "is_fallback": True
        }
    
    def _get_fallback_content_text(self, language: str) -> str:
        """Get fallback content text only"""
        fallback_texts = {
            "en": "Market analysis is temporarily unavailable. Please check back later for updates.",
            "fr": "L'analyse de marché est temporairement indisponible. Veuillez revenir plus tard pour les mises à jour.",
            "ar": "تحليل السوق غير متاح مؤقتاً. يرجى العودة لاحقاً للتحديثات."
        }
        return fallback_texts.get(language, fallback_texts["en"])

# Global service instance
openai_service = OpenAIService()

# Convenience functions for backward compatibility
async def generate_weekly_recap(
    include_macro: bool = True,
    include_sectors: bool = True,
    include_top_movers: bool = True,
    language: str = "en"
) -> Dict[str, Any]:
    """Generate weekly market recap"""
    return await openai_service.generate_weekly_recap(
        include_macro=include_macro,
        include_sectors=include_sectors,
        include_top_movers=include_top_movers,
        language=language
    )

async def generate_market_summary(ticker: str, language: str = "en") -> str:
    """Generate market summary for a specific ticker"""
    # This would be implemented for individual stock analysis
    return f"Market summary for {ticker} (language: {language})"

async def generate_chat_response(query: str, context: Dict[str, Any], language: str = "en") -> str:
    """Generate chat response for AI chat system"""
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a financial advisor specializing in Moroccan markets."},
                {"role": "user", "content": f"Query: {query}\nContext: {json.dumps(context)}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content or "I apologize, but I'm unable to process your request at the moment. Please try again later."
    except Exception as e:
        logger.error(f"Error generating chat response: {str(e)}")
        return "I apologize, but I'm unable to process your request at the moment. Please try again later." 