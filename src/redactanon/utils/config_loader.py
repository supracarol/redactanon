"""
Configuration Loader for RedactAnon
Handles loading and merging of configuration files.
"""

import os
from typing import Dict, List, Optional

from ..patterns.builtin import get_builtin_patterns
from ..patterns.user_patterns import (
    load_simple_patterns,
    load_toml_patterns,
    validate_patterns,
)


class ConfigLoader:
    """Loader for handling configuration files and pattern merging."""

    def __init__(self):
        """Initialize the configuration loader."""
        self.builtin_patterns = get_builtin_patterns()

    def load_patterns(
        self,
        config_file: Optional[str] = None,
        simple_config_file: Optional[str] = None,
        no_defaults: bool = False,
    ) -> List[Dict]:
        """Load patterns from configuration files.

        Args:
            config_file: Path to TOML configuration file
            simple_config_file: Path to simple text configuration file
            no_defaults: If True, exclude built-in default patterns

        Returns:
            List of pattern dictionaries
        """
        patterns = []

        # Load user patterns from TOML file
        if config_file and os.path.exists(config_file):
            toml_patterns = load_toml_patterns(config_file)
            patterns.extend(toml_patterns)

        # Load user patterns from simple text file
        if simple_config_file and os.path.exists(simple_config_file):
            simple_patterns = load_simple_patterns(simple_config_file)
            patterns.extend(simple_patterns)

        # Validate user patterns
        patterns = validate_patterns(patterns)

        # Add built-in patterns if not disabled
        if not no_defaults:
            builtin_patterns_list = []
            for name, pattern_info in self.builtin_patterns.items():
                pattern_dict = {
                    "name": name,
                    "pattern": pattern_info["pattern"],
                    "type": pattern_info["type"],
                    "compiled": __import__("re").compile(pattern_info["pattern"]),
                }
                builtin_patterns_list.append(pattern_dict)
            patterns.extend(builtin_patterns_list)

        # Handle pattern conflicts/naming
        patterns = self._resolve_conflicts(patterns)

        return patterns

    def _resolve_conflicts(self, patterns: List[Dict]) -> List[Dict]:
        """Resolve naming conflicts between patterns.

        Args:
            patterns: List of pattern dictionaries

        Returns:
            List of patterns with resolved conflicts
        """
        # Group patterns by name
        pattern_groups: Dict[str, List[Dict]] = {}
        for pattern in patterns:
            name = pattern.get("name", "unnamed")
            if name not in pattern_groups:
                pattern_groups[name] = []
            pattern_groups[name].append(pattern)

        # Resolve conflicts - user patterns override built-in patterns
        resolved_patterns = []
        for name, group in pattern_groups.items():
            if len(group) == 1:
                resolved_patterns.append(group[0])
            else:
                # Multiple patterns with same name - prioritize user patterns
                user_patterns = [
                    p
                    for p in group
                    if p.get("name", "").startswith("simple_pattern_")
                    or not p.get("name", "") in self.builtin_patterns
                ]
                if user_patterns:
                    # Use the first user pattern
                    resolved_patterns.append(user_patterns[0])
                    print(f"Warning: Pattern '{name}' overridden by user pattern")
                else:
                    # Use the first pattern (shouldn't happen normally)
                    resolved_patterns.append(group[0])

        return resolved_patterns

    def get_default_config_path(self) -> Optional[str]:
        """Get the default configuration file path.

        Returns:
            Path to default config file if exists, None otherwise
        """
        default_paths = ["./patterns.toml", "./config/patterns.toml"]

        for path in default_paths:
            if os.path.exists(path):
                return path
        return None

    def create_default_config(self, filepath: str = "patterns.toml") -> str:
        """Create a default configuration file.

        Args:
            filepath: Path where to create the default config file

        Returns:
            Path to the created configuration file
        """
        default_config = """# RedactAnon Default Configuration File

# Example email pattern
[email]
pattern = '\\\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Z|a-z]{2,}\\\\b'
type = "email"
# Optional: specify custom replacement value
# replacement = "user@example.com"

# Example IP address pattern
[ip_address]
pattern = '\\\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\\\b'
type = "ip_address"
# Optional: let system generate random replacement
# replacement = "192.168.1.100"

# Example custom pattern
[custom_name]
pattern = "John Doe"
type = "name"
replacement = "Anonymous User"
"""

        with open(filepath, "w") as f:
            f.write(default_config)

        return filepath


def load_merged_patterns(
    config_file: Optional[str] = None,
    simple_config_file: Optional[str] = None,
    no_defaults: bool = False,
) -> List[Dict]:
    """Convenience function to load merged patterns.

    Args:
        config_file: Path to TOML configuration file
        simple_config_file: Path to simple text configuration file
        no_defaults: If True, exclude built-in default patterns

    Returns:
        List of pattern dictionaries
    """
    loader = ConfigLoader()
    return loader.load_patterns(config_file, simple_config_file, no_defaults)
