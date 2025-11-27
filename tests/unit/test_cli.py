"""Unit tests for CLI user interaction."""

from unittest.mock import patch

from src.email_signature.domain.models import SignatureData
from src.email_signature.domain.validators import InputValidator
from src.email_signature.interface.cli import CLI


def test_collect_user_data_with_valid_inputs() -> None:
    """Test CLI collects user data successfully with valid inputs.

    Validates: Requirements 1.1-1.7

    When user provides all valid inputs, the CLI should collect
    and return a SignatureData object with all the information.
    """
    # Given a CLI instance with validator
    validator = InputValidator()
    cli = CLI(validator)

    # Mock user inputs - all valid
    user_inputs = [
        "John Doe",  # name
        "Software Engineer",  # position
        "123 Main St, Anytown, USA",  # address
        "john.doe@example.com",  # email
        "900000001",  # phone (fictional 9-digit format)
        "900000002",  # mobile (fictional 9-digit format)
        "www.example.com",  # website
    ]

    # When collecting user data with valid inputs
    with patch("builtins.input", side_effect=user_inputs):
        result = cli.collect_user_data()

    # Then it should return a SignatureData object with correct values
    assert isinstance(result, SignatureData)
    assert result.name == "John Doe"
    assert result.position == "Software Engineer"
    assert result.address == "123 Main St, Anytown, USA"
    assert result.email == "john.doe@example.com"
    assert result.phone == "900000001"
    assert result.mobile == "900000002"
    assert result.website == "www.example.com"


def test_collect_user_data_with_default_website() -> None:
    """Test CLI uses default website when user skips it.

    Validates: Requirements 1.7

    When user provides empty input for website, the CLI should
    use the default value "www.example.com".
    """
    # Given a CLI instance
    validator = InputValidator()
    cli = CLI(validator)

    # Mock user inputs with empty website
    user_inputs = [
        "Jane Smith",
        "Product Manager",
        "456 Oak Ave, Springfield, USA",
        "jane@example.com",
        "900000003",
        "900000004",
        "",  # empty website - should use default
    ]

    # When collecting user data
    with patch("builtins.input", side_effect=user_inputs):
        result = cli.collect_user_data()

    # Then website should be the default value
    assert result.website == "www.example.com"


def test_collect_user_data_with_optional_fields_empty() -> None:
    """Test CLI handles empty optional fields correctly.

    Validates: Requirements 1.5

    When user leaves optional fields (phone, mobile) empty,
    the CLI should accept them and create SignatureData.
    """
    # Given a CLI instance
    validator = InputValidator()
    cli = CLI(validator)

    # Mock user inputs with empty optional fields
    user_inputs = [
        "Alice Johnson",
        "Designer",
        "789 Pine Rd, Riverside, USA",
        "alice@example.com",
        "",  # empty phone (optional)
        "",  # empty mobile (optional)
        "",  # empty website (will use default)
    ]

    # When collecting user data
    with patch("builtins.input", side_effect=user_inputs):
        result = cli.collect_user_data()

    # Then optional fields should be empty strings
    assert result.phone == ""
    assert result.mobile == ""
    assert result.website == "www.example.com"


def test_validation_error_handling_and_reentry() -> None:
    """Test CLI handles validation errors and allows re-entry.

    Validates: Requirements 2.5

    When user provides invalid input, the CLI should display
    an error message and prompt for re-entry until valid input
    is provided.
    """
    # Given a CLI instance
    validator = InputValidator()
    cli = CLI(validator)

    # Mock user inputs with initial invalid values followed by valid ones
    user_inputs = [
        "Bob Wilson",
        "",  # invalid position (empty)
        "Senior Developer",  # valid position (retry)
        "321 Elm St, Lakeside, USA",
        "invalid-email",  # invalid email (no @)
        "bob@example.com",  # valid email (retry)
        "12345",  # invalid phone (wrong format)
        "900000005",  # valid phone (retry)
        "",  # empty mobile (valid - optional)
        "",  # empty website (will use default)
    ]

    # When collecting user data with validation errors
    with patch("builtins.input", side_effect=user_inputs):
        with patch("builtins.print") as mock_print:
            result = cli.collect_user_data()

    # Then it should eventually return valid SignatureData
    assert result.name == "Bob Wilson"
    assert result.position == "Senior Developer"
    assert result.email == "bob@example.com"
    assert result.phone == "900000005"

    # And error messages should have been displayed
    print_calls = [str(call) for call in mock_print.call_args_list]
    error_displayed = any("Error:" in str(call) for call in print_calls)
    assert error_displayed


def test_display_welcome_shows_message() -> None:
    """Test display_welcome shows welcome message."""
    # Given a CLI instance
    validator = InputValidator()
    cli = CLI(validator)

    # When displaying welcome message
    with patch("builtins.print") as mock_print:
        cli.display_welcome()

    # Then it should print welcome information
    print_calls = [str(call) for call in mock_print.call_args_list]
    output = " ".join(print_calls)

    assert "Email Signature Generator" in output
    assert "information" in output.lower()


def test_display_success_shows_details() -> None:
    """Test display_success shows output details."""
    # Given a CLI instance
    validator = InputValidator()
    cli = CLI(validator)

    # When displaying success message
    output_path = "/path/to/signature.png"
    dimensions = (800, 300)

    with patch("builtins.print") as mock_print:
        cli.display_success(output_path, dimensions)

    # Then it should print success information with path and dimensions
    print_calls = [str(call) for call in mock_print.call_args_list]
    output = " ".join(print_calls)

    assert "Success" in output
    assert output_path in output
    assert "800x300" in output


def test_display_error_shows_message() -> None:
    """Test display_error shows error message."""
    # Given a CLI instance
    validator = InputValidator()
    cli = CLI(validator)

    # When displaying error message
    error_message = "Logo file not found"

    with patch("builtins.print") as mock_print:
        cli.display_error(error_message)

    # Then it should print error information
    print_calls = [str(call) for call in mock_print.call_args_list]
    output = " ".join(print_calls)

    assert "Error" in output
    assert error_message in output


def test_multiple_validation_retries() -> None:
    """Test CLI allows multiple retries for validation errors.

    Validates: Requirements 2.1, 2.2, 2.5

    When user provides invalid input multiple times, the CLI
    should continue prompting until valid input is received.
    """
    # Given a CLI instance
    validator = InputValidator()
    cli = CLI(validator)

    # Mock user inputs with multiple invalid attempts
    user_inputs = [
        "",  # invalid name (empty) - attempt 1
        "   ",  # invalid name (whitespace) - attempt 2
        "Charlie Brown",  # valid name - attempt 3
        "Manager",
        "555 Maple Dr, Hilltown, USA",
        "charlie@example.com",
        "",  # empty phone (valid - optional)
        "",  # empty mobile (valid - optional)
        "",  # empty website
    ]

    # When collecting user data with multiple validation failures
    with patch("builtins.input", side_effect=user_inputs):
        result = cli.collect_user_data()

    # Then it should eventually succeed with valid data
    assert result.name == "Charlie Brown"
    assert result.position == "Manager"
