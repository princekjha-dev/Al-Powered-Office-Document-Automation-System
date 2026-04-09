"""
Document Auto-Categorization and Smart Tagging Service.
Automatically categorizes documents and generates relevant tags using AI.
"""

import logging
import json
import os
from typing import List, Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentCategorization:
    """
    Service for automatic document categorization and tag generation.
    Identifies document type and generates relevant metadata.
    """

    # Predefined document categories
    CATEGORIES = {
        "contract": ["agreement", "terms", "parties", "signatures", "obligations", "clauses"],
        "report": ["summary", "findings", "analysis", "conclusion", "recommendations", "data"],
        "proposal": ["objectives", "timeline", "budget", "deliverables", "team", "pricing"],
        "invoice": ["invoice", "amount", "payment", "date", "items", "total", "customer"],
        "memo": ["memorandum", "to:", "from:", "subject:", "urgent", "action required"],
        "resume": ["experience", "education", "skills", "employment", "qualification", "background"],
        "manual": ["instructions", "steps", "procedure", "guide", "how to", "warning", "caution"],
        "specification": ["requirements", "specifications", "technical", "implementation", "interface"],
        "newsletter": ["news", "updates", "announcement", "subscribers", "highlights", "edition"],
        "email": ["from:", "to:", "subject:", "regards", "sincerely", "message"],
    }

    def __init__(self):
        """Initialize categorization service."""
        pass

    def categorize_document(self, text: str, ai_service=None) -> Tuple[str, float]:
        """
        Categorize a document based on content analysis.
        
        Args:
            text: Document text
            ai_service: Optional AI service for enhanced categorization
        
        Returns:
            Tuple of (category, confidence_score)
        """
        # First try keyword-based categorization
        scores = {}
        text_lower = text.lower()
        
        # Score each category
        for category, keywords in self.CATEGORIES.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            score = matches / len(keywords) if keywords else 0
            scores[category] = score
        
        # Get highest scoring category
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = scores[best_category]
            
            # Use AI for verification if confidence is low or service available
            if confidence < 0.5 and ai_service:
                return self._ai_categorize(text, ai_service)
            
            return best_category, min(confidence, 1.0)
        
        return "other", 0.5

    def _ai_categorize(self, text: str, ai_service) -> Tuple[str, float]:
        """
        Use AI service to categorize document.
        
        Args:
            text: Document text
            ai_service: AI service
        
        Returns:
            Tuple of (category, confidence)
        """
        categories_list = ", ".join(self.CATEGORIES.keys())
        
        prompt = (
            f"Classify this document into ONE of these categories: {categories_list}\n\n"
            f"Document preview:\n{text[:500]}\n\n"
            f"Respond with ONLY the category name and your confidence (0-100).\n"
            f"Format: CATEGORY,CONFIDENCE"
        )
        
        try:
            response = ai_service.call_ai(prompt).strip()
            parts = response.split(',')
            
            if len(parts) >= 2:
                category = parts[0].strip().lower()
                confidence = float(parts[1].strip()) / 100.0
                
                if category in self.CATEGORIES:
                    return category, min(confidence, 1.0)
        except Exception as e:
            logger.error(f"AI categorization error: {e}")
        
        return "other", 0.5

    def generate_tags(self, text: str, category: str = "", ai_service=None) -> List[str]:
        """
        Generate relevant tags for a document.
        
        Args:
            text: Document text
            category: Document category
            ai_service: Optional AI service for enhanced tag generation
        
        Returns:
            List of tags
        """
        tags = set()
        
        # Add category as tag
        if category and category != "other":
            tags.add(category)
        
        # Extract tags using keywords
        text_lower = text.lower()
        text_words = set(text_lower.split())
        
        # Common business tags
        business_tags = {
            "urgent": ["urgent", "asap", "immediate", "priority"],
            "financial": ["budget", "cost", "price", "payment", "invoice", "revenue"],
            "legal": ["contract", "agreement", "liability", "compliance", "legal"],
            "technical": ["technical", "api", "server", "database", "system", "code"],
            "marketing": ["marketing", "campaign", "audience", "brand", "promotion"],
            "hr": ["employee", "hiring", "salary", "benefits", "hr", "human resources"],
            "sales": ["sales", "customer", "deal", "proposal", "revenue", "target"],
            "operations": ["process", "procedure", "workflow", "guidelines", "operations"],
        }
        
        for tag, keywords in business_tags.items():
            if any(keyword in text_words for keyword in keywords):
                tags.add(tag)
        
        # Use AI for advanced tag generation if available
        if ai_service:
            ai_tags = self._ai_generate_tags(text, list(tags), ai_service)
            tags.update(ai_tags)
        
        return list(tags)

    def _ai_generate_tags(self, text: str, existing_tags: List[str], ai_service) -> List[str]:
        """
        Use AI to generate additional tags.
        
        Args:
            text: Document text
            existing_tags: Tags already identified
            ai_service: AI service for tag generation
        
        Returns:
            Additional tags
        """
        existing_str = ", ".join(existing_tags) if existing_tags else "none"
        
        prompt = (
            f"Generate 3-5 short, specific tags for this document.\n"
            f"Avoid generic tags. Focus on key topics, themes, or purposes.\n"
            f"Already have: {existing_str}\n\n"
            f"Document preview:\n{text[:500]}\n\n"
            f"Respond with ONLY comma-separated tags (lowercase, no spaces)."
        )
        
        try:
            response = ai_service.call_ai(prompt).strip()
            tags = [tag.strip().lower().replace(" ", "_") for tag in response.split(",")]
            return [tag for tag in tags if tag and len(tag) > 2]
        except Exception as e:
            logger.error(f"AI tag generation error: {e}")
            return []

    def analyze_document(self, text: str, ai_service=None) -> Dict:
        """
        Perform complete document analysis (categorization + tagging).
        
        Args:
            text: Document text
            ai_service: Optional AI service
        
        Returns:
            Analysis dictionary
        """
        category, confidence = self.categorize_document(text, ai_service)
        tags = self.generate_tags(text, category, ai_service)
        
        # Calculate document statistics
        word_count = len(text.split())
        line_count = len(text.split('\n'))
        char_count = len(text)
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "confidence": confidence,
            "tags": tags,
            "statistics": {
                "words": word_count,
                "lines": line_count,
                "characters": char_count,
                "pages_estimated": max(1, word_count // 250),
            }
        }
        
        return analysis

    def get_categorization_report(self, text: str, ai_service=None) -> str:
        """
        Generate a formatted categorization report.
        
        Args:
            text: Document text
            ai_service: Optional AI service
        
        Returns:
            Formatted report string
        """
        analysis = self.analyze_document(text, ai_service)
        
        category = analysis["category"]
        confidence = analysis["confidence"]
        tags = analysis["tags"]
        stats = analysis["statistics"]
        
        report = (
            f"📂 *Document Analysis*\n\n"
            f"*Category:* {category.upper()}\n"
            f"*Confidence:* {confidence*100:.0f}%\n\n"
            f"*Tags:* {', '.join(tags)}\n\n"
            f"*Statistics:*\n"
            f"Words: {stats['words']}\n"
            f"Lines: {stats['lines']}\n"
            f"Est. Pages: {stats['pages_estimated']}"
        )
        
        return report

    def save_analysis(self, analysis: Dict, filepath: str) -> bool:
        """
        Save analysis to file.
        
        Args:
            analysis: Analysis result
            filepath: Output filepath
        
        Returns:
            True if successful
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Save analysis error: {e}")
            return False
