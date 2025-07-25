#!/usr/bin/env python3
"""
Newsletter Content Generator

This script generates newsletter content using real market data and AI analysis.
It can create weekly recaps, market summaries, and company-specific analysis.

Usage:
    python scripts/generate_newsletter_content.py [--type weekly|daily|company] [--language en|fr|ar] [--output file.json]
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import requests
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install: pip install requests python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

class NewsletterContentGenerator:
    """Generate newsletter content using market data and AI"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found")
            print("   Content will use fallback data")
    
    async def get_market_data(self) -> Dict[str, Any]:
        """Fetch current market data"""
        try:
            # Get market quotes
            quotes_response = requests.get(f"{self.api_base_url}/api/markets/quotes", timeout=10)
            quotes_data = quotes_response.json() if quotes_response.status_code == 200 else {"quotes": []}
            
            # Get market summary
            summary_response = requests.get(f"{self.api_base_url}/api/markets/summary", timeout=10)
            summary_data = summary_response.json() if summary_response.status_code == 200 else {}
            
            # Get sector data
            sectors_response = requests.get(f"{self.api_base_url}/api/markets/sectors", timeout=10)
            sectors_data = sectors_response.json() if sectors_response.status_code == 200 else {"sectors": []}
            
            return {
                "quotes": quotes_data.get("quotes", []),
                "summary": summary_data,
                "sectors": sectors_data.get("sectors", []),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return {"quotes": [], "summary": {}, "sectors": [], "timestamp": datetime.now().isoformat()}
    
    async def generate_weekly_recap(self, language: str = "en") -> Dict[str, Any]:
        """Generate weekly market recap"""
        print(f"📊 Generating weekly recap in {language.upper()}")
        
        try:
            url = f"{self.api_base_url}/api/newsletter/generate-weekly-recap"
            payload = {
                "include_macro": True,
                "include_sectors": True,
                "include_top_movers": True,
                "language": language
            }
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Weekly recap generated successfully!")
                return data
            else:
                print(f"❌ Failed to generate weekly recap: {response.status_code}")
                return self._generate_fallback_recap(language)
                
        except Exception as e:
            print(f"❌ Error generating weekly recap: {e}")
            return self._generate_fallback_recap(language)
    
    async def generate_daily_summary(self, language: str = "en") -> Dict[str, Any]:
        """Generate daily market summary"""
        print(f"📊 Generating daily summary in {language.upper()}")
        
        try:
            # Get market data
            market_data = await self.get_market_data()
            
            # Generate AI summary using chat endpoint
            url = f"{self.api_base_url}/api/chat"
            prompt = f"Generate a concise daily market summary for Morocco in {language}. Include key indices, top movers, and market sentiment."
            
            payload = {
                "message": prompt,
                "context": {
                    "market_data": market_data,
                    "language": language,
                    "type": "daily_summary"
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "type": "daily_summary",
                    "language": language,
                    "subject": f"Daily Market Summary - {datetime.now().strftime('%Y-%m-%d')}",
                    "content": data.get("response", ""),
                    "market_data": market_data,
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return self._generate_fallback_daily_summary(language, market_data)
                
        except Exception as e:
            print(f"❌ Error generating daily summary: {e}")
            return self._generate_fallback_daily_summary(language, {})
    
    async def generate_company_analysis(self, ticker: str, language: str = "en") -> Dict[str, Any]:
        """Generate company-specific analysis"""
        print(f"📊 Generating company analysis for {ticker} in {language.upper()}")
        
        try:
            # Get company data
            company_url = f"{self.api_base_url}/api/markets/quotes?tickers={ticker}"
            company_response = requests.get(company_url, timeout=10)
            company_data = company_response.json() if company_response.status_code == 200 else {}
            
            # Generate AI analysis
            url = f"{self.api_base_url}/api/chat"
            prompt = f"Generate a comprehensive analysis for {ticker} in {language}. Include technical analysis, fundamental factors, and investment outlook."
            
            payload = {
                "message": prompt,
                "context": {
                    "ticker": ticker,
                    "company_data": company_data,
                    "language": language,
                    "type": "company_analysis"
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "type": "company_analysis",
                    "ticker": ticker,
                    "language": language,
                    "subject": f"{ticker} Analysis - {datetime.now().strftime('%Y-%m-%d')}",
                    "content": data.get("response", ""),
                    "company_data": company_data,
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return self._generate_fallback_company_analysis(ticker, language, company_data)
                
        except Exception as e:
            print(f"❌ Error generating company analysis: {e}")
            return self._generate_fallback_company_analysis(ticker, language, {})
    
    def _generate_fallback_recap(self, language: str) -> Dict[str, Any]:
        """Generate fallback weekly recap content"""
        if language == "fr":
            subject = "Récapitulatif Hebdomadaire du Marché Marocain"
            content = """
            📊 Récapitulatif Hebdomadaire du Marché Marocain
            
            Cette semaine, le marché marocain a connu des mouvements variés avec des performances sectorielles mixtes.
            
            🏦 Secteur Bancaire
            Les banques ont affiché une performance stable avec ATW et BCP en tête.
            
            📱 Télécommunications
            IAM a maintenu sa position dominante dans le secteur.
            
            📈 Perspectives
            Les analystes restent optimistes pour la semaine à venir.
            """
        elif language == "ar":
            subject = "ملخص أسبوعي للسوق المغربي"
            content = """
            📊 ملخص أسبوعي للسوق المغربي
            
            شهد السوق المغربي هذه الأسبوع حركات متنوعة مع أداء قطاعي مختلط.
            
            🏦 قطاع البنوك
            أظهرت البنوك أداء مستقر مع تصدر ATW و BCP.
            
            📱 الاتصالات
            حافظت IAM على موقعها المهيمن في القطاع.
            
            📈 التوقعات
            يبقى المحللون متفائلين للأسبوع القادم.
            """
        else:
            subject = "Weekly Moroccan Market Recap"
            content = """
            📊 Weekly Moroccan Market Recap
            
            This week, the Moroccan market experienced varied movements with mixed sectoral performance.
            
            🏦 Banking Sector
            Banks showed stable performance with ATW and BCP leading.
            
            📱 Telecommunications
            IAM maintained its dominant position in the sector.
            
            📈 Outlook
            Analysts remain optimistic for the coming week.
            """
        
        return {
            "type": "weekly_recap",
            "language": language,
            "subject": subject,
            "content": content,
            "generated_at": datetime.now().isoformat(),
            "fallback": True
        }
    
    def _generate_fallback_daily_summary(self, language: str, market_data: Dict) -> Dict[str, Any]:
        """Generate fallback daily summary content"""
        if language == "fr":
            subject = "Résumé Quotidien du Marché"
            content = f"""
            📊 Résumé Quotidien du Marché - {datetime.now().strftime('%d/%m/%Y')}
            
            Le marché marocain a clôturé la journée avec des performances variées.
            {len(market_data.get('quotes', []))} titres ont été négociés aujourd'hui.
            
            📈 Indices Principaux
            - MASI: Performance stable
            - MADEX: Légère hausse
            
            🔍 Points Clés
            - Volatilité modérée
            - Volume d'échanges normal
            - Sentiment du marché neutre
            """
        elif language == "ar":
            subject = "ملخص يومي للسوق"
            content = f"""
            📊 ملخص يومي للسوق - {datetime.now().strftime('%d/%m/%Y')}
            
            أغلق السوق المغربي اليوم بأداء متنوع.
            تم تداول {len(market_data.get('quotes', []))} سهم اليوم.
            
            📈 المؤشرات الرئيسية
            - MASI: أداء مستقر
            - MADEX: ارتفاع طفيف
            
            🔍 النقاط الرئيسية
            - تقلب معتدل
            - حجم تداول طبيعي
            - معنويات السوق محايدة
            """
        else:
            subject = "Daily Market Summary"
            content = f"""
            📊 Daily Market Summary - {datetime.now().strftime('%Y-%m-%d')}
            
            The Moroccan market closed the day with varied performance.
            {len(market_data.get('quotes', []))} stocks were traded today.
            
            📈 Key Indices
            - MASI: Stable performance
            - MADEX: Slight increase
            
            🔍 Key Points
            - Moderate volatility
            - Normal trading volume
            - Neutral market sentiment
            """
        
        return {
            "type": "daily_summary",
            "language": language,
            "subject": subject,
            "content": content,
            "market_data": market_data,
            "generated_at": datetime.now().isoformat(),
            "fallback": True
        }
    
    def _generate_fallback_company_analysis(self, ticker: str, language: str, company_data: Dict) -> Dict[str, Any]:
        """Generate fallback company analysis content"""
        if language == "fr":
            subject = f"Analyse de {ticker}"
            content = f"""
            📊 Analyse de {ticker}
            
            {ticker} affiche une performance stable sur le marché marocain.
            
            📈 Analyse Technique
            - Support: Niveau de soutien solide
            - Résistance: Objectif de résistance
            - Tendance: Tendance haussière modérée
            
            💼 Facteurs Fondamentaux
            - Bénéfices: Croissance stable
            - Dividendes: Rendement attractif
            - Perspectives: Outlook positif
            
            🔍 Recommandation
            Maintenir la position avec surveillance continue.
            """
        elif language == "ar":
            subject = f"تحليل {ticker}"
            content = f"""
            📊 تحليل {ticker}
            
            يظهر {ticker} أداء مستقر في السوق المغربي.
            
            📈 التحليل الفني
            - الدعم: مستوى دعم قوي
            - المقاومة: هدف مقاومة
            - الاتجاه: اتجاه صاعد معتدل
            
            💼 العوامل الأساسية
            - الأرباح: نمو مستقر
            - الأرباح الموزعة: عائد جذاب
            - التوقعات: نظرة إيجابية
            
            🔍 التوصية
            الحفاظ على الموقف مع مراقبة مستمرة.
            """
        else:
            subject = f"{ticker} Analysis"
            content = f"""
            📊 {ticker} Analysis
            
            {ticker} shows stable performance in the Moroccan market.
            
            📈 Technical Analysis
            - Support: Strong support level
            - Resistance: Resistance target
            - Trend: Moderate upward trend
            
            💼 Fundamental Factors
            - Earnings: Stable growth
            - Dividends: Attractive yield
            - Outlook: Positive outlook
            
            🔍 Recommendation
            Maintain position with continuous monitoring.
            """
        
        return {
            "type": "company_analysis",
            "ticker": ticker,
            "language": language,
            "subject": subject,
            "content": content,
            "company_data": company_data,
            "generated_at": datetime.now().isoformat(),
            "fallback": True
        }
    
    async def generate_content(self, content_type: str, language: str = "en", ticker: str = None, output_file: str = None) -> Dict[str, Any]:
        """Generate newsletter content based on type"""
        print(f"🚀 Generating {content_type} content in {language.upper()}")
        
        if content_type == "weekly":
            content = await self.generate_weekly_recap(language)
        elif content_type == "daily":
            content = await self.generate_daily_summary(language)
        elif content_type == "company":
            if not ticker:
                print("❌ Error: Ticker required for company analysis")
                return {}
            content = await self.generate_company_analysis(ticker, language)
        else:
            print(f"❌ Error: Unknown content type '{content_type}'")
            return {}
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            print(f"💾 Content saved to: {output_file}")
        
        return content

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate Newsletter Content')
    parser.add_argument('--type', type=str, choices=['weekly', 'daily', 'company'], default='weekly', help='Content type to generate')
    parser.add_argument('--language', type=str, choices=['en', 'fr', 'ar'], default='en', help='Language for content')
    parser.add_argument('--ticker', type=str, help='Company ticker for company analysis')
    parser.add_argument('--output', type=str, help='Output file path')
    
    args = parser.parse_args()
    
    # Validate ticker for company analysis
    if args.type == 'company' and not args.ticker:
        print("❌ Error: --ticker is required for company analysis")
        sys.exit(1)
    
    # Generate content
    generator = NewsletterContentGenerator()
    content = await generator.generate_content(
        content_type=args.type,
        language=args.language,
        ticker=args.ticker,
        output_file=args.output
    )
    
    if content:
        print("\n📄 Generated Content Preview:")
        print("=" * 50)
        print(f"Subject: {content.get('subject', 'N/A')}")
        print(f"Type: {content.get('type', 'N/A')}")
        print(f"Language: {content.get('language', 'N/A')}")
        print(f"Generated: {content.get('generated_at', 'N/A')}")
        print(f"Content Length: {len(content.get('content', ''))} characters")
        
        if content.get('fallback'):
            print("⚠️  Note: Using fallback content (AI not available)")
        
        print("\n📝 Content Preview:")
        print("-" * 30)
        content_preview = content.get('content', '')[:500]
        print(content_preview)
        if len(content.get('content', '')) > 500:
            print("...")
        
        print("\n✅ Content generation completed!")
    else:
        print("❌ Content generation failed")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main()) 