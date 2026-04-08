"""
Document Comparison Service - Compare two documents and highlight differences.
Uses AI to provide intelligent insights on what changed between versions.
"""

import difflib
import logging
from typing import List, Dict, Tuple
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)


class DocumentComparison:
    """
    Service for comparing two documents and detecting meaningful differences.
    Provides both structural and semantic comparison.
    """

    def __init__(self):
        """Initialize document comparison service."""
        pass

    def compare_text(self, text1: str, text2: str) -> Dict:
        """
        Compare two text documents.
        
        Args:
            text1: First document text
            text2: Second document text
        
        Returns:
            Dictionary with comparison results
        """
        lines1 = text1.split('\n')
        lines2 = text2.split('\n')
        
        # Use difflib for detailed comparison
        differ = difflib.Differ()
        diff_result = list(differ.compare(lines1, lines2))
        
        # Extract additions, deletions, and changes
        added = [line[2:].strip() for line in diff_result if line.startswith('+ ')]
        removed = [line[2:].strip() for line in diff_result if line.startswith('- ')]
        unchanged = [line[2:].strip() for line in diff_result if line.startswith('  ')]
        
        return {
            "added_lines": added,
            "removed_lines": removed,
            "unchanged_lines": unchanged,
            "total_added": len(added),
            "total_removed": len(removed),
            "total_unchanged": len(unchanged),
            "similarity_ratio": difflib.SequenceMatcher(None, text1, text2).ratio()
        }

    def get_change_summary(self, comparison: Dict) -> str:
        """
        Generate a human-readable summary of changes.
        
        Args:
            comparison: Comparison result dictionary
        
        Returns:
            Summary string
        """
        ratio = comparison.get("similarity_ratio", 0)
        added = comparison.get("total_added", 0)
        removed = comparison.get("total_removed", 0)
        
        if ratio > 0.95:
            change_level = "minimal"
        elif ratio > 0.75:
            change_level = "moderate"
        elif ratio > 0.5:
            change_level = "significant"
        else:
            change_level = "major"
        
        summary = (
            f"📊 *Comparison Summary*\n\n"
            f"Change Level: {change_level.upper()}\n"
            f"Similarity: {ratio*100:.1f}%\n\n"
            f"➕ Added: {added} lines\n"
            f"➖ Removed: {removed} lines\n"
            f"✓ Unchanged: {comparison.get('total_unchanged', 0)} lines"
        )
        
        return summary

    def get_key_changes(self, comparison: Dict, max_items: int = 5) -> str:
        """
        Get the most important changes.
        
        Args:
            comparison: Comparison result
            max_items: Max changes to show
        
        Returns:
            Formatted string of key changes
        """
        changes_text = "🔍 *Key Changes*\n\n"
        
        added = comparison.get("added_lines", [])[:max_items]
        removed = comparison.get("removed_lines", [])[:max_items]
        
        if added:
            changes_text += "*Added:*\n"
            for line in added:
                if line:
                    changes_text += f"✅ {line[:80]}\n"
        
        if removed:
            changes_text += "\n*Removed:*\n"
            for line in removed:
                if line:
                    changes_text += f"❌ {line[:80]}\n"
        
        if not added and not removed:
            changes_text += "No significant content changes detected."
        
        return changes_text

    def analyze_semantic_changes(self, text1: str, text2: str, ai_service) -> str:
        """
        Use AI to analyze semantic meaning changes.
        
        Args:
            text1: Original document
            text2: Modified document
            ai_service: AI service for analysis
        
        Returns:
            AI-generated analysis
        """
        prompt = (
            f"Compare these two documents and explain the meaningful differences:\n\n"
            f"DOCUMENT 1:\n{text1[:1000]}\n\n"
            f"DOCUMENT 2:\n{text2[:1000]}\n\n"
            f"Provide a concise list of:\n"
            f"1. What concepts were removed or changed\n"
            f"2. What new concepts or sections were added\n"
            f"3. Assessment of whether changes are significant or minor"
        )
        
        try:
            response = ai_service.call_ai(prompt)
            return response
        except Exception as e:
            logger.error(f"Semantic analysis error: {e}")
            return "Could not perform semantic analysis."

    def generate_comparison_report(self, text1: str, text2: str, ai_service=None) -> Dict:
        """
        Generate a comprehensive comparison report.
        
        Args:
            text1: Document 1
            text2: Document 2
            ai_service: Optional AI service for semantic analysis
        
        Returns:
            Complete comparison report
        """
        comparison = self.compare_text(text1, text2)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "comparison_data": comparison,
            "summary": self.get_change_summary(comparison),
            "key_changes": self.get_key_changes(comparison),
        }
        
        # Add semantic analysis if AI service provided
        if ai_service:
            semantic = self.analyze_semantic_changes(text1, text2, ai_service)
            report["semantic_analysis"] = semantic
        
        return report

    def create_comparison_table(self, comparison: Dict) -> str:
        """
        Create a formatted table comparing documents.
        
        Args:
            comparison: Comparison result
        
        Returns:
            Formatted table string
        """
        added = comparison.get("total_added", 0)
        removed = comparison.get("total_removed", 0)
        unchanged = comparison.get("total_unchanged", 0)
        similarity = comparison.get("similarity_ratio", 0)
        
        table = (
            "📋 *Detailed Comparison*\n\n"
            "```\n"
            "Metric              | Value\n"
            "────────────────────┼──────────\n"
            f"Lines Added         | {added}\n"
            f"Lines Removed       | {removed}\n"
            f"Lines Unchanged     | {unchanged}\n"
            f"Similarity          | {similarity*100:.1f}%\n"
            "```"
        )
        
        return table

    def save_comparison(self, report: Dict, filepath: str) -> bool:
        """
        Save comparison report to file.
        
        Args:
            report: Comparison report
            filepath: Output file path
        
        Returns:
            True if successful
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Save comparison error: {e}")
            return False
