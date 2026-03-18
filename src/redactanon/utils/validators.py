"""
Validators for RedactAnon
Input validation and sanitization utilities.
"""

import re
from pathlib import Path
from typing import Tuple


def validate_file_path(filepath: str) -> Tuple[bool, str]:
    """Validate a file path.

    Args:
        filepath: Path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filepath:
        return False, "File path cannot be empty"

    try:
        path = Path(filepath)

        # Check if path is absolute or relative
        if path.is_absolute():
            # For absolute paths, check if parent directory exists
            if not path.parent.exists():
                return False, f"Parent directory does not exist: {path.parent}"
        else:
            # For relative paths, check if the path resolves to something valid
            try:
                resolved_path = path.resolve()
                if not resolved_path.parent.exists():
                    return (
                        False,
                        f"Parent directory does not exist: {resolved_path.parent}",
                    )
            except Exception:
                # Continue with other checks - path resolution failed but that's OK
                pass  # nosec B110

        return True, ""

    except Exception as e:
        return False, f"Invalid file path: {e}"


def validate_directory_path(dirpath: str) -> Tuple[bool, str]:
    """Validate a directory path.

    Args:
        dirpath: Directory path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not dirpath:
        return False, "Directory path cannot be empty"

    try:
        path = Path(dirpath)

        # Check if directory exists
        if path.exists() and not path.is_dir():
            return False, f"Path exists but is not a directory: {dirpath}"

        # Check if parent directory exists (for creation)
        if not path.exists():
            if not path.parent.exists():
                return False, f"Parent directory does not exist: {path.parent}"

        return True, ""

    except Exception as e:
        return False, f"Invalid directory path: {e}"


def validate_regex_pattern(pattern: str) -> Tuple[bool, str]:
    """Validate a regex pattern.

    Args:
        pattern: Regex pattern to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not pattern:
        return False, "Pattern cannot be empty"

    try:
        re.compile(pattern)
        return True, ""
    except re.error as e:
        return False, f"Invalid regex pattern: {e}"


def validate_config_file(filepath: str) -> Tuple[bool, str]:
    """Validate a configuration file.

    Args:
        filepath: Configuration file path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filepath:
        return False, "Configuration file path cannot be empty"

    # Validate file path first
    is_valid, error_msg = validate_file_path(filepath)
    if not is_valid:
        return False, error_msg

    path = Path(filepath)

    # Check if file exists
    if not path.exists():
        return False, f"Configuration file does not exist: {filepath}"

    # Check if it's a file
    if not path.is_file():
        return False, f"Path is not a file: {filepath}"

    # Check file extension
    valid_extensions = [".toml", ".txt"]
    if path.suffix.lower() not in valid_extensions:
        return (
            False,
            f"Invalid configuration file extension. Supported: {valid_extensions}",
        )

    return True, ""


def validate_mapping_file(filepath: str) -> Tuple[bool, str]:
    """Validate a mapping file.

    Args:
        filepath: Mapping file path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filepath:
        return False, "Mapping file path cannot be empty"

    # Validate file path first
    is_valid, error_msg = validate_file_path(filepath)
    if not is_valid:
        return False, error_msg

    path = Path(filepath)

    # Check if file exists
    if not path.exists():
        return False, f"Mapping file does not exist: {filepath}"

    # Check if it's a file
    if not path.is_file():
        return False, f"Path is not a file: {filepath}"

    # Check file extension
    if path.suffix.lower() != ".json":
        return False, "Mapping file must have .json extension"

    return True, ""


def sanitize_path(path: str) -> str:
    """Sanitize a file path.

    Args:
        path: Path to sanitize

    Returns:
        Sanitized path
    """
    # Remove null bytes
    path = path.replace("\x00", "")

    # Normalize path separators
    path = path.replace("\\", "/")

    # Remove trailing slashes
    path = path.rstrip("/")

    return path


def is_safe_path(base_path: str, target_path: str) -> bool:
    """Check if a target path is safe relative to a base path (prevent directory traversal).

    Args:
        base_path: Base directory path
        target_path: Target path to check

    Returns:
        True if target path is safe, False otherwise
    """
    try:
        base_path_obj = Path(base_path).resolve()
        target_path_obj = Path(target_path).resolve()

        # Check if target path is within base path
        return str(target_path_obj).startswith(str(base_path_obj))
    except Exception:
        return False


def is_text_file(filepath: str, sample_size: int = 1024) -> bool:
    """Determine if a file is a text file by examining its content.

    Args:
        filepath: Path to the file to check
        sample_size: Number of bytes to read for analysis (default: 1024)

    Returns:
        True if file appears to be text, False otherwise
    """
    try:
        path = Path(filepath)

        # Check if it's a file
        if not path.is_file():
            return False

        # Empty files are considered text files
        if path.stat().st_size == 0:
            return True

        # Read a sample of the file content
        with open(path, "rb") as f:
            sample = f.read(sample_size)

        # Check for null bytes (common in binary files)
        if b"\x00" in sample:
            return False

        # Try to decode as UTF-8
        try:
            sample.decode("utf-8")
            return True
        except UnicodeDecodeError:
            # If UTF-8 fails, check if it's mostly printable ASCII
            printable_chars = sum(
                1 for byte in sample if 32 <= byte <= 126 or byte in (9, 10, 13)
            )
            return (printable_chars / len(sample)) > 0.7

    except Exception:
        # If we can't read the file, assume it's not a text file
        return False
