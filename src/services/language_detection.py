"""
Language Detection and Translation Service.
Auto-detects language and provides multi-language support.
"""

import logging
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)


class LanguageDetection:
    """
    Service for language detection and multi-language support.
    """

    SUPPORTED_LANGUAGES = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "zh": "Chinese",
        "ja": "Japanese",
        "pt": "Portuguese",
        "ru": "Russian",
        "it": "Italian",
        "ko": "Korean",
    }

    # Language detection keywords
    LANGUAGE_KEYWORDS = {
        "en": ["the", "and", "is", "to", "of", "in", "for", "you", "be", "that"],
        "es": ["el", "la", "de", "que", "y", "a", "en", "es", "un", "por"],
        "fr": ["le", "de", "un", "et", "à", "être", "en", "que", "du", "avoir"],
        "de": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich"],
        "zh": ["的", "一", "是", "在", "不", "了", "有", "和", "人", "这"],
        "ja": ["が", "を", "に", "へ", "と", "は", "の", "から", "まで", "で"],
        "pt": ["de", "a", "o", "que", "e", "do", "da", "em", "um", "para"],
        "ru": ["и", "в", "во", "не", "что", "он", "на", "я", "с", "со"],
        "it": ["il", "di", "da", "che", "e", "a", "un", "in", "si", "gli"],
        "ko": ["의", "가", "이", "을", "로", "에", "과", "도", "는", "한"],
    }

    def __init__(self):
        """Initialize language detection service."""
        self.try_import_langdetect()

    def try_import_langdetect(self):
        """Attempt to import langdetect library."""
        try:
            from langdetect import detect, detect_langs
            self.detect = detect
            self.detect_langs = detect_langs
            self.langdetect_available = True
            logger.info("langdetect library available")
        except ImportError:
            self.langdetect_available = False
            logger.warning("langdetect not installed. Using keyword-based detection.")
            self.detect = None
            self.detect_langs = None

    def detect_language(self, text: str) -> Dict[str, any]:
        """
        Detect the language of provided text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with detected language info
        """
        if not text or len(text.strip()) < 10:
            return {
                "language": "unknown",
                "language_name": "Unknown",
                "confidence": 0.0,
                "is_confident": False
            }
        
        # Try langdetect first
        if self.langdetect_available and self.detect:
            try:
                lang = self.detect(text)
                if lang in self.SUPPORTED_LANGUAGES:
                    return {
                        "language": lang,
                        "language_name": self.SUPPORTED_LANGUAGES[lang],
                        "confidence": 0.85,
                        "is_confident": True
                    }
            except Exception as e:
                logger.warning(f"langdetect error: {e}")
        
        # Fallback to keyword-based detection
        return self._keyword_detect(text)

    def _keyword_detect(self, text: str) -> Dict[str, any]:
        """
        Detect language using keyword matching.
        
        Args:
            text: Text to analyze
        
        Returns:
            Detection result
        """
        text_lower = text.lower()
        text_words = set(text_lower.split())
        
        scores = {}
        
        for lang, keywords in self.LANGUAGE_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in text_words)
            score = matches / len(keywords) if keywords else 0
            scores[lang] = score
        
        if scores:
            best_lang = max(scores, key=scores.get)
            confidence = scores[best_lang]
            
            return {
                "language": best_lang,
                "language_name": self.SUPPORTED_LANGUAGES.get(best_lang, "Unknown"),
                "confidence": min(confidence, 1.0),
                "is_confident": confidence > 0.3
            }
        
        return {
            "language": "unknown",
            "language_name": "Unknown",
            "confidence": 0.0,
            "is_confident": False
        }

    def translate(self, text: str, target_language: str, ai_service) -> str:
        """
        Translate text to target language using AI.
        
        Args:
            text: Text to translate
            target_language: Target language code or name
            ai_service: AI service for translation
        
        Returns:
            Translated text
        """
        # Resolve language name to code
        target_lang_code = target_language
        if target_language in self.SUPPORTED_LANGUAGES.values():
            target_lang_code = [k for k, v in self.SUPPORTED_LANGUAGES.items() 
                               if v.lower() == target_language.lower()][0]
        
        if target_lang_code not in self.SUPPORTED_LANGUAGES:
            return f"Language {target_language} not supported."
        
        target_lang_name = self.SUPPORTED_LANGUAGES[target_lang_code]
        
        prompt = (
            f"Translate the following text to {target_lang_name}. "
            f"Keep formatting intact. Respond ONLY with the translation.\n\n"
            f"{text}"
        )
        
        try:
            translated = ai_service.call_ai(prompt)
            return translated
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return f"Translation failed: {str(e)}"

    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages."""
        return self.SUPPORTED_LANGUAGES.copy()

    def get_language_info(self, text: str) -> str:
        """
        Get formatted language detection info.
        
        Args:
            text: Text to analyze
        
        Returns:
            Formatted info string
        """
        detection = self.detect_language(text)
        
        lang = detection["language"]
        lang_name = detection["language_name"]
        confidence = detection["confidence"]
        is_confident = detection["is_confident"]
        
        if not is_confident:
            return (
                f"🌐 *Language Detection*\n\n"
                f"Detected: {lang_name} ({lang})\n"
                f"Confidence: {confidence*100:.0f}%\n"
                f"⚠️ Low confidence - manual verification recommended"
            )
        
        return (
            f"🌐 *Language Detection*\n\n"
            f"Detected: {lang_name} ({lang})\n"
            f"Confidence: {confidence*100:.0f}%"
        )

    def prepare_for_processing(self, text: str, ai_service=None) -> Dict:
        """
        Prepare text for processing with language info.
        
        Args:
            text: Text to prepare
            ai_service: Optional AI service
        
        Returns:
            Processed data with language info
        """
        detection = self.detect_language(text)
        
        return {
            "original_text": text,
            "language": detection["language"],
            "language_name": detection["language_name"],
            "confidence": detection["confidence"],
            "is_confident": detection["is_confident"],
            "text_to_process": text  # Will be translated if needed
        }

    def auto_translate_if_needed(self, text: str, target_lang: str = "en", ai_service=None) -> str:
        """
        Auto-translate text if it's not in target language.
        
        Args:
            text: Text to process
            target_lang: Target language code
            ai_service: AI service
        
        Returns:
            Text in target language (or original if already in target)
        """
        detection = self.detect_language(text)
        detected_lang = detection["language"]
        
        if detected_lang == target_lang:
            return text
        
        if detected_lang == "unknown" or not detection["is_confident"]:
            return text  # Don't translate if detection is uncertain
        
        if ai_service:
            return self.translate(text, target_lang, ai_service)
        
        return text
