"""Command-line interface for email signature generator."""

from collections.abc import Callable

from ..domain.models import SignatureData
from ..domain.validators import InputValidator


class CLI:
    """Command-line interface for user interaction."""

    def __init__(self, validator: InputValidator):
        """Initialize CLI with validator.

        Args:
            validator: InputValidator instance for validating user input
        """
        self.validator = validator

    def display_welcome(self) -> None:
        """Display welcome message and instructions."""
        print("=" * 60)
        print("Email Signature Generator")
        print("=" * 60)
        print("\nPlease provide your information to generate your email signature.")
        print("Required fields are marked with *\n")

    def collect_user_data(self) -> SignatureData:
        """Collect and validate user input.

        Returns:
            SignatureData object with validated user information
        """
        # Collect name with validation
        name = self._collect_field_with_validation(
            prompt="Name*: ",
            field_name="Name",
            validator_func=self.validator.validate_required_field,
        )

        # Collect position with validation
        position = self._collect_field_with_validation(
            prompt="Position*: ",
            field_name="Position",
            validator_func=self.validator.validate_required_field,
        )

        # Collect address with validation
        address = self._collect_field_with_validation(
            prompt="Address*: ",
            field_name="Address",
            validator_func=self.validator.validate_required_field,
        )

        # Collect email with validation
        email = self._collect_field_with_validation(
            prompt="Email*: ",
            field_name="Email",
            validator_func=self.validator.validate_email,
            pass_field_name=False,
        )

        # Collect phone (optional) with validation
        phone = self._collect_field_with_validation(
            prompt="Phone (optional): ",
            field_name="Phone",
            validator_func=self.validator.validate_phone,
            pass_field_name=False,
            required=False,
        )

        # Collect mobile (optional) with validation
        mobile = self._collect_field_with_validation(
            prompt="Mobile (optional): ",
            field_name="Mobile",
            validator_func=self.validator.validate_phone,
            pass_field_name=False,
            required=False,
        )

        # Collect website (optional)
        website = input("Website (press Enter for default 'www.eos.pt'): ").strip()
        if not website:
            website = "www.eos.pt"

        # Create and return SignatureData
        return SignatureData(
            name=name,
            position=position,
            address=address,
            phone=phone,
            mobile=mobile,
            email=email,
            website=website,
        )

    def _collect_field_with_validation(
        self,
        prompt: str,
        field_name: str,
        validator_func: Callable[..., tuple[bool, str]],
        pass_field_name: bool = True,
        required: bool = True,
    ) -> str:
        """Collect a field with validation loop.

        Args:
            prompt: Prompt to display to user
            field_name: Name of the field for error messages
            validator_func: Validation function to use
            pass_field_name: Whether to pass field_name to validator
            required: Whether the field is required

        Returns:
            Validated field value
        """
        while True:
            value = input(prompt).strip()

            # Skip validation for optional empty fields
            if not required and not value:
                return value

            # Validate the input
            if pass_field_name:
                is_valid, error_message = validator_func(value, field_name)
            else:
                is_valid, error_message = validator_func(value)

            if is_valid:
                return value
            else:
                print(f"Error: {error_message}")
                print("Please try again.\n")

    def display_success(self, output_path: str, dimensions: tuple[int, int]) -> None:
        """Display success message with output details.

        Args:
            output_path: Path where signature was saved
            dimensions: Tuple of (width, height) of generated image
        """
        print("\n" + "=" * 60)
        print("Success!")
        print("=" * 60)
        print("\nYour email signature has been generated successfully!")
        print(f"File: {output_path}")
        print(f"Dimensions: {dimensions[0]}x{dimensions[1]} pixels")
        print("\nYou can now use this image in your email signature.")

    def display_error(self, error_message: str) -> None:
        """Display error message to user.

        Args:
            error_message: Error message to display
        """
        print("\n" + "=" * 60)
        print("Error")
        print("=" * 60)
        print(f"\n{error_message}")
        print("\nPlease check the error and try again.")
