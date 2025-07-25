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