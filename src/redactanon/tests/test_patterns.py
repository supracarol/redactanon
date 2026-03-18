"""
Tests for RedactAnon Pattern Engine
"""

import unittest

from ..core.pattern_engine import PatternEngine


class TestPatternEngine(unittest.TestCase):
    """Test cases for the PatternEngine class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.engine = PatternEngine()

    def test_init(self):
        """Test PatternEngine initialization."""
        self.assertIsInstance(self.engine.user_patterns, list)
        self.assertIsInstance(self.engine.builtin_patterns, dict)

    def test_add_user_pattern(self):
        """Test adding user patterns."""
        pattern = r"\btest@example\.com\b"
        self.engine.add_user_pattern(pattern, "email", "test_email")

        self.assertEqual(len(self.engine.user_patterns), 1)
        pattern_info = self.engine.user_patterns[0]
        self.assertEqual(pattern_info["pattern"], pattern)
        self.assertEqual(pattern_info["type"], "email")
        self.assertEqual(pattern_info["name"], "test_email")

    def test_add_builtin_pattern(self):
        """Test adding built-in patterns."""
        name = "custom_builtin"
        pattern = r"\b\d{3}-\d{2}-\d{4}\b"
        pattern_type = "ssn"

        self.engine.add_builtin_pattern(name, pattern, pattern_type)

        self.assertIn(name, self.engine.builtin_patterns)
        pattern_info = self.engine.builtin_patterns[name]
        self.assertEqual(pattern_info["pattern"], pattern)
        self.assertEqual(pattern_info["type"], pattern_type)

    def test_detect_sensitive_data(self):
        """Test detecting sensitive data."""
        # Add a simple test pattern
        self.engine.add_user_pattern(r"John Doe", "name", "test_name")

        text = "Contact John Doe at john.doe@example.com"
        findings = self.engine.detect_sensitive_data(text)

        self.assertIsInstance(findings, list)
        # Should find at least the name (built-in email pattern might also match)
        self.assertGreaterEqual(len(findings), 1)

        # Check if our test name was found
        name_found = any(match[0] == "John Doe" for match in findings)
        self.assertTrue(name_found)

    def test_get_all_patterns(self):
        """Test getting all patterns."""
        # Add a user pattern
        self.engine.add_user_pattern(r"test", "custom", "test_pattern")

        # Get all patterns (including defaults)
        all_patterns = self.engine.get_all_patterns(include_defaults=True)
        self.assertIsInstance(all_patterns, list)
        self.assertGreater(len(all_patterns), 1)  # Should have user + built-in patterns

        # Get only user patterns
        user_patterns = self.engine.get_all_patterns(include_defaults=False)
        self.assertEqual(len(user_patterns), 1)
        self.assertEqual(user_patterns[0]["name"], "test_pattern")


if __name__ == "__main__":
    unittest.main()
