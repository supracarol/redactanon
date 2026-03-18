"""
Integration tests for RedactAnon mapfile behavior
"""

import json
import os
from pathlib import Path

import pytest

from redactanon.core.data_generator import DataGenerator
from redactanon.core.file_processor import FileProcessor
from redactanon.core.mapping_manager import MappingManager
from redactanon.core.pattern_engine import PatternEngine


class TestMapfileBehavior:
    """Test mapfile behavior implementation"""

    def test_single_file_default_mapfile(self, tmp_path):
        """Test single file creates default mapfile"""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello john.doe@example.com world")

        # Initialize components
        pattern_engine = PatternEngine()
        data_generator = DataGenerator()
        mapping_manager = MappingManager()
        file_processor = FileProcessor(pattern_engine, data_generator, mapping_manager)

        # Add a simple email pattern
        pattern_engine.add_user_pattern(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"
        )

        # Process the file (should create test.txt.map.json)
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = file_processor.process_directory(str(test_file), mode="anonymize")
        finally:
            os.chdir(old_cwd)

        assert result, "File processing should succeed"

        # Check if mapfile was created
        expected_mapfile = tmp_path / "test.txt.map.json"
        assert (
            expected_mapfile.exists()
        ), f"Mapfile should be created at {expected_mapfile}"

        # Load and verify mapfile contents
        with open(expected_mapfile, "r") as f:
            mapping_data = json.load(f)

        assert "mappings" in mapping_data, "Mapfile should contain mappings"
        assert (
            len(mapping_data["mappings"]) > 0
        ), "Mapfile should contain at least one mapping"
        # Note: session_uuid may be None for single files, which is expected

    def test_directory_default_mapfile(self, tmp_path):
        """Test directory processing creates default mapfile in ~/.redactanon/mappings/"""
        # Create test directory structure
        test_dir = tmp_path / "test_folder"
        test_dir.mkdir()

        # Create test files
        (test_dir / "file1.txt").write_text("Email: alice@example.com")
        (test_dir / "file2.txt").write_text("Phone: 555-123-4567")

        # Initialize components
        pattern_engine = PatternEngine()
        data_generator = DataGenerator()
        mapping_manager = MappingManager()
        file_processor = FileProcessor(pattern_engine, data_generator, mapping_manager)

        # Add patterns
        pattern_engine.add_user_pattern(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"
        )
        pattern_engine.add_user_pattern(r"\b\d{3}-\d{3}-\d{4}\b", "phone")

        # Process the directory
        result = file_processor._process_directory_in_place(test_dir, mode="anonymize")

        assert result, "Directory processing should succeed"

        # Check if .redactanon-id was created
        id_file = test_dir / ".redactanon-id"
        assert id_file.exists(), "ID file should be created in directory"

        with open(id_file, "r") as f:
            uuid_str = f.read().strip()

        assert uuid_str, "UUID should be written to ID file"

        # Check if mapping file was created in default location
        home_dir = Path.home()
        expected_mapping_file = (
            home_dir / ".redactanon" / "mappings" / f"{uuid_str}.json"
        )

        try:
            assert (
                expected_mapping_file.exists()
            ), f"Mapping file should be created at {expected_mapping_file}"

            # Load and verify mapping file contents
            with open(expected_mapping_file, "r") as f:
                mapping_data = json.load(f)

            assert "mappings" in mapping_data, "Mapping file should contain mappings"
            assert (
                "session_uuid" in mapping_data
            ), "Mapping file should contain session_uuid"
            assert mapping_data["session_uuid"] == uuid_str, "Session UUID should match"
            assert (
                len(mapping_data["mappings"]) > 0
            ), "Mapping file should contain at least one mapping"
        finally:
            # Cleanup mapping file
            if expected_mapping_file.exists():
                expected_mapping_file.unlink()

    def test_custom_mapfile_for_file(self, tmp_path):
        """Test custom mapfile for single file processing"""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello john.doe@example.com world")

        custom_mapfile = tmp_path / "custom_map.json"

        # Initialize components
        pattern_engine = PatternEngine()
        data_generator = DataGenerator()
        mapping_manager = MappingManager()
        file_processor = FileProcessor(pattern_engine, data_generator, mapping_manager)

        # Add a simple email pattern
        pattern_engine.add_user_pattern(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"
        )

        # Process the file with custom mapfile
        result = file_processor.process_directory(
            str(test_file), mode="anonymize", mappings_output=str(custom_mapfile)
        )

        # Check if custom mapfile was created
        assert result, "File processing should succeed"
        assert (
            custom_mapfile.exists()
        ), f"Custom mapfile should be created at {custom_mapfile}"

        # Load and verify custom mapfile contents
        with open(custom_mapfile, "r") as f:
            mapping_data = json.load(f)

        assert "mappings" in mapping_data, "Custom mapfile should contain mappings"
        assert (
            "session_uuid" in mapping_data
        ), "Custom mapfile should contain session_uuid"
        assert (
            len(mapping_data["mappings"]) > 0
        ), "Custom mapfile should contain at least one mapping"

    def test_custom_mapfile_for_directory(self, tmp_path):
        """Test custom mapfile for directory processing"""
        # Create test directory structure
        test_dir = tmp_path / "test_folder"
        test_dir.mkdir()

        # Create test file
        (test_dir / "contact.txt").write_text("Phone: 999-888-7777")

        custom_mapfile = tmp_path / "custom_directory_map.json"

        # Initialize components
        pattern_engine = PatternEngine()
        data_generator = DataGenerator()
        mapping_manager = MappingManager()
        file_processor = FileProcessor(pattern_engine, data_generator, mapping_manager)

        # Add pattern
        pattern_engine.add_user_pattern(r"\b\d{3}-\d{3}-\d{4}\b", "phone")

        # Process the directory with custom mapfile
        result = file_processor.process_directory(
            str(test_dir), mode="anonymize", mappings_output=str(custom_mapfile)
        )

        assert result, "Directory processing should succeed"
        assert (
            custom_mapfile.exists()
        ), f"Custom directory mapfile should be created at {custom_mapfile}"

        # Check if .redactanon-id was created
        id_file = test_dir / ".redactanon-id"
        assert id_file.exists(), "ID file should be created in directory"

        # Load and verify custom mapfile contents
        with open(custom_mapfile, "r") as f:
            mapping_data = json.load(f)

        assert "mappings" in mapping_data, "Custom mapfile should contain mappings"
        assert (
            "session_uuid" in mapping_data
        ), "Custom mapfile should contain session_uuid"
        assert (
            len(mapping_data["mappings"]) > 0
        ), "Custom mapfile should contain at least one mapping"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
