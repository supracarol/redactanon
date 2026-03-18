#!/usr/bin/env python3
"""
RedactAnon - A CLI tool for reversible file anonymization
"""

import argparse
import sys
from pathlib import Path

from .core.data_generator import DataGenerator
from .core.file_processor import FileProcessor
from .core.mapping_manager import MappingManager
from .core.pattern_engine import PatternEngine
from .patterns.builtin import get_pattern_names
from .utils.config_loader import ConfigLoader
from .utils.validators import (
    validate_config_file,
    validate_directory_path,
    validate_file_path,
    validate_mapping_file,
)


def main():
    """Main entry point for the RedactAnon CLI application."""
    parser = argparse.ArgumentParser(
        description=(
            "Anonymize files by replacing private values with dummy values "
            "in a reversible manner."
        )
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Anonymize command
    anon_parser = subparsers.add_parser("anon", help="Anonymize files or directories")
    anon_parser.add_argument("source", help="Source file or directory to anonymize")
    anon_parser.add_argument(
        "destination", nargs="?", help="Destination directory (optional, for backup)"
    )
    anon_parser.add_argument("--config", help="Custom configuration file (TOML format)")
    anon_parser.add_argument("--simple-config", help="Simple text configuration file")
    anon_parser.add_argument(
        "--no-defaults",
        action="store_true",
        help="Disable default patterns, use only custom patterns",
    )
    anon_parser.add_argument(
        "--mapfile",
        help=(
            "Output file path for mappings (default: "
            "~/.redactanon/mappings/<uuid>.json for directories, "
            "<filename>.map.json for files)"
        ),
    )

    # Restore command
    restore_parser = subparsers.add_parser(
        "restore", help="Restore files from mappings"
    )
    restore_parser.add_argument("target", help="File or directory to restore")
    restore_parser.add_argument("--mappings", help="Specific mapping file to use")

    args = parser.parse_args()

    if args.command == "anon":
        return handle_anonymize(args)
    elif args.command == "restore":
        return handle_restore(args)
    else:
        parser.print_help()
        return 1


def handle_anonymize(args):
    """Handle the anonymize command."""
    # Validate source path
    is_valid, error_msg = validate_file_path(args.source)
    if not is_valid:
        print(f"Error: {error_msg}")
        return 1

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source path does not exist: {args.source}")
        return 1

    # Validate destination path if provided
    if args.destination:
        is_valid, error_msg = validate_directory_path(args.destination)
        if not is_valid:
            print(f"Error: {error_msg}")
            return 1

    # Validate config files if provided
    if args.config:
        is_valid, error_msg = validate_config_file(args.config)
        if not is_valid:
            print(f"Error: {error_msg}")
            return 1

    if args.simple_config:
        is_valid, error_msg = validate_config_file(args.simple_config)
        if not is_valid:
            print(f"Error: {error_msg}")
            return 1

    try:
        # Initialize core components
        pattern_engine = PatternEngine()
        data_generator = DataGenerator()
        mapping_manager = MappingManager()
        file_processor = FileProcessor(pattern_engine, data_generator, mapping_manager)

        # Load patterns
        config_loader = ConfigLoader()
        patterns = config_loader.load_patterns(
            config_file=args.config,
            simple_config_file=args.simple_config,
            no_defaults=args.no_defaults,
        )

        # Get builtin pattern names for comparison
        builtin_names = get_pattern_names()

        # Add patterns to engine
        for pattern in patterns:
            if pattern.get("name") in builtin_names:
                pattern_engine.add_builtin_pattern(
                    pattern["name"], pattern["pattern"], pattern["type"]
                )
            else:
                pattern_engine.add_user_pattern(
                    pattern["pattern"],
                    pattern["type"],
                    name=pattern.get("name"),
                    replacement=pattern.get("replacement"),
                )

        print(f"Loaded {len(patterns)} patterns")
        print(f"Anonymizing: {args.source}")

        if args.destination:
            print(f"Destination: {args.destination}")
            success = file_processor.process_directory(
                str(source_path),
                args.destination,
                mode="anonymize",
                mappings_output=args.mapfile,
            )
        else:
            print("Processing in-place")
            success = file_processor.process_directory(
                str(source_path), mode="anonymize", mappings_output=args.mapfile
            )

        if success:
            print("Anonymization completed successfully!")
            return 0
        else:
            print("Anonymization failed!")
            return 1

    except Exception as e:
        print(f"Error during anonymization: {e}")
        return 1


def handle_restore(args):
    """Handle the restore command."""
    # Validate target path
    is_valid, error_msg = validate_file_path(args.target)
    if not is_valid:
        print(f"Error: {error_msg}")
        return 1

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {args.target}")
        return 1

    # Validate mapping file if provided
    if args.mappings:
        is_valid, error_msg = validate_mapping_file(args.mappings)
        if not is_valid:
            print(f"Error: {error_msg}")
            return 1

    try:
        # Initialize core components
        pattern_engine = PatternEngine()
        data_generator = DataGenerator()
        mapping_manager = MappingManager()
        file_processor = FileProcessor(pattern_engine, data_generator, mapping_manager)

        # Load mappings
        if args.mappings:
            print(f"Loading mappings from: {args.mappings}")
            mapping_manager.load_mappings(args.mappings)
        else:
            # Try to find mappings automatically
            if target_path.is_dir():
                # For directories, look for .redactanon-id file
                uuid_str = mapping_manager.read_id_file(str(target_path))
                if uuid_str:
                    mapping_file = mapping_manager.find_mapping_file_by_uuid(uuid_str)
                    if mapping_file:
                        print(f"Loading mappings from: {mapping_file}")
                        mapping_manager.load_mappings(mapping_file)
                    else:
                        print("Error: Could not find mapping file for this directory")
                        return 1
                else:
                    print("Error: No .redactanon-id file found in directory")
                    return 1
            else:
                # For files, look for <filename>.map.json
                default_mapping_file = Path.cwd() / f"{target_path.name}.map.json"
                if default_mapping_file.exists():
                    print(f"Loading mappings from: {default_mapping_file}")
                    mapping_manager.load_mappings(str(default_mapping_file))
                else:
                    print(f"Error: Mapping file not found: {default_mapping_file}")
                    print("Specify mapping file with --mappings option")
                    return 1

        print(f"Restoring: {args.target}")
        success = file_processor.process_directory(str(target_path), mode="restore")

        if success:
            print("Restoration completed successfully!")
            return 0
        else:
            print("Restoration failed!")
            return 1

    except Exception as e:
        print(f"Error during restoration: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
