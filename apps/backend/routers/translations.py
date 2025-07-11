from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from pydantic import BaseModel
import hashlib

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/translations", tags=["Multilingual Support"])

# Request/Response Models
class TranslationRequest(BaseModel):
    text: str
    target_language: str  # 'en', 'fr', 'ar'
    source_language: Optional[str] = None  # Auto-detect if not provided
    context: Optional[str] = None  # 'financial', 'market', 'general'

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence_score: float
    translation_provider: str
    cached: bool = False

class LanguagePreferenceRequest(BaseModel):
    language: str  # 'en', 'fr', 'ar'

class ContentTranslationRequest(BaseModel):
    content_type: str  # 'ai_summary', 'news_article', 'report', 'ui_text'
    content_id: Optional[str] = None
    target_language: str
    include_original: bool = False

# Mock database functions (replace with actual Supabase calls)
async def get_user_language_preference(user_id: str) -> str:
    """Get user's language preference"""
    # Mock implementation - replace with actual database query
    return "en"

async def update_user_language_preference(user_id: str, language: str):
    """Update user's language preference"""
    # Mock implementation
    logger.info(f"User {user_id} language preference updated to {language}")

async def get_cached_translation(source_text: str, source_lang: str, target_lang: str) -> Optional[Dict[str, Any]]:
    """Get cached translation if available"""
    # Mock implementation - replace with actual database query
    cache_key = hashlib.md5(f"{source_text}{source_lang}{target_lang}".encode()).hexdigest()
    
    # Mock cache hit
    if cache_key.startswith("a"):  # 1/16 chance of cache hit for demo
        return {
            "translated_text": f"Translated: {source_text}",
            "confidence_score": 0.95,
            "translation_provider": "openai",
            "cached": True
        }
    return None

async def cache_translation(source_text: str, source_lang: str, target_lang: str, translated_text: str, confidence: float):
    """Cache translation for future use"""
    # Mock implementation
    logger.info(f"Caching translation: {source_lang} -> {target_lang}")

async def translate_with_ai(text: str, source_lang: str, target_lang: str, context: str = "general") -> Dict[str, Any]:
    """Translate text using AI service"""
    # Mock AI translation - replace with actual OpenAI/DeepL API call
    translations = {
        "en": {
            "fr": {
                "financial": f"Traduction financière: {text}",
                "market": f"Traduction marché: {text}",
                "general": f"Traduction générale: {text}"
            },
            "ar": {
                "financial": f"ترجمة مالية: {text}",
                "market": f"ترجمة السوق: {text}",
                "general": f"ترجمة عامة: {text}"
            }
        },
        "fr": {
            "en": {
                "financial": f"Financial translation: {text}",
                "market": f"Market translation: {text}",
                "general": f"General translation: {text}"
            },
            "ar": {
                "financial": f"ترجمة مالية: {text}",
                "market": f"ترجمة السوق: {text}",
                "general": f"ترجمة عامة: {text}"
            }
        },
        "ar": {
            "en": {
                "financial": f"Financial translation: {text}",
                "market": f"Market translation: {text}",
                "general": f"General translation: {text}"
            },
            "fr": {
                "financial": f"Traduction financière: {text}",
                "market": f"Traduction marché: {text}",
                "general": f"Traduction générale: {text}"
            }
        }
    }
    
    # Get translation based on context
    context_translations = translations.get(source_lang, {}).get(target_lang, {})
    translated_text = context_translations.get(context, context_translations.get("general", f"Translation: {text}"))
    
    return {
        "translated_text": translated_text,
        "confidence_score": 0.92,
        "translation_provider": "openai"
    }

# Authentication dependency (mock)
async def get_current_user() -> dict:
    """Get current authenticated user"""
    return {"id": "mock_user_id"}

# Translation Endpoints
@router.post("/translate", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    user: dict = Depends(get_current_user)
):
    """Translate text to target language"""
    try:
        # Validate target language
        valid_languages = ["en", "fr", "ar"]
        if request.target_language not in valid_languages:
            raise HTTPException(status_code=400, detail=f"Invalid target language. Must be one of: {valid_languages}")
        
        # Auto-detect source language if not provided
        source_language = request.source_language or "en"
        
        # Check cache first
        cached_translation = await get_cached_translation(
            request.text, source_language, request.target_language
        )
        
        if cached_translation:
            return TranslationResponse(
                original_text=request.text,
                translated_text=cached_translation["translated_text"],
                source_language=source_language,
                target_language=request.target_language,
                confidence_score=cached_translation["confidence_score"],
                translation_provider=cached_translation["translation_provider"],
                cached=True
            )
        
        # Translate with AI
        translation_result = await translate_with_ai(
            request.text, 
            source_language, 
            request.target_language, 
            request.context or "general"
        )
        
        # Cache the translation
        await cache_translation(
            request.text,
            source_language,
            request.target_language,
            translation_result["translated_text"],
            translation_result["confidence_score"]
        )
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translation_result["translated_text"],
            source_language=source_language,
            target_language=request.target_language,
            confidence_score=translation_result["confidence_score"],
            translation_provider=translation_result["translation_provider"],
            cached=False
        )
        
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate text")

@router.post("/batch-translate", response_model=List[TranslationResponse])
async def batch_translate(
    requests: List[TranslationRequest],
    user: dict = Depends(get_current_user)
):
    """Translate multiple texts in batch"""
    try:
        translations = []
        
        for request in requests:
            # Validate target language
            valid_languages = ["en", "fr", "ar"]
            if request.target_language not in valid_languages:
                raise HTTPException(status_code=400, detail=f"Invalid target language: {request.target_language}")
            
            # Auto-detect source language if not provided
            source_language = request.source_language or "en"
            
            # Check cache first
            cached_translation = await get_cached_translation(
                request.text, source_language, request.target_language
            )
            
            if cached_translation:
                translations.append(TranslationResponse(
                    original_text=request.text,
                    translated_text=cached_translation["translated_text"],
                    source_language=source_language,
                    target_language=request.target_language,
                    confidence_score=cached_translation["confidence_score"],
                    translation_provider=cached_translation["translation_provider"],
                    cached=True
                ))
            else:
                # Translate with AI
                translation_result = await translate_with_ai(
                    request.text, 
                    source_language, 
                    request.target_language, 
                    request.context or "general"
                )
                
                # Cache the translation
                await cache_translation(
                    request.text,
                    source_language,
                    request.target_language,
                    translation_result["translated_text"],
                    translation_result["confidence_score"]
                )
                
                translations.append(TranslationResponse(
                    original_text=request.text,
                    translated_text=translation_result["translated_text"],
                    source_language=source_language,
                    target_language=request.target_language,
                    confidence_score=translation_result["confidence_score"],
                    translation_provider=translation_result["translation_provider"],
                    cached=False
                ))
        
        return translations
        
    except Exception as e:
        logger.error(f"Error in batch translation: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate texts")

# Language Preference Management
@router.get("/preference")
async def get_language_preference(user: dict = Depends(get_current_user)):
    """Get user's language preference"""
    try:
        language = await get_user_language_preference(user["id"])
        return {"language": language}
        
    except Exception as e:
        logger.error(f"Error getting language preference: {e}")
        raise HTTPException(status_code=500, detail="Failed to get language preference")

@router.post("/preference")
async def update_language_preference(
    request: LanguagePreferenceRequest,
    user: dict = Depends(get_current_user)
):
    """Update user's language preference"""
    try:
        # Validate language
        valid_languages = ["en", "fr", "ar"]
        if request.language not in valid_languages:
            raise HTTPException(status_code=400, detail=f"Invalid language. Must be one of: {valid_languages}")
        
        await update_user_language_preference(user["id"], request.language)
        
        return {"message": "Language preference updated successfully", "language": request.language}
        
    except Exception as e:
        logger.error(f"Error updating language preference: {e}")
        raise HTTPException(status_code=500, detail="Failed to update language preference")

# Content Translation
@router.post("/content", response_model=Dict[str, Any])
async def translate_content(
    request: ContentTranslationRequest,
    user: dict = Depends(get_current_user)
):
    """Translate specific content types (AI summaries, news articles, etc.)"""
    try:
        # Validate content type
        valid_content_types = ["ai_summary", "news_article", "report", "ui_text"]
        if request.content_type not in valid_content_types:
            raise HTTPException(status_code=400, detail=f"Invalid content type. Must be one of: {valid_content_types}")
        
        # Validate target language
        valid_languages = ["en", "fr", "ar"]
        if request.target_language not in valid_languages:
            raise HTTPException(status_code=400, detail=f"Invalid target language. Must be one of: {valid_languages}")
        
        # Mock content retrieval and translation
        content_data = await get_mock_content(request.content_type, request.content_id)
        
        translated_content = {}
        for key, value in content_data.items():
            if isinstance(value, str):
                # Translate text content
                translation_result = await translate_with_ai(
                    value, "en", request.target_language, "financial"
                )
                translated_content[key] = translation_result["translated_text"]
            else:
                translated_content[key] = value
        
        result = {
            "content_type": request.content_type,
            "content_id": request.content_id,
            "target_language": request.target_language,
            "translated_content": translated_content
        }
        
        if request.include_original:
            result["original_content"] = content_data
        
        return result
        
    except Exception as e:
        logger.error(f"Error translating content: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate content")

# Language Detection
@router.post("/detect")
async def detect_language(text: str):
    """Detect the language of input text"""
    try:
        # Mock language detection - replace with actual language detection service
        # Simple heuristic based on character sets
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        french_chars = sum(1 for char in text.lower() if char in 'àâäéèêëïîôöùûüÿç')
        
        if arabic_chars > len(text) * 0.3:
            detected_lang = "ar"
            confidence = 0.95
        elif french_chars > len(text) * 0.1:
            detected_lang = "fr"
            confidence = 0.85
        else:
            detected_lang = "en"
            confidence = 0.90
        
        return {
            "detected_language": detected_lang,
            "confidence": confidence,
            "text_length": len(text)
        }
        
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect language")

# Translation Statistics
@router.get("/stats")
async def get_translation_stats(user: dict = Depends(get_current_user)):
    """Get translation usage statistics"""
    try:
        # Mock translation statistics
        stats = {
            "total_translations": 15420,
            "translations_by_language": {
                "en_to_fr": 8230,
                "en_to_ar": 4560,
                "fr_to_en": 2630
            },
            "cache_hit_rate": 0.75,
            "average_confidence": 0.92,
            "most_translated_content": "ai_summary"
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting translation stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get translation statistics")

# Helper function to get mock content
async def get_mock_content(content_type: str, content_id: Optional[str] = None) -> Dict[str, Any]:
    """Get mock content for translation"""
    if content_type == "ai_summary":
        return {
            "title": "AI Analysis Summary",
            "summary": "This company demonstrates strong financial performance with consistent revenue growth and solid profitability metrics. The company maintains a healthy balance sheet with manageable debt levels and attractive valuation ratios.",
            "key_points": [
                "Strong revenue growth",
                "Healthy balance sheet",
                "Attractive valuation"
            ]
        }
    elif content_type == "news_article":
        return {
            "headline": "Market Update: Banking Sector Performance",
            "content": "The banking sector showed mixed performance this quarter, with some institutions reporting strong earnings while others faced challenges from regulatory changes.",
            "summary": "Mixed performance in banking sector"
        }
    elif content_type == "report":
        return {
            "title": "Financial Analysis Report",
            "executive_summary": "This comprehensive analysis reveals positive trends in the company's financial health and market position.",
            "conclusion": "The company is well-positioned for future growth"
        }
    else:  # ui_text
        return {
            "dashboard_title": "Market Dashboard",
            "welcome_message": "Welcome to your personalized market dashboard",
            "navigation_labels": {
                "markets": "Markets",
                "portfolio": "Portfolio",
                "news": "News",
                "settings": "Settings"
            }
        } 