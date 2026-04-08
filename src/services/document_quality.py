"""
Document Preview and Quality Scoring Service.
Provides preview generation and quality metrics for documents.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class DocumentQuality:
    """
    Service for document quality assessment and preview generation.
    """

    def __init__(self):
        """Initialize quality service."""
        pass

    def score_document(self, text: str) -> Dict[str, float]:
        """
        Score document quality across multiple dimensions.
        
        Args:
            text: Document text
        
        Returns:
            Dictionary with quality scores (0-10 scale)
        """
        scores = {}
        
        # Clarity score (based on sentence length, readability)
        scores["clarity"] = self._score_clarity(text)
        
        # Completeness score (structure, sections)
        scores["completeness"] = self._score_completeness(text)
        
        # Coherence score (flow, connections)
        scores["coherence"] = self._score_coherence(text)
        
        # Grammar-like score (basic checks)
        scores["grammar"] = self._score_grammar(text)
        
        # Professionalism score
        scores["professionalism"] = self._score_professionalism(text)
        
        # Calculate overall score
        scores["overall"] = sum(scores.values()) / len(scores)
        
        return scores

    def _score_clarity(self, text: str) -> float:
        """
        Score document clarity based on sentence structure.
        
        Args:
            text: Document text
        
        Returns:
            Clarity score (0-10)
        """
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Average sentence length (optimal is 15-20 words)
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Sentences too long (>30 words) lower clarity
        too_long = sum(1 for s in sentences if len(s.split()) > 30)
        too_short = sum(1 for s in sentences if len(s.split()) < 3)
        
        # Calculate score
        length_score = min(10, max(0, 10 - abs(avg_length - 17) / 2))
        problem_ratio = (too_long + too_short) / len(sentences)
        final_score = length_score * (1 - problem_ratio)
        
        return round(final_score, 1)

    def _score_completeness(self, text: str) -> float:
        """
        Score document completeness (structure, sections).
        
        Args:
            text: Document text
        
        Returns:
            Completeness score (0-10)
        """
        sections_indicators = [
            "introduction", "summary", "conclusion", "recommendation",
            "section", "chapter", "part", "background", "overview"
        ]
        
        text_lower = text.lower()
        found_sections = sum(1 for indicator in sections_indicators 
                            if indicator in text_lower)
        
        # Score based on document structure
        lines = text.split('\n')
        empty_lines = sum(1 for line in lines if not line.strip())
        has_headings = text.count('#') + text.count('*')
        
        structure_score = min(10, found_sections * 1.5 + has_headings * 0.5)
        
        # Penalize if too much empty space
        empty_ratio = empty_lines / len(lines) if lines else 0
        if empty_ratio > 0.3:
            structure_score *= 0.7
        
        return round(min(10, structure_score), 1)

    def _score_coherence(self, text: str) -> float:
        """
        Score document coherence (flow and connections).
        
        Args:
            text: Document text
        
        Returns:
            Coherence score (0-10)
        """
        # Check for transition words
        transitions = [
            "however", "therefore", "furthermore", "moreover",
            "in addition", "consequently", "as a result", "meanwhile",
            "for example", "in particular", "to summarize"
        ]
        
        text_lower = text.lower()
        transition_count = sum(1 for trans in transitions if trans in text_lower)
        
        # Check for repetitive structure
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        starts = [s.split()[0] if s.split() else "" for s in sentences]
        unique_starts = len(set(starts)) / len(starts) if sentences else 0
        
        # Calculate score
        transition_score = min(10, transition_count * 1.5)
        variety_score = unique_starts * 10
        
        coherence_score = (transition_score * 0.4 + variety_score * 0.6)
        
        return round(min(10, coherence_score), 1)

    def _score_grammar(self, text: str) -> float:
        """
        Score basic grammar and formatting.
        
        Args:
            text: Document text
        
        Returns:
            Grammar score (0-10)
        """
        issues = 0
        total_checks = 0
        
        # Check for double spaces
        total_checks += 1
        if "  " in text:
            issues += 0.5
        
        # Check for proper capitalization at sentence start
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        total_checks += len(sentences)
        for sent in sentences:
            if sent and sent[0].islower():
                issues += 0.3
        
        # Check for balanced parentheses/quotes
        total_checks += 1
        if text.count('(') != text.count(')'):
            issues += 0.5
        if text.count('"') % 2 != 0:
            issues += 0.3
        
        # Check for common typos patterns (simplified)
        common_errors = ["teh ", "hte ", "recieve", "ocur"]
        total_checks += len(common_errors)
        issues += sum(1 for error in common_errors if error.lower() in text.lower())
        
        score = max(0, 10 - (issues / total_checks * 10))
        return round(score, 1)

    def _score_professionalism(self, text: str) -> float:
        """
        Score document professionalism.
        
        Args:
            text: Document text
        
        Returns:
            Professionalism score (0-10)
        """
        text_lower = text.lower()
        
        # Check for professional tone indicators
        professional_words = [
            "recommend", "analysis", "conclude", "findings",
            "objective", "methodology", "implementation", "strategy"
        ]
        professional_count = sum(1 for word in professional_words 
                               if word in text_lower)
        
        # Check for unprofessional indicators
        unprofessional = [
            "lol", "omg", "btw", "etc.", "blah",
            "really really", "super", "awesome", "hate", "sucks"
        ]
        unprofessional_count = sum(1 for word in unprofessional 
                                  if word in text_lower)
        
        # Calculate score
        professional_score = min(10, professional_count * 1.5)
        unprofessional_penalty = unprofessional_count * 2
        
        final_score = max(0, professional_score - unprofessional_penalty)
        
        return round(final_score, 1)

    def get_quality_report(self, text: str) -> str:
        """
        Generate a formatted quality report.
        
        Args:
            text: Document text
        
        Returns:
            Formatted report string
        """
        scores = self.score_document(text)
        overall = scores["overall"]
        
        # Determine quality level
        if overall >= 8:
            level = "Excellent"
            emoji = "🌟"
        elif overall >= 6:
            level = "Good"
            emoji = "👍"
        elif overall >= 4:
            level = "Fair"
            emoji = "⚠️"
        else:
            level = "Needs Improvement"
            emoji = "🔧"
        
        report = (
            f"📊 *Document Quality Report*\n\n"
            f"{emoji} Overall: {overall:.1f}/10 ({level})\n\n"
            f"*Breakdown:*\n"
            f"📝 Clarity: {scores['clarity']:.1f}/10\n"
            f"✓ Completeness: {scores['completeness']:.1f}/10\n"
            f"🔗 Coherence: {scores['coherence']:.1f}/10\n"
            f"✏️ Grammar: {scores['grammar']:.1f}/10\n"
            f"🎩 Professionalism: {scores['professionalism']:.1f}/10"
        )
        
        return report

    def get_improvement_suggestions(self, scores: Dict) -> List[str]:
        """
        Get suggestions for document improvement.
        
        Args:
            scores: Quality scores dictionary
        
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        if scores.get("clarity", 10) < 7:
            suggestions.append("Consider breaking long sentences into shorter ones for better clarity")
        
        if scores.get("completeness", 10) < 7:
            suggestions.append("Add more structure with clear sections and headings")
        
        if scores.get("coherence", 10) < 7:
            suggestions.append("Use transition words to improve flow between ideas")
        
        if scores.get("grammar", 10) < 7:
            suggestions.append("Review grammar and check for formatting issues")
        
        if scores.get("professionalism", 10) < 7:
            suggestions.append("Use more formal, professional language throughout")
        
        return suggestions

    def generate_preview(self, text: str, lines: int = 5) -> str:
        """
        Generate a text preview for documents.
        
        Args:
            text: Full document text
            lines: Number of lines to preview
        
        Returns:
            Preview text
        """
        preview_lines = text.split('\n')[:lines]
        preview = '\n'.join(preview_lines)
        
        if len(text.split('\n')) > lines:
            preview += f"\n... ({len(text.split())} total words)"
        
        return preview

    def create_quality_summary(self, text: str) -> Dict:
        """
        Create comprehensive quality summary.
        
        Args:
            text: Document text
        
        Returns:
            Quality summary dictionary
        """
        scores = self.score_document(text)
        suggestions = self.get_improvement_suggestions(scores)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "scores": scores,
            "quality_level": self._get_quality_level(scores["overall"]),
            "suggestions": suggestions,
            "preview": self.generate_preview(text)
        }

    def _get_quality_level(self, score: float) -> str:
        """Get quality level label from score."""
        if score >= 8:
            return "Excellent"
        elif score >= 6:
            return "Good"
        elif score >= 4:
            return "Fair"
        else:
            return "Needs Improvement"
