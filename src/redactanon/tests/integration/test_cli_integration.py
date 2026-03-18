"""
CLI integration tests for RedactAnon
"""

import json
import os
import subprocess
from pathlib import Path

import pytest


class TestCLIIntegration:
    """Test CLI integration behavior"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, tmp_path):
        """Setup and teardown for each test"""
        self.original_cwd = os.getcwd()
        os.chdir(tmp_path)
        yield
        os.chdir(self.original_cwd)

    def run_redactanon(self, *args):
        """Run redactanon command and return result"""
        cmd = ["redactanon"] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result
        except subprocess.TimeoutExpired:
            pytest.fail(f"Command timed out: {' '.join(cmd)}")
        except FileNotFoundError:
            pytest.skip("redactanon command not found - skipping CLI tests")

    def test_single_file_default_mapfile_cli(self, tmp_path):
        """Test single file anonymization creates default mapfile via CLI"""
        # Create test file with data matching built-in patterns
        test_file = tmp_path / "test_file.txt"
        test_file.write_text(
            "Contact John Doe at john.doe@example.com or call +1 (555) 123-4567"
        )

        # Run anonymization
        result = self.run_redactanon("anon", str(test_file))

        assert result.returncode == 0, f"Command failed with output: {result.stderr}"

        # Check if mapfile was created
        expected_mapfile = tmp_path / "test_file.txt.map.json"
        assert (
            expected_mapfile.exists()
        ), f"Mapfile should be created at {expected_mapfile}"

        # Check if original file was processed
        assert test_file.exists(), "Original file should still exist"

        # Load and verify mapfile contents
        with open(expected_mapfile, "r") as f:
            mapping_data = json.load(f)

        assert "mappings" in mapping_data, "Mapfile should contain mappings"
        assert len(mapping_data["mappings"]) > 0, "Mapfile should contain mappings"

    def test_directory_default_mapfile_cli(self, tmp_path):
        """Test directory anonymization creates default mapfile via CLI"""
        # Create test directory structure
        test_folder = tmp_path / "test_folder"
        test_folder.mkdir()

        # Create test files
        (test_folder / "file1.txt").write_text("Email: alice.smith@company.com")
        (test_folder / "file2.txt").write_text("SSN: 123-45-6789 and IP: 192.168.1.100")

        # Run anonymization
        result = self.run_redactanon("anon", str(test_folder))

        assert result.returncode == 0, f"Command failed with output: {result.stderr}"

        # Check if .redactanon-id was created
        id_file = test_folder / ".redactanon-id"
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
            ), "Mapping file should contain mappings"
        finally:
            # Cleanup mapping file
            if expected_mapping_file.exists():
                expected_mapping_file.unlink()

    def test_single_file_custom_mapfile_cli(self, tmp_path):
        """Test single file with custom mapfile via CLI"""
        # Create test file with data matching built-in patterns
        test_file = tmp_path / "custom_test.txt"
        test_file.write_text(
            "Contact Bob Wilson at bob.wilson@test.org or call 555-0199"
        )

        custom_mapfile = "my_custom_map.json"

        # Run anonymization with custom mapfile
        result = self.run_redactanon(
            "anon", "--mapfile", custom_mapfile, str(test_file)
        )

        assert result.returncode == 0, f"Command failed with output: {result.stderr}"

        # Check if custom mapfile was created
        assert Path(
            custom_mapfile
        ).exists(), f"Custom mapfile should be created at {custom_mapfile}"

        # Load and verify custom mapfile contents
        with open(custom_mapfile, "r") as f:
            mapping_data = json.load(f)

        assert "mappings" in mapping_data, "Custom mapfile should contain mappings"
        assert (
            len(mapping_data["mappings"]) > 0
        ), "Custom mapfile should contain mappings"

    def test_directory_custom_mapfile_cli(self, tmp_path):
        """Test directory with custom mapfile via CLI"""
        # Create test directory structure
        custom_folder = tmp_path / "custom_folder"
        custom_folder.mkdir()

        # Create test file
        (custom_folder / "contact.txt").write_text("Phone: 999-888-7777")

        custom_mapfile = "custom_directory_map.json"

        # Run anonymization with custom mapfile
        result = self.run_redactanon(
            "anon", "--mapfile", custom_mapfile, str(custom_folder)
        )

        assert result.returncode == 0, f"Command failed with output: {result.stderr}"

        # Check if custom mapfile was created
        assert Path(
            custom_mapfile
        ).exists(), f"Custom mapfile should be created at {custom_mapfile}"

        # Check if .redactanon-id was created
        id_file = custom_folder / ".redactanon-id"
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
        ), "Custom mapfile should contain mappings"

    def test_help_commands(self):
        """Test help commands work correctly"""
        # Test main help
        result = self.run_redactanon("--help")
        assert result.returncode == 0, f"Main help failed: {result.stderr}"
        assert "anon" in result.stdout and "restore" in result.stdout

        # Test anon help
        result = self.run_redactanon("anon", "--help")
        assert result.returncode == 0, f"Anon help failed: {result.stderr}"
        assert "--mapfile" in result.stdout

        # Test restore help
        result = self.run_redactanon("restore", "--help")
        assert result.returncode == 0, f"Restore help failed: {result.stderr}"

    def test_simple_config_custom_replacements(self, tmp_path):
        """Test simple config with custom replacement values"""
        # Create simple config file with custom replacements
        config_file = tmp_path / "simple_config.txt"
        config_content = """John Doe=Anonymous User
192.168.1.100=10.0.0.1
confidential-project=public-project
+1-555-0199
secret-api-key"""
        config_file.write_text(config_content)

        # Create test file with data matching simple config patterns
        test_file = tmp_path / "test_file.txt"
        test_file.write_text(
            "Contact John Doe at john.doe@example.com or call +1-555-0199 for more information about the confidential-project. The server is running on 192.168.1.100 and uses secret-api-key for authentication."
        )

        # Run anonymization with simple config
        result = self.run_redactanon(
            "anon", "--simple-config", str(config_file), str(test_file)
        )

        assert result.returncode == 0, f"Command failed with output: {result.stderr}"

        # Check if mapfile was created
        expected_mapfile = tmp_path / "test_file.txt.map.json"
        assert (
            expected_mapfile.exists()
        ), f"Mapfile should be created at {expected_mapfile}"

        # Load and verify mapfile contents
        with open(expected_mapfile, "r") as f:
            mapping_data = json.load(f)

        assert "mappings" in mapping_data, "Mapfile should contain mappings"
        mappings = mapping_data["mappings"]

        # Verify custom replacements are preserved
        assert (
            mappings.get("John Doe") == "Anonymous User"
        ), "Custom replacement for 'John Doe' should be preserved"
        assert (
            mappings.get("192.168.1.100") == "10.0.0.1"
        ), "Custom replacement for IP should be preserved"
        assert (
            mappings.get("confidential-project") == "public-project"
        ), "Custom replacement for project name should be preserved"

        # Verify patterns without custom replacements get generated values
        assert (
            "+1-555-0199" in mappings
        ), "Pattern without custom replacement should be mapped"
        assert (
            "secret-api-key" in mappings
        ), "Pattern without custom replacement should be mapped"

        # Verify builtin patterns also work
        assert (
            "john.doe@example.com" in mappings
        ), "Builtin email pattern should also be detected"

        # Check the actual file content
        anonymized_content = test_file.read_text()

        # Verify custom replacements are used in the file
        assert (
            "Anonymous User" in anonymized_content
        ), "Custom replacement 'Anonymous User' should appear in file"
        assert (
            "public-project" in anonymized_content
        ), "Custom replacement 'public-project' should appear in file"

        # Verify the custom IP replacement is used
        assert (
            "10.0.0.1" in anonymized_content
        ), "Custom IP replacement '10.0.0.1' should appear in file"

        # Verify other values are replaced (but not with custom values since they weren't specified)
        assert (
            "John Doe" not in anonymized_content
        ), "Original 'John Doe' should be replaced"
        assert (
            "192.168.1.100" not in anonymized_content
        ), "Original IP should be replaced"
        assert (
            "confidential-project" not in anonymized_content
        ), "Original project name should be replaced"
        assert (
            "+1-555-0199" not in anonymized_content
        ), "Original phone should be replaced"
        assert (
            "secret-api-key" not in anonymized_content
        ), "Original API key should be replaced"

        # Test restoration
        restore_result = self.run_redactanon("restore", str(test_file))
        assert (
            restore_result.returncode == 0
        ), f"Restore command failed: {restore_result.stderr}"

        # Verify file is restored to original content
        restored_content = test_file.read_text()
        original_content = "Contact John Doe at john.doe@example.com or call +1-555-0199 for more information about the confidential-project. The server is running on 192.168.1.100 and uses secret-api-key for authentication."
        assert (
            restored_content == original_content
        ), "File should be restored to original content"

    def test_simple_config_only_no_defaults(self, tmp_path):
        """Test simple config with --no-defaults flag"""
        # Create simple config file
        config_file = tmp_path / "simple_config.txt"
        config_content = "TEST_USER=anonymous_user"
        config_file.write_text(config_content)

        # Create test file with only simple config pattern (no builtin patterns)
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("User: TEST_USER")

        # Run anonymization with simple config and --no-defaults
        result = self.run_redactanon(
            "anon", "--simple-config", str(config_file), "--no-defaults", str(test_file)
        )

        assert result.returncode == 0, f"Command failed with output: {result.stderr}"

        # Check mapfile
        expected_mapfile = tmp_path / "test_file.txt.map.json"
        assert (
            expected_mapfile.exists()
        ), f"Mapfile should be created at {expected_mapfile}"

        # Load mappings
        with open(expected_mapfile, "r") as f:
            mapping_data = json.load(f)

        mappings = mapping_data["mappings"]

        # Should only have simple config patterns
        assert len(mappings) == 1, f"Should only have 1 mapping, got {len(mappings)}"
        assert "TEST_USER" in mappings, "Simple config pattern should be mapped"
        assert (
            mappings["TEST_USER"] == "anonymous_user"
        ), "Custom replacement should be preserved"

        # Check file content
        anonymized_content = test_file.read_text()
        assert (
            "anonymous_user" in anonymized_content
        ), "Custom replacement should be used"
        assert (
            "TEST_USER" not in anonymized_content
        ), "Original value should be replaced"

    def test_simple_config_with_directory(self, tmp_path):
        """Test simple config with directory processing"""
        # Create simple config file
        config_file = tmp_path / "simple_config.txt"
        config_content = "PROJECT_NAME=ANONYMOUS_PROJECT"
        config_file.write_text(config_content)

        # Create test directory
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Create test files
        (test_dir / "file1.txt").write_text("Working on PROJECT_NAME")
        (test_dir / "file2.txt").write_text("Project: PROJECT_NAME")

        # Run anonymization
        result = self.run_redactanon(
            "anon", "--simple-config", str(config_file), str(test_dir)
        )

        assert result.returncode == 0, f"Command failed with output: {result.stderr}"

        # Check if .redactanon-id was created
        id_file = test_dir / ".redactanon-id"
        assert id_file.exists(), "ID file should be created in directory"

        # Check mapping file exists in default location
        with open(id_file, "r") as f:
            uuid_str = f.read().strip()

        home_dir = Path.home()
        expected_mapping_file = (
            home_dir / ".redactanon" / "mappings" / f"{uuid_str}.json"
        )

        try:
            assert (
                expected_mapping_file.exists()
            ), f"Mapping file should be created at {expected_mapping_file}"

            # Load and verify mappings
            with open(expected_mapping_file, "r") as f:
                mapping_data = json.load(f)

            mappings = mapping_data["mappings"]
            assert "PROJECT_NAME" in mappings, "Pattern should be mapped"
            assert (
                mappings["PROJECT_NAME"] == "ANONYMOUS_PROJECT"
            ), "Custom replacement should be preserved"

            # Check file contents
            file1_content = (test_dir / "file1.txt").read_text()
            file2_content = (test_dir / "file2.txt").read_text()

            assert (
                "ANONYMOUS_PROJECT" in file1_content
            ), "Custom replacement should appear in file1"
            assert (
                "ANONYMOUS_PROJECT" in file2_content
            ), "Custom replacement should appear in file2"
            assert (
                "PROJECT_NAME" not in file1_content
            ), "Original value should be replaced in file1"
            assert (
                "PROJECT_NAME" not in file2_content
            ), "Original value should be replaced in file2"

        finally:
            # Cleanup mapping file
            if expected_mapping_file.exists():
                expected_mapping_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
