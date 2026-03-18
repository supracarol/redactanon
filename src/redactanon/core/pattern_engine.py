"""
Pattern Engine for RedactAnon
Handles pattern detection and matching for sensitive data.
"""

import re
from typing import Dict, List, Optional, Tuple


class PatternEngine:
    """Engine for detecting and matching sensitive data patterns."""

    def __init__(self):
        """Initialize the pattern engine with empty pattern collections."""
        self.user_patterns: List[Dict] = []
        self.builtin_patterns: Dict[str, Dict] = {}
        self._load_builtin_patterns()

    def _load_builtin_patterns(self):
        """Load built-in default patterns."""
        try:
            from ..patterns.builtin import get_builtin_patterns

            builtin_patterns = get_builtin_patterns()

            for name, pattern_info in builtin_patterns.items():
                self.add_builtin_pattern(
                    name, pattern_info["pattern"], pattern_info["type"]
                )
        except Exception as e:
            print(f"Warning: Could not load built-in patterns: {e}")

    def add_user_pattern(
        self,
        pattern: str,
        replacement_type: str,
        name: Optional[str] = None,
        replacement: Optional[str] = None,
    ):
        """Add a user-defined pattern to the engine.

        Args:
            pattern: Regex pattern string
            replacement_type: Type of data (email, ip, etc.)
            name: Optional name for the pattern
            replacement: Optional specific replacement value
        """
        pattern_dict = {
            "pattern": pattern,
            "type": replacement_type,
            "compiled": re.compile(pattern),
        }

        if name:
            pattern_dict["name"] = name
        if (
            replacement is not None
        ):  # Changed from "if replacement:" to handle empty strings
            pattern_dict["replacement"] = replacement

        self.user_patterns.append(pattern_dict)

    def add_builtin_pattern(self, name: str, pattern: str, replacement_type: str):
        """Add a built-in pattern to the engine.

        Args:
            name: Name of the pattern
            pattern: Regex pattern string
            replacement_type: Type of data (email, ip, etc.)
        """
        self.builtin_patterns[name] = {
            "pattern": pattern,
            "type": replacement_type,
            "compiled": re.compile(pattern),
        }

    def detect_sensitive_data(self, text: str) -> List[Tuple[str, str, str]]:
        """Detect sensitive data in text using all applicable patterns.

        Args:
            text: Text to scan for sensitive data

        Returns:
            List of tuples: (matched_text, pattern_type, pattern_name)
        """
        findings = []

        # Check user patterns first
        for pattern_info in self.user_patterns:
            matches = pattern_info["compiled"].finditer(text)
            for match in matches:
                findings.append(
                    (
                        match.group(0),
                        pattern_info["type"],
                        pattern_info.get("name", "user_pattern"),
                    )
                )

        # Check built-in patterns
        for name, pattern_info in self.builtin_patterns.items():
            matches = pattern_info["compiled"].finditer(text)
            for match in matches:
                findings.append((match.group(0), pattern_info["type"], name))

        return findings

    def get_all_patterns(self, include_defaults: bool = True) -> List[Dict]:
        """Get all patterns currently loaded in the engine.

        Args:
            include_defaults: Whether to include built-in patterns

        Returns:
            List of all pattern dictionaries
        """
        patterns = self.user_patterns.copy()
        if include_defaults:
            patterns.extend(list(self.builtin_patterns.values()))
        return patterns
