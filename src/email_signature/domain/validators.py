"""Input validation for email signature data."""

import re


class InputValidator:
    """Validates user input according to business rules."""

    # Email regex pattern - basic validation for format
    EMAIL_PATTERN = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

    # Portuguese phone number patterns
    # Supports formats like: +351 XXX XXX XXX, 351XXXXXXXXX, XXX XXX XXX, XXXXXXXXX
    PHONE_PATTERN = re.compile(r"^(\+351\s?)?(\d{3}\s?\d{3}\s?\d{3}|\d{9})$")

    @staticmethod
    def validate_required_field(value: str, field_name: str) -> tuple[bool, str]:
        """Validate that a required field is not empty.

        Args:
            value: The field value to validate
            field_name: Name of the field for error messages

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        if not value or not value.strip():
            return False, f"{field_name} is required and cannot be empty or whitespace only"
        return True, ""

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email format.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        if not email or not email.strip():
            return False, "Email is required and cannot be empty"

        if not InputValidator.EMAIL_PATTERN.match(email.strip()):
            return (
                False,
                "Email must be in valid format (e.g., user@example.com) with @ symbol and domain",
            )

        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> tuple[bool, str]:
        """Validate phone number format for Portuguese numbers.

        Args:
            phone: Phone number to validate

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        # Empty phone is allowed (optional field)
        if not phone or not phone.strip():
            return True, ""

        # Remove common separators for validation
        cleaned_phone = phone.strip().replace(" ", "").replace("-", "")

        if not InputValidator.PHONE_PATTERN.match(cleaned_phone):
            return (
                False,
                "Phone number must be in Portuguese format (e.g., +351 XXX XXX XXX, "
                "351XXXXXXXXX, XXX XXX XXX, or XXXXXXXXX with 9 digits)",
            )

        return True, ""
