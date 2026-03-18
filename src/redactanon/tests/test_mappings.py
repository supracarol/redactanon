"""
Tests for RedactAnon Mapping Manager
"""

import os
import tempfile
import unittest

from ..core.mapping_manager import MappingManager


class TestMappingManager(unittest.TestCase):
    """Test cases for the MappingManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.mappings_dir = os.path.join(self.test_dir, "mappings")
        self.manager = MappingManager(self.mappings_dir)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Clean up temporary directory
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        """Test MappingManager initialization."""
        self.assertIsInstance(self.manager.mappings, dict)
        self.assertIsInstance(self.manager.reverse_mappings, dict)
        self.assertIsNone(self.manager.session_uuid)
        self.assertTrue(os.path.exists(self.mappings_dir))

    def test_store_and_retrieve_mapping(self):
        """Test storing and retrieving mappings."""
        original = "John Doe"
        fake = "Anonymous User"

        # Store mapping
        self.manager.store_mapping(original, fake)

        # Retrieve mapping
        retrieved_fake = self.manager.get_fake_value(original)
        retrieved_original = self.manager.get_original_value(fake)

        self.assertEqual(retrieved_fake, fake)
        self.assertEqual(retrieved_original, original)

    def test_generate_session_uuid(self):
        """Test generating session UUID."""
        uuid1 = self.manager.generate_session_uuid()
        self.assertIsInstance(uuid1, str)
        self.assertIsNotNone(self.manager.session_uuid)

        # Generate another UUID (should be different)
        uuid2 = self.manager.generate_session_uuid()
        self.assertNotEqual(uuid1, uuid2)

    def test_save_and_load_mappings(self):
        """Test saving and loading mappings."""
        # Add some mappings
        self.manager.store_mapping("Original Value 1", "Fake Value 1")
        self.manager.store_mapping("Original Value 2", "Fake Value 2")

        # Save mappings
        saved_path = self.manager.save_mappings()

        # Check that file was created
        self.assertTrue(os.path.exists(saved_path))

        # Create new manager and load mappings
        new_manager = MappingManager(self.mappings_dir)
        new_manager.load_mappings(saved_path)

        # Check that mappings were loaded correctly
        self.assertEqual(new_manager.get_fake_value("Original Value 1"), "Fake Value 1")
        self.assertEqual(
            new_manager.get_original_value("Fake Value 2"), "Original Value 2"
        )

    def test_create_and_read_id_file(self):
        """Test creating and reading ID files."""
        # Create a test directory
        test_dir = os.path.join(self.test_dir, "test_processed_dir")
        os.makedirs(test_dir, exist_ok=True)

        # Create ID file
        id_file_path = self.manager.create_id_file(test_dir)

        # Check that file was created
        self.assertTrue(os.path.exists(id_file_path))

        # Read ID file
        uuid_from_file = self.manager.read_id_file(test_dir)
        self.assertEqual(uuid_from_file, self.manager.session_uuid)

    def test_find_mapping_file_by_uuid(self):
        """Test finding mapping file by UUID."""
        # Add some mappings and save
        self.manager.store_mapping("test", "fake")
        saved_path = self.manager.save_mappings()

        # Find mapping file by UUID
        found_path = self.manager.find_mapping_file_by_uuid(self.manager.session_uuid)
        self.assertEqual(found_path, saved_path)

        # Try to find non-existent UUID
        not_found = self.manager.find_mapping_file_by_uuid("non-existent-uuid")
        self.assertIsNone(not_found)

    def test_get_all_mappings(self):
        """Test getting all mappings."""
        # Add some mappings
        self.manager.store_mapping("key1", "value1")
        self.manager.store_mapping("key2", "value2")

        # Get all mappings
        all_mappings = self.manager.get_all_mappings()
        self.assertIsInstance(all_mappings, dict)
        self.assertEqual(len(all_mappings), 2)
        self.assertIn("key1", all_mappings)
        self.assertIn("key2", all_mappings)

    def test_clear_mappings(self):
        """Test clearing mappings."""
        # Add some mappings
        self.manager.store_mapping("key1", "value1")
        self.manager.store_mapping("key2", "value2")

        # Clear mappings
        self.manager.clear_mappings()

        # Check that mappings are cleared
        self.assertEqual(len(self.manager.mappings), 0)
        self.assertEqual(len(self.manager.reverse_mappings), 0)
        self.assertIsNone(self.manager.session_uuid)


if __name__ == "__main__":
    unittest.main()
