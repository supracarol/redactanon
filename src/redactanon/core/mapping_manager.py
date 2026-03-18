"""
Mapping Manager for RedactAnon
Handles storage and retrieval of value mappings for reversible anonymization.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Optional


class MappingManager:
    """Manager for storing and retrieving value mappings."""

    def __init__(self, mappings_dir: Optional[str] = None):
        """Initialize the mapping manager.

        Args:
            mappings_dir: Directory to store mapping files.
                Defaults to ~/.redactanon/mappings/
        """
        if mappings_dir is None:
            home_dir = Path.home()
            self.mappings_dir = home_dir / ".redactanon" / "mappings"
        else:
            self.mappings_dir = Path(mappings_dir)

        # Create mappings directory if it doesn't exist
        self.mappings_dir.mkdir(parents=True, exist_ok=True)

        # Current mappings storage
        self.mappings: Dict[str, str] = {}
        self.reverse_mappings: Dict[str, str] = {}

        # UUID for current session
        self.session_uuid: Optional[str] = None

    def generate_session_uuid(self) -> str:
        """Generate a UUID for the current processing session.

        Returns:
            UUID string
        """
        self.session_uuid = str(uuid.uuid4())
        return self.session_uuid

    def store_mapping(self, original: str, fake: str) -> None:
        """Store a mapping between original and fake values.

        Args:
            original: Original sensitive value
            fake: Generated fake value
        """
        self.mappings[original] = fake
        self.reverse_mappings[fake] = original

    def retrieve_mapping(self, fake: str) -> Optional[str]:
        """Retrieve the original value for a fake value.

        Args:
            fake: Fake value to look up

        Returns:
            Original value if found, None otherwise
        """
        return self.reverse_mappings.get(fake)

    def get_original_value(self, fake: str) -> Optional[str]:
        """Get original value from fake value (alias for retrieve_mapping).

        Args:
            fake: Fake value to look up

        Returns:
            Original value if found, None otherwise
        """
        return self.retrieve_mapping(fake)

    def get_fake_value(self, original: str) -> Optional[str]:
        """Get fake value from original value.

        Args:
            original: Original value to look up

        Returns:
            Fake value if found, None otherwise
        """
        return self.mappings.get(original)

    def save_mappings(self, filepath: Optional[str] = None) -> str:
        """Save current mappings to a file.

        Args:
            filepath: Optional specific file path. If None, uses session UUID.

        Returns:
            Path to the saved mapping file
        """
        if filepath is None:
            if self.session_uuid is None:
                self.generate_session_uuid()
            filepath = str(self.mappings_dir / f"{self.session_uuid}.json")
        else:
            filepath_path = Path(filepath)
            # Ensure directory exists
            filepath_path.parent.mkdir(parents=True, exist_ok=True)
            filepath = str(filepath_path)

        mapping_data = {"mappings": self.mappings, "session_uuid": self.session_uuid}

        with open(filepath, "w") as f:
            json.dump(mapping_data, f, indent=2)

        return filepath

    def load_mappings(self, filepath: str) -> None:
        """Load mappings from a file.

        Args:
            filepath: Path to the mapping file
        """
        with open(filepath, "r") as f:
            mapping_data = json.load(f)

        self.mappings = mapping_data.get("mappings", {})
        # Derive reverse mappings from mappings
        self.reverse_mappings = {
            fake: original for original, fake in self.mappings.items()
        }
        self.session_uuid = mapping_data.get("session_uuid")

    def create_id_file(self, directory_path: str) -> str:
        """Create a .redactanon-id file in the processed directory.

        Args:
            directory_path: Path to the processed directory

        Returns:
            Path to the created ID file
        """
        if self.session_uuid is None:
            self.generate_session_uuid()

        id_file_path = Path(directory_path) / ".redactanon-id"
        with open(id_file_path, "w") as f:
            f.write(self.session_uuid or "")

        return str(id_file_path)

    def read_id_file(self, directory_path: str) -> Optional[str]:
        """Read the UUID from a .redactanon-id file.

        Args:
            directory_path: Path to the directory containing the ID file

        Returns:
            UUID string if found, None otherwise
        """
        id_file_path = Path(directory_path) / ".redactanon-id"
        if id_file_path.exists():
            with open(id_file_path, "r") as f:
                return f.read().strip()
        return None

    def find_mapping_file_by_uuid(self, uuid_str: str) -> Optional[str]:
        """Find a mapping file by its UUID.

        Args:
            uuid_str: UUID to search for

        Returns:
            Path to mapping file if found, None otherwise
        """
        mapping_file = self.mappings_dir / f"{uuid_str}.json"
        if mapping_file.exists():
            return str(mapping_file)
        return None

    def get_all_mappings(self) -> Dict[str, str]:
        """Get all current mappings.

        Returns:
            Dictionary of original -> fake mappings
        """
        return self.mappings.copy()

    def clear_mappings(self) -> None:
        """Clear all current mappings."""
        self.mappings.clear()
        self.reverse_mappings.clear()
        self.session_uuid = None
