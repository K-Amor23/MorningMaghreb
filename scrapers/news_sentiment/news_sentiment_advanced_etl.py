
from ..base.scraper_interface import BaseScraper
from ..utils.http_helpers import make_request, add_delay
from ..utils.date_parsers import parse_date, extract_date_from_text
from ..utils.config_loader import get_scraper_config
from ..utils.data_validators import validate_dataframe, clean_dataframe
import pandas as pd
import logging
from typing import Dict, Any, Optional
#!/usr/bin/env python3
"""
Advanced News Sentiment ETL Pipeline
Enhanced sentiment analysis with NLP models for all 78 companies
"""

import asyncio
import aiohttp
import logging
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import hashlib
import time
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from database.connection import get_db_session
from models.company import SentimentType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_sentiment_etl.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SentimentConfig:
    """Sentiment analysis configuration"""
    batch_size: int = 20
    max_concurrent_requests: int = 10
    retry_attempts: int = 3
    retry_delay: int = 5
    timeout: int = 30
    progress_file: str = "sentiment_etl_progress.json"
    checkpoint_interval: int = 100
    nlp_model: str = "transformers"  # transformers, spacy, or custom
    confidence_threshold: float = 0.7

class AdvancedSentimentAnalyzer:
    """Advanced sentiment analysis with multiple NLP models"""
    
    def __init__(self, config: SentimentConfig):
        self.config = config
        self.models = {}
        self._load_nlp_models()
    
    def _load_nlp_models(self):
        """Load NLP models for sentiment analysis"""
        try:
            if self.config.nlp_model == "transformers":
                self._load_transformers_model()
            elif self.config.nlp_model == "spacy":
                self._load_spacy_model()
            else:
                self._load_custom_model()
        except Exception as e:
            logger.warning(f"Could not load NLP models: {e}, falling back to rule-based analysis")
            self.models = {}
    
    def _load_transformers_model(self):
        """Load Hugging Face transformers model"""
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
            
            # Load French and English sentiment models
            self.models["french"] = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                tokenizer="nlptown/bert-base-multilingual-uncased-sentiment"
            )
            
            self.models["english"] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            logger.info("✅ Transformers models loaded successfully")
            
        except ImportError:
            logger.warning("Transformers not available, using rule-based analysis")
        except Exception as e:
            logger.error(f"Error loading transformers model: {e}")
    
    def _load_spacy_model(self):
        """Load spaCy model for sentiment analysis"""
        try:
            import spacy
            
            # Load French and English models
            self.models["french"] = spacy.load("fr_core_news_sm")
            self.models["english"] = spacy.load("en_core_web_sm")
            
            logger.info("✅ spaCy models loaded successfully")
            
        except ImportError:
            logger.warning("spaCy not available, using rule-based analysis")
        except Exception as e:
            logger.error(f"Error loading spaCy model: {e}")
    
    def _load_custom_model(self):
        """Load custom sentiment analysis model"""
        # Implement custom model loading logic here
        logger.info("Custom model loading not implemented, using rule-based analysis")
    
    async def analyze_sentiment(self, text: str, language: str = "auto") -> Tuple[str, float, Dict[str, Any]]:
        """Analyze sentiment of text using multiple models"""
        if not text or len(text.strip()) < 10:
            return SentimentType.NEUTRAL, 0.5, {"method": "empty_text"}
        
        # Detect language if not specified
        if language == "auto":
            language = self._detect_language(text)
        
        # Try multiple analysis methods
        results = []
        
        # 1. Try transformers model
        if "transformers" in str(type(self.models.get(language, ""))):
            try:
                result = self.models[language](text[:512])  # Limit text length
                sentiment, confidence = self._parse_transformers_result(result)
                results.append(("transformers", sentiment, confidence))
            except Exception as e:
                logger.debug(f"Transformers analysis failed: {e}")
        
        # 2. Try spaCy model
        if "spacy" in str(type(self.models.get(language, ""))):
            try:
                doc = self.models[language](text)
                sentiment, confidence = self._analyze_spacy_sentiment(doc)
                results.append(("spacy", sentiment, confidence))
            except Exception as e:
                logger.debug(f"spaCy analysis failed: {e}")
        
        # 3. Rule-based analysis as fallback
        sentiment, confidence = self._rule_based_sentiment_analysis(text, language)
        results.append(("rule_based", sentiment, confidence))
        
        # Combine results using ensemble method
        final_sentiment, final_confidence, metadata = self._ensemble_sentiment(results)
        
        return final_sentiment, final_confidence, {
            "method": "ensemble",
            "language": language,
            "individual_results": results,
            "text_length": len(text),
            "confidence_threshold": self.config.confidence_threshold
        }
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Count French vs English words
        french_words = len(re.findall(r'\b(le|la|les|un|une|des|et|ou|mais|pour|avec|sur|dans|par|de|du|des|au|aux|ce|cette|ces|qui|que|quoi|où|quand|comment|pourquoi|comment|bien|très|plus|moins|grand|petit|bon|mauvais|nouveau|ancien|premier|dernier|seul|ensemble|toujours|jamais|souvent|rarement|maintenant|aujourd\'hui|demain|hier|semaine|mois|année|temps|jour|nuit|matin|soir|midi|minuit|heure|minute|seconde|fois|fois|fois|fois|fois|fois|fois|fois|fois|fois)\b', text.lower()))
        english_words = len(re.findall(r'\b(the|a|an|and|or|but|for|with|on|in|by|of|to|from|this|that|these|those|who|what|where|when|how|why|very|more|less|big|small|good|bad|new|old|first|last|only|together|always|never|often|rarely|now|today|tomorrow|yesterday|week|month|year|time|day|night|morning|evening|noon|midnight|hour|minute|second|time|time|time|time|time|time|time|time|time|time)\b', text.lower()))
        
        return "french" if french_words > english_words else "english"
    
    def _parse_transformers_result(self, result) -> Tuple[str, float]:
        """Parse transformers sentiment analysis result"""
        if isinstance(result, list) and len(result) > 0:
            result = result[0]
        
        label = result.get('label', '').lower()
        score = result.get('score', 0.5)
        
        # Map labels to sentiment types
        if 'positive' in label or '5' in label or '4' in label:
            return SentimentType.POSITIVE, score
        elif 'negative' in label or '1' in label or '2' in label:
            return SentimentType.NEGATIVE, score
        else:
            return SentimentType.NEUTRAL, score
    
    def _analyze_spacy_sentiment(self, doc) -> Tuple[str, float]:
        """Analyze sentiment using spaCy"""
        # Simple rule-based sentiment for spaCy
        positive_words = ['bon', 'excellent', 'positif', 'fort', 'hausse', 'croissance', 'profit', 'gain', 'succès']
        negative_words = ['mauvais', 'négatif', 'faible', 'baisse', 'perte', 'échec', 'problème', 'risque']
        
        text_lower = doc.text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return SentimentType.POSITIVE, min(0.9, 0.5 + (positive_count * 0.1))
        elif negative_count > positive_count:
            return SentimentType.NEGATIVE, min(0.9, 0.5 + (negative_count * 0.1))
        else:
            return SentimentType.NEUTRAL, 0.5
    
    def _rule_based_sentiment_analysis(self, text: str, language: str) -> Tuple[str, float]:
        """Rule-based sentiment analysis"""
        text_lower = text.lower()
        
        if language == "french":
            positive_words = [
                'hausse', 'croissance', 'profit', 'gain', 'succès', 'excellent', 'positif', 'fort',
                'bon', 'bien', 'amélioration', 'progrès', 'développement', 'expansion', 'montée',
                'augmentation', 'hausse', 'plus', 'mieux', 'supérieur', 'excellent', 'remarquable'
            ]
            negative_words = [
                'baisse', 'chute', 'perte', 'échec', 'problème', 'risque', 'négatif', 'faible',
                'mauvais', 'mal', 'dégradation', 'régression', 'contraction', 'chute', 'diminution',
                'moins', 'pire', 'inférieur', 'médiocre', 'décevant'
            ]
        else:  # English
            positive_words = [
                'rise', 'growth', 'profit', 'gain', 'success', 'excellent', 'positive', 'strong',
                'good', 'well', 'improvement', 'progress', 'development', 'expansion', 'increase',
                'up', 'better', 'superior', 'outstanding', 'remarkable'
            ]
            negative_words = [
                'fall', 'drop', 'loss', 'failure', 'problem', 'risk', 'negative', 'weak',
                'bad', 'poor', 'decline', 'regression', 'contraction', 'decrease', 'down',
                'worse', 'inferior', 'mediocre', 'disappointing'
            ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate sentiment score
        total_words = len(text.split())
        if total_words == 0:
            return SentimentType.NEUTRAL, 0.5
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        if positive_ratio > negative_ratio and positive_ratio > 0.01:
            confidence = min(0.9, 0.5 + (positive_ratio * 10))
            return SentimentType.POSITIVE, confidence
        elif negative_ratio > positive_ratio and negative_ratio > 0.01:
            confidence = min(0.9, 0.5 + (negative_ratio * 10))
            return SentimentType.NEGATIVE, confidence
        else:
            return SentimentType.NEUTRAL, 0.5
    
    def _ensemble_sentiment(self, results: List[Tuple[str, str, float]]) -> Tuple[str, float, Dict[str, Any]]:
        """Combine multiple sentiment analysis results"""
        if not results:
            return SentimentType.NEUTRAL, 0.5, {"method": "no_results"}
        
        # Weight different methods
        method_weights = {
            "transformers": 0.6,
            "spacy": 0.3,
            "rule_based": 0.1
        }
        
        sentiment_scores = {SentimentType.POSITIVE: 0.0, SentimentType.NEGATIVE: 0.0, SentimentType.NEUTRAL: 0.0}
        
        for method, sentiment, confidence in results:
            weight = method_weights.get(method, 0.1)
            sentiment_scores[sentiment] += confidence * weight
        
        # Determine final sentiment
        final_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        final_confidence = sentiment_scores[final_sentiment]
        
        # Apply confidence threshold
        if final_confidence < self.config.confidence_threshold:
            final_sentiment = SentimentType.NEUTRAL
            final_confidence = 0.5
        
        return final_sentiment, final_confidence, {
            "ensemble_scores": sentiment_scores,
            "method_weights": method_weights
        }

class AdvancedNewsSentimentETL:
    """Advanced news sentiment ETL pipeline"""
    
    def __init__(self, config: SentimentConfig):
        self.config = config
        self.sentiment_analyzer = AdvancedSentimentAnalyzer(config)
        self.progress = self._load_progress()
        self.companies = self._get_all_companies()
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
    def _load_progress(self) -> Dict[str, Any]:
        """Load ETL progress from file"""
        try:
            if os.path.exists(self.config.progress_file):
                with open(self.config.progress_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load progress file: {e}")
        
        return {
            "started_at": datetime.now().isoformat(),
            "total_companies": 0,
            "processed_companies": 0,
            "failed_companies": 0,
            "total_articles": 0,
            "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
            "last_checkpoint": None,
            "company_status": {}
        }
    
    def _save_progress(self):
        """Save ETL progress to file"""
        try:
            self.progress["last_updated"] = datetime.now().isoformat()
            with open(self.config.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    async def _get_all_companies(self) -> List[str]:
        """Get all company tickers from database"""
        async with get_db_session() as session:
            result = await session.execute(
                text("SELECT ticker FROM companies WHERE is_active = TRUE ORDER BY ticker")
            )
            return [row.ticker for row in result.fetchall()]
    
    async def run_sentiment_etl(self):
        """Main sentiment ETL pipeline execution"""
        logger.info(f"🚀 Starting Advanced News Sentiment ETL for {len(self.companies)} companies")
        
        start_time = time.time()
        self.progress["total_companies"] = len(self.companies)
        self.progress["started_at"] = datetime.now().isoformat()
        
        try:
            # Process companies in batches
            for i in range(0, len(self.companies), self.config.batch_size):
                batch = self.companies[i:i + self.config.batch_size]
                logger.info(f"Processing batch {i//self.config.batch_size + 1}: {batch}")
                
                # Process batch concurrently
                tasks = [self._process_company_sentiment(ticker) for ticker in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update progress
                for ticker, result in zip(batch, results):
                    if isinstance(result, Exception):
                        self.progress["failed_companies"] += 1
                        self.progress["company_status"][ticker] = "failed"
                        logger.error(f"Failed to process {ticker}: {result}")
                    else:
                        self.progress["processed_companies"] += 1
                        self.progress["total_articles"] += result.get("articles_processed", 0)
                        self.progress["company_status"][ticker] = "completed"
                        
                        # Update sentiment distribution
                        sentiment_dist = result.get("sentiment_distribution", {})
                        for sentiment, count in sentiment_dist.items():
                            self.progress["sentiment_distribution"][sentiment] += count
                
                # Save checkpoint
                if (i + self.config.batch_size) % self.config.checkpoint_interval == 0:
                    self._save_progress()
                    logger.info(f"Checkpoint saved: {self.progress['processed_companies']}/{self.progress['total_companies']} companies processed")
            
            # Final progress save
            self._save_progress()
            
            # Generate final report
            await self._generate_sentiment_report(start_time)
            
        except Exception as e:
            logger.error(f"Sentiment ETL pipeline failed: {e}")
            self.progress["status"] = "failed"
            self.progress["error"] = str(e)
            self._save_progress()
            raise
    
    async def _process_company_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Process sentiment analysis for a single company"""
        async with self.semaphore:
            logger.info(f"Processing sentiment for {ticker}")
            
            try:
                # Get recent news articles for the company
                articles = await self._get_company_news(ticker)
                
                if not articles:
                    logger.info(f"No recent news found for {ticker}")
                    return {"articles_processed": 0, "sentiment_distribution": {}}
                
                # Analyze sentiment for each article
                processed_articles = []
                sentiment_distribution = {"positive": 0, "negative": 0, "neutral": 0}
                
                for article in articles:
                    sentiment_result = await self._analyze_article_sentiment(article)
                    if sentiment_result:
                        processed_articles.append(sentiment_result)
                        sentiment_distribution[sentiment_result["sentiment"]] += 1
                
                # Store sentiment results
                await self._store_sentiment_results(ticker, processed_articles)
                
                logger.info(f"✅ {ticker}: {len(processed_articles)} articles processed")
                return {
                    "articles_processed": len(processed_articles),
                    "sentiment_distribution": sentiment_distribution,
                    "status": "success"
                }
                
            except Exception as e:
                logger.error(f"❌ {ticker}: {e}")
                raise
    
    async def _get_company_news(self, ticker: str) -> List[Dict[str, Any]]:
        """Get recent news articles for a company"""
        async with get_db_session() as session:
            # Get news from the last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            result = await session.execute(
                text("""
                    SELECT id, title, content, source, published_at, url
                    FROM company_news 
                    WHERE company_id = (SELECT id FROM companies WHERE ticker = :ticker)
                    AND published_at >= :start_date
                    AND sentiment IS NULL
                    ORDER BY published_at DESC
                    LIMIT 50
                """),
                {"ticker": ticker, "start_date": thirty_days_ago}
            )
            
            articles = []
            for row in result.fetchall():
                articles.append({
                    "id": row.id,
                    "title": row.title,
                    "content": row.content,
                    "source": row.source,
                    "published_at": row.published_at,
                    "url": row.url
                })
            
            return articles
    
    async def _analyze_article_sentiment(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze sentiment for a single article"""
        try:
            # Combine title and content for analysis
            text = f"{article['title']} {article['content']}"
            
            # Analyze sentiment
            sentiment, confidence, metadata = await asyncio.to_thread(
                self.sentiment_analyzer.analyze_sentiment, text
            )
            
            return {
                "article_id": article["id"],
                "sentiment": sentiment,
                "confidence": confidence,
                "metadata": metadata,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for article {article['id']}: {e}")
            return None
    
    async def _store_sentiment_results(self, ticker: str, sentiment_results: List[Dict[str, Any]]):
        """Store sentiment analysis results in database"""
        async with get_db_session() as session:
            for result in sentiment_results:
                try:
                    await session.execute(
                        text("""
                            UPDATE company_news 
                            SET sentiment = :sentiment, 
                                sentiment_confidence = :confidence,
                                sentiment_metadata = :metadata,
                                sentiment_analyzed_at = NOW()
                            WHERE id = :article_id
                        """),
                        {
                            "sentiment": result["sentiment"],
                            "confidence": result["confidence"],
                            "metadata": json.dumps(result["metadata"]),
                            "article_id": result["article_id"]
                        }
                    )
                except Exception as e:
                    logger.error(f"Error storing sentiment for article {result['article_id']}: {e}")
                    continue
            
            await session.commit()
    
    async def _generate_sentiment_report(self, start_time: float):
        """Generate sentiment ETL completion report"""
        end_time = time.time()
        duration = end_time - start_time
        
        total_articles = self.progress["total_articles"]
        sentiment_dist = self.progress["sentiment_distribution"]
        
        report = {
            "sentiment_etl_completion_report": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "duration_formatted": str(timedelta(seconds=int(duration))),
                "total_companies": self.progress["total_companies"],
                "processed_companies": self.progress["processed_companies"],
                "failed_companies": self.progress["failed_companies"],
                "success_rate": (self.progress["processed_companies"] / self.progress["total_companies"]) * 100 if self.progress["total_companies"] > 0 else 0,
                "total_articles_processed": total_articles,
                "articles_per_second": total_articles / duration if duration > 0 else 0,
                "sentiment_distribution": sentiment_dist,
                "sentiment_percentages": {
                    "positive": (sentiment_dist["positive"] / total_articles * 100) if total_articles > 0 else 0,
                    "negative": (sentiment_dist["negative"] / total_articles * 100) if total_articles > 0 else 0,
                    "neutral": (sentiment_dist["neutral"] / total_articles * 100) if total_articles > 0 else 0
                },
                "nlp_model_used": self.config.nlp_model,
                "confidence_threshold": self.config.confidence_threshold
            }
        }
        
        # Save report
        report_file = f"sentiment_etl_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Sentiment ETL Report generated: {report_file}")
        logger.info(f"✅ Sentiment ETL completed in {duration:.2f} seconds")
        logger.info(f"📈 Success rate: {report['sentiment_etl_completion_report']['success_rate']:.1f}%")
        logger.info(f"📄 Total articles processed: {total_articles}")
        logger.info(f"😊 Sentiment distribution: {sentiment_dist}")

async def main():
    """Main sentiment ETL execution function"""
    config = SentimentConfig(
        batch_size=20,
        max_concurrent_requests=10,
        retry_attempts=3,
        retry_delay=5,
        timeout=30,
        nlp_model="transformers",
        confidence_threshold=0.7
    )
    
    etl = AdvancedNewsSentimentETL(config)
    
    try:
        await etl.run_sentiment_etl()
        logger.info("🎉 Advanced News Sentiment ETL completed successfully!")
    except Exception as e:
        logger.error(f"💥 Sentiment ETL failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 

class NewsSentimentAdvancedEtlScraper(BaseScraper):
    """News Sentiment Advanced Etl Scraper"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.config = get_scraper_config("news_sentiment_advanced_etl")
    
    def fetch(self) -> pd.DataFrame:
        """Fetch data from source"""
        # TODO: Implement fetch logic
        return pd.DataFrame()
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate fetched data"""
        # TODO: Implement validation logic
        return True
