"""
User Patterns for RedactAnon
Handles loading and processing of user-defined patterns.
"""

import re
from typing import Dict, List

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib_  # Fallback for older versions

    tomllib = tomllib_


def load_toml_patterns(config_file: str) -> List[Dict]:
    """Load patterns from a TOML configuration file.

    Args:
        config_file: Path to the TOML configuration file

    Returns:
        List of pattern dictionaries
    """
    try:
        with open(config_file, "rb") as f:
            config = tomllib.load(f)

        patterns = []
        for pattern_name, pattern_config in config.items():
            if (
                isinstance(pattern_config, dict)
                and "pattern" in pattern_config
                and "type" in pattern_config
            ):
                pattern_dict = {
                    "name": pattern_name,
                    "pattern": pattern_config["pattern"],
                    "type": pattern_config["type"],
                }

                # Optional replacement value
                if "replacement" in pattern_config:
                    pattern_dict["replacement"] = pattern_config["replacement"]

                # Compile the regex pattern
                try:
                    pattern_dict["compiled"] = re.compile(pattern_config["pattern"])
                except re.error as e:
                    print(
                        f"Warning: Invalid regex pattern "
                        f"'{pattern_config['pattern']}' for pattern "
                        f"'{pattern_name}': {e}"
                    )
                    continue

                patterns.append(pattern_dict)

        return patterns

    except Exception as e:
        print(f"Error loading TOML patterns from {config_file}: {e}")
        return []


def load_simple_patterns(simple_file: str) -> List[Dict]:
    """Load patterns from a simple text file.

    Args:
        simple_file: Path to the simple text configuration file

    Returns:
        List of pattern dictionaries
    """
    try:
        patterns = []
        with open(simple_file, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse line: original[=replacement]
                if "=" in line:
                    original, replacement = line.split("=", 1)
                    original = original.strip()
                    replacement = replacement.strip()

                    # Create regex pattern for exact match
                    pattern = re.escape(original)
                    pattern_dict = {
                        "name": f"simple_pattern_{line_num}",
                        "pattern": pattern,
                        "type": "custom",
                        "replacement": replacement,
                        "compiled": re.compile(pattern),
                    }
                else:
                    original = line.strip()
                    # Create regex pattern for exact match
                    pattern = re.escape(original)
                    pattern_dict = {
                        "name": f"simple_pattern_{line_num}",
                        "pattern": pattern,
                        "type": "custom",
                        "compiled": re.compile(pattern),
                    }

                patterns.append(pattern_dict)

        return patterns

    except Exception as e:
        print(f"Error loading simple patterns from {simple_file}: {e}")
        return []


def validate_patterns(patterns: List[Dict]) -> List[Dict]:
    """Validate a list of patterns.

    Args:
        patterns: List of pattern dictionaries to validate

    Returns:
        List of valid patterns
    """
    valid_patterns = []

    for pattern_dict in patterns:
        try:
            # Check required fields
            if "pattern" not in pattern_dict or "type" not in pattern_dict:
                print(f"Warning: Pattern missing required fields: {pattern_dict}")
                continue

            # Try to compile the pattern
            if "compiled" not in pattern_dict:
                pattern_dict["compiled"] = re.compile(pattern_dict["pattern"])

            valid_patterns.append(pattern_dict)

        except re.error as e:
            print(
                f"Warning: Invalid regex pattern "
                f"'{pattern_dict.get('pattern', 'unknown')}': {e}"
            )
        except Exception as e:
            print(f"Warning: Error validating pattern: {e}")

    return valid_patterns
