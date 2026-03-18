"""
Built-in patterns for RedactAnon
Default patterns for common sensitive data types.
"""

import os
from pathlib import Path

from ..patterns.user_patterns import load_toml_patterns


def get_builtin_patterns():
    """Get all built-in patterns from the default configuration file.

    Returns:
        Dictionary of built-in patterns
    """
    config_path = get_default_patterns_path()
    if config_path and os.path.exists(config_path):
        patterns_list = load_toml_patterns(config_path)
        # Convert list to dictionary format expected by the rest of the system
        patterns_dict = {}
        for pattern in patterns_list:
            if "name" in pattern:
                patterns_dict[pattern["name"]] = {
                    "pattern": pattern["pattern"],
                    "type": pattern["type"],
                    "description": pattern.get("description", ""),
                }
        return patterns_dict
    else:
        # Return empty dict if no config file found
        return {}


def get_default_patterns_path():
    """Get the path to the default patterns configuration file.

    Returns:
        Path to default patterns file, or None if not found
    """
    try:
        # Get the package root directory (where setup.py/pyproject.toml is located)
        # __file__ is src/redactanon/patterns/builtin.py
        # So parent.parent.parent.parent = /home/user/code/redactanon (project root)
        project_root = Path(__file__).parent.parent.parent.parent  # project root level

        # Try to find the default patterns file in known locations
        possible_paths = [
            project_root / "config" / "default_patterns.toml",  # Correct path
            Path(__file__).parent.parent.parent
            / "config"
            / "default_patterns.toml",  # src/config
            project_root / "default_patterns.toml",  # Fallback
        ]

        for path in possible_paths:
            if path.exists():
                return str(path)
    except Exception:
        # Fallback: try relative path from current working directory
        fallback_path = Path("config") / "default_patterns.toml"
        if fallback_path.exists():
            return str(fallback_path)

        # Try absolute path from project root
        fallback_path = (
            Path(__file__).parent.parent.parent.parent
            / "config"
            / "default_patterns.toml"
        )
        if fallback_path.exists():
            return str(fallback_path)

    return None


def get_pattern_names():
    """Get list of built-in pattern names.

    Returns:
        List of pattern names
    """
    builtin_patterns = get_builtin_patterns()
    return list(builtin_patterns.keys())


def get_pattern(name):
    """Get a specific built-in pattern by name.

    Args:
        name: Name of the pattern to retrieve

    Returns:
        Pattern dictionary or None if not found
    """
    builtin_patterns = get_builtin_patterns()
    return builtin_patterns.get(name)
