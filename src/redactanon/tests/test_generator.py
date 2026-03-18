"""
Tests for RedactAnon Data Generator
"""

import unittest

from src.redactanon.core.data_generator import DataGenerator


class TestDataGenerator(unittest.TestCase):
    """Test cases for the DataGenerator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.generator = DataGenerator()

    def test_init(self):
        """Test DataGenerator initialization."""
        self.assertIsInstance(self.generator.common_domains, list)
        # Note: first_names and last_names attributes are removed since we use Faker

    def test_generate_fake_ip(self):
        """Test generating fake IP addresses."""
        ip = self.generator.generate_fake_ip()
        self.assertIsInstance(ip, str)

        # Check if it matches IPv4 format (more flexible for Faker)
        ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        self.assertRegex(ip, ip_pattern)

        # Check that each octet is valid (0-255)
        octets = ip.split(".")
        for octet in octets:
            self.assertTrue(0 <= int(octet) <= 255)

    def test_generate_fake_ipv6(self):
        """Test generating fake IPv6 addresses."""
        ipv6 = self.generator.generate_fake_ipv6()
        self.assertIsInstance(ipv6, str)

        # Check if it contains IPv6 format elements (more flexible for Faker)
        self.assertIn(":", ipv6)
        # Should have multiple colon-separated parts
        parts = ipv6.split(":")
        self.assertGreater(len(parts), 1)

    def test_generate_fake_email(self):
        """Test generating fake email addresses."""
        email = self.generator.generate_fake_email()
        self.assertIsInstance(email, str)

        # Check if it contains basic email elements (more flexible for Faker)
        self.assertIn("@", email)
        self.assertIn(".", email)
        # Should have username and domain parts
        parts = email.split("@")
        self.assertEqual(len(parts), 2)
        self.assertGreater(len(parts[0]), 0)
        self.assertGreater(len(parts[1]), 0)

    def test_generate_fake_email_with_domain(self):
        """Test generating fake email with specific domain."""
        domain = "example.com"
        email = self.generator.generate_fake_email(domain)
        self.assertIsInstance(email, str)
        self.assertTrue(email.endswith(f"@{domain}"))

    def test_generate_fake_name(self):
        """Test generating fake names."""
        name = self.generator.generate_fake_name()
        self.assertIsInstance(name, str)
        self.assertIn(" ", name)  # Should contain space between first and last name

        # Check that it has reasonable parts (may vary with Faker)
        parts = name.split()
        self.assertGreaterEqual(len(parts), 2)

    def test_generate_fake_phone(self):
        """Test generating fake phone numbers."""
        phone = self.generator.generate_fake_phone()
        self.assertIsInstance(phone, str)

        # Check if it contains phone number elements (more flexible for Faker)
        self.assertGreater(len(phone), 0)
        # Should contain digits
        self.assertTrue(any(c.isdigit() for c in phone))

    def test_generate_fake_ssn(self):
        """Test generating fake SSNs."""
        ssn = self.generator.generate_fake_ssn()
        self.assertIsInstance(ssn, str)

        # Check if it contains SSN elements (more flexible for Faker)
        self.assertIn("-", ssn)
        # Should contain digits
        self.assertTrue(any(c.isdigit() for c in ssn))
        # Should have reasonable length
        self.assertGreater(len(ssn), 10)

    def test_generate_fake_credit_card(self):
        """Test generating fake credit card numbers."""
        cc = self.generator.generate_fake_credit_card()
        self.assertIsInstance(cc, str)

        # Check if it contains credit card elements (more flexible for Faker)
        self.assertGreater(len(cc), 10)
        # Should contain digits
        self.assertTrue(any(c.isdigit() for c in cc))
        # Should start with a digit (likely 4 for Visa)
        self.assertTrue(cc[0].isdigit())

    def test_generate_fake_data(self):
        """Test generating fake data by type."""
        # Test email generation
        email = self.generator.generate_fake_data("email")
        self.assertIsInstance(email, str)
        self.assertIn("@", email)

        # Test IP address generation
        ip = self.generator.generate_fake_data("ip_address")
        self.assertIsInstance(ip, str)
        self.assertIn(".", ip)  # Should be IPv4 by default

        # Test name generation
        name = self.generator.generate_fake_data("name")
        self.assertIsInstance(name, str)
        self.assertIn(" ", name)

        # Test phone generation
        phone = self.generator.generate_fake_data("phone")
        self.assertIsInstance(phone, str)
        # Phone format may vary with Faker, just check it's not empty
        self.assertGreater(len(phone), 0)

        # Test unknown type (should return generic fake data)
        generic = self.generator.generate_fake_data("unknown_type")
        self.assertIsInstance(generic, str)
        self.assertTrue(generic.startswith("FAKE_"))


if __name__ == "__main__":
    unittest.main()
