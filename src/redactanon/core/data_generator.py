"""
Data Generator for RedactAnon
Generates realistic fake data for replacement values using Faker library.
"""

import random
from typing import Optional

from faker import Faker


class DataGenerator:
    """Generator for creating realistic fake data replacements using Faker."""

    def __init__(self):
        """Initialize the data generator with Faker instance."""
        self.fake = Faker()
        # Set seed for reproducible results in testing
        Faker.seed(42)
        random.seed(42)

        # Common domain names for email generation (fallback)
        self.common_domains = [
            "example.com",
            "test.com",
            "demo.org",
            "sample.net",
            "fake.email",
        ]

    def generate_fake_ip(self) -> str:
        """Generate a fake IPv4 address.

        Returns:
            Fake IP address string
        """
        return self.fake.ipv4()

    def generate_fake_ipv6(self) -> str:
        """Generate a fake IPv6 address.

        Returns:
            Fake IPv6 address string
        """
        return self.fake.ipv6()

    def generate_fake_email(self, original_domain: Optional[str] = None) -> str:
        """Generate a fake email address.

        Args:
            original_domain: Optional original domain to preserve structure

        Returns:
            Fake email address string
        """
        if original_domain:
            # Generate email with specific domain using Faker
            first_name = self.fake.first_name().lower()
            last_name = self.fake.last_name().lower()
            # Remove special characters and spaces
            first_name = "".join(c for c in first_name if c.isalnum())
            last_name = "".join(c for c in last_name if c.isalnum())
            return f"{first_name}.{last_name}@{original_domain}"
        else:
            # Generate completely random email using Faker
            return self.fake.email()

    def generate_fake_name(self) -> str:
        """Generate a fake name.

        Returns:
            Fake name string
        """
        return self.fake.name()

    def generate_fake_phone(self) -> str:
        """Generate a fake phone number.

        Returns:
            Fake phone number string
        """
        return self.fake.phone_number()

    def generate_fake_ssn(self) -> str:
        """Generate a fake Social Security Number.

        Returns:
            Fake SSN string
        """
        return self.fake.ssn()

    def generate_fake_credit_card(self) -> str:
        """Generate a fake credit card number.

        Returns:
            Fake credit card number string
        """
        return self.fake.credit_card_number(card_type="visa")

    def generate_fake_data(
        self, data_type: str, original_value: Optional[str] = None
    ) -> str:
        """Generate fake data based on the type.

        Args:
            data_type: Type of data to generate
            original_value: Original value for reference

        Returns:
            Generated fake data string
        """
        if data_type == "email":
            return self.generate_fake_email()
        elif data_type == "ip_address":
            # Determine if IPv4 or IPv6 based on original or randomly
            if original_value and ":" in original_value:
                return self.generate_fake_ipv6()
            return self.generate_fake_ip()
        elif data_type == "name":
            return self.generate_fake_name()
        elif data_type == "phone":
            return self.generate_fake_phone()
        elif data_type == "ssn":
            return self.generate_fake_ssn()
        elif data_type == "credit_card":
            return self.generate_fake_credit_card()
        else:
            # Generic fallback
            if original_value:
                return f"REDACTED_{random.randint(1000, 9999)}"
            return f"FAKE_{random.randint(100000, 999999)}"
