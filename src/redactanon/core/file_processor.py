"""
File Processor for RedactAnon
Handles file and directory processing for anonymization and restoration.
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from ..utils.validators import is_text_file
from .data_generator import DataGenerator
from .mapping_manager import MappingManager
from .pattern_engine import PatternEngine


class FileProcessor:
    """Processor for handling file and directory anonymization/restoration."""

    def __init__(
        self,
        pattern_engine: PatternEngine,
        data_generator: DataGenerator,
        mapping_manager: MappingManager,
    ):
        """Initialize the file processor.

        Args:
            pattern_engine: Pattern engine for detecting sensitive data
            data_generator: Data generator for creating fake values
            mapping_manager: Mapping manager for storing/retrieving mappings
        """
        self.pattern_engine = pattern_engine
        self.data_generator = data_generator
        self.mapping_manager = mapping_manager

    def process_file(self, filepath: str, mode: str = "anonymize") -> bool:
        """Process a single file for anonymization or restoration.

        Args:
            filepath: Path to the file to process
            mode: Processing mode ('anonymize' or 'restore')

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            if mode == "anonymize":
                return self._anonymize_file(filepath)
            elif mode == "restore":
                return self._restore_file(filepath)
            else:
                raise ValueError(f"Invalid mode: {mode}")
        except Exception as e:
            print(f"Error processing file {filepath}: {e}")
            return False

    def process_directory(
        self,
        source_path: str,
        destination_path: Optional[str] = None,
        mode: str = "anonymize",
        mappings_output: Optional[str] = None,
    ) -> bool:
        """Process a directory for anonymization or restoration.

        Args:
            source_path: Path to the source directory/file
            destination_path: Optional destination path. If provided, creates backup
                            and processes to new location. If None, processes in-place.
            mode: Processing mode ('anonymize' or 'restore')
            mappings_output: Optional path for mappings output file

        Returns:
            True if processing was successful, False otherwise
        """
        source_path_obj: Path = Path(source_path)

        try:
            if destination_path:
                # Process to destination (creates backup)
                destination_path_obj: Path = Path(destination_path)
                return self._process_to_destination(
                    source_path_obj, destination_path_obj, mode, mappings_output
                )
            else:
                # Process in-place
                if source_path_obj.is_file():
                    result = self.process_file(str(source_path_obj), mode)
                    # Save mappings for single file processing
                    if mode == "anonymize":
                        if mappings_output:
                            mapping_file = self.mapping_manager.save_mappings(
                                mappings_output
                            )
                            print(f"Saved mappings to: {mapping_file}")
                        else:
                            # Default to <filename>.map.json for single files
                            default_mapping_file = (
                                Path.cwd() / f"{source_path_obj.name}.map.json"
                            )
                            mapping_file = self.mapping_manager.save_mappings(
                                str(default_mapping_file)
                            )
                            print(f"Saved mappings to: {mapping_file}")
                    return result
                elif source_path_obj.is_dir():
                    return self._process_directory_in_place(
                        source_path_obj, mode, mappings_output
                    )
                else:
                    print(f"Source path does not exist: {source_path}")
                    return False
        except Exception as e:
            print(f"Error processing directory {source_path}: {e}")
            return False

    def _anonymize_file(self, filepath: str) -> bool:
        """Anonymize a single file.

        Args:
            filepath: Path to the file to anonymize

        Returns:
            True if anonymization was successful, False otherwise
        """
        try:
            # Read the file content
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Detect sensitive data with pattern info
            findings = self.pattern_engine.detect_sensitive_data(content)

            if not findings:
                print(f"No sensitive data found in {filepath}")
                return True

            # Apply anonymization
            anonymized_content = content
            replacements = 0

            for original_value, pattern_type, pattern_name in findings:
                # Check if we already have a mapping for this value
                fake_value = self.mapping_manager.get_fake_value(original_value)

                if fake_value is None:
                    # Check if pattern has custom replacement
                    custom_replacement = None
                    all_patterns = self.pattern_engine.get_all_patterns()

                    # Find the pattern that matched this value
                    for pattern_info in all_patterns:
                        if (
                            pattern_info.get("name") == pattern_name
                            and "replacement" in pattern_info
                        ):
                            # Verify this pattern actually matches the original value
                            if pattern_info["compiled"].match(original_value):
                                custom_replacement = pattern_info["replacement"]
                                break

                    if custom_replacement:
                        fake_value = custom_replacement
                    else:
                        # Generate new fake value
                        fake_value = self.data_generator.generate_fake_data(
                            pattern_type, original_value
                        )

                    # Store the mapping
                    self.mapping_manager.store_mapping(original_value, fake_value)

                # Replace in content
                if original_value in anonymized_content:
                    anonymized_content = anonymized_content.replace(
                        original_value, fake_value
                    )
                    replacements += 1

            # Write anonymized content back to file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(anonymized_content)

            print(f"Anonymized {filepath}: {replacements} items replaced")
            return True

        except Exception as e:
            print(f"Error anonymizing file {filepath}: {e}")
            return False

    def _restore_file(self, filepath: str) -> bool:
        """Restore a single file from mappings.

        Args:
            filepath: Path to the file to restore

        Returns:
            True if restoration was successful, False otherwise
        """
        try:
            # Read the file content
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Get all mappings
            mappings = self.mapping_manager.get_all_mappings()

            if not mappings:
                print(f"No mappings available for restoring {filepath}")
                return True

            # Apply restoration (reverse mapping)
            restored_content = content
            replacements = 0

            for original_value, fake_value in mappings.items():
                if fake_value in restored_content:
                    restored_content = restored_content.replace(
                        fake_value, original_value
                    )
                    replacements += 1

            # Write restored content back to file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(restored_content)

            print(f"Restored {filepath}: {replacements} items restored")
            return True

        except Exception as e:
            print(f"Error restoring file {filepath}: {e}")
            return False

    def _process_directory_in_place(
        self, directory_path: Path, mode: str, mappings_output: Optional[str] = None
    ) -> bool:
        """Process all files in a directory in-place.

        Args:
            directory_path: Path to the directory to process
            mode: Processing mode ('anonymize' or 'restore')
            mappings_output: Optional path for mappings output file

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            # Generate session UUID for this directory processing
            self.mapping_manager.generate_session_uuid()

            # Create .redactanon-id file
            self.mapping_manager.create_id_file(str(directory_path))

            success = True
            file_count = 0

            # Walk through all files in directory
            for root, dirs, files in os.walk(directory_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for filename in files:
                    # Skip hidden files and our own files
                    if filename.startswith(".") or filename == ".redactanon-id":
                        continue

                    filepath = Path(root) / filename

                    # Only process text files
                    if not is_text_file(str(filepath)):
                        print(f"Skipping non-text file: {filepath}")
                        continue

                    if self.process_file(str(filepath), mode):
                        file_count += 1
                    else:
                        success = False

                # Save mappings after processing
                if mode == "anonymize":
                    if mappings_output:
                        mapping_file = self.mapping_manager.save_mappings(
                            mappings_output
                        )
                        print(f"Saved mappings to: {mapping_file}")
                    else:
                        # Save to default location
                        # (~/.redactanon/mappings/<uuid>.json)
                        mapping_file = self.mapping_manager.save_mappings()
                        print(f"Saved mappings to: {mapping_file}")

            print(f"Processed {file_count} files in {directory_path}")
            return success

        except Exception as e:
            print(f"Error processing directory {directory_path}: {e}")
            return False

    def _process_to_destination(
        self,
        source_path: Path,
        destination_path: Path,
        mode: str,
        mappings_output: Optional[str] = None,
    ) -> bool:
        """Process files from source to destination (with backup).

        Args:
            source_path: Source path (file or directory)
            destination_path: Destination path
            mode: Processing mode ('anonymize' or 'restore')
            mappings_output: Optional path for mappings output file

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            # Create destination directory if it doesn't exist
            destination_path.mkdir(parents=True, exist_ok=True)

            # Copy source to destination
            if source_path.is_file():
                shutil.copy2(source_path, destination_path)
                target_path = destination_path / source_path.name
                return self.process_file(str(target_path), mode)
            elif source_path.is_dir():
                # Copy entire directory structure
                for item in source_path.rglob("*"):
                    if item.is_file():
                        # Only copy text files
                        if not is_text_file(str(item)):
                            print(f"Skipping non-text file: {item}")
                            continue

                        # Calculate relative path
                        rel_path = item.relative_to(source_path)
                        dest_file = destination_path / rel_path

                        # Create parent directories
                        dest_file.parent.mkdir(parents=True, exist_ok=True)

                        # Copy file
                        shutil.copy2(item, dest_file)

                # Process the copied directory
                return self._process_directory_in_place(
                    destination_path, mode, mappings_output
                )
            else:
                print(f"Source path does not exist: {source_path}")
                return False

        except Exception as e:
            print(f"Error processing to destination: {e}")
            return False

    def create_backup(self, source_path: str, backup_path: str) -> bool:
        """Create a backup of a file or directory.

        Args:
            source_path: Path to the source file/directory
            backup_path: Path where backup should be created

        Returns:
            True if backup was successful, False otherwise
        """
        try:
            source_path_obj: Path = Path(source_path)
            backup_path_obj: Path = Path(backup_path)

            if source_path_obj.is_file():
                backup_path_obj.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path_obj, backup_path_obj)
            elif source_path_obj.is_dir():
                backup_path_obj.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source_path_obj, backup_path_obj, dirs_exist_ok=True)
            else:
                print(f"Source path does not exist: {source_path}")
                return False

            print(f"Created backup of {source_path} to {backup_path}")
            return True

        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
