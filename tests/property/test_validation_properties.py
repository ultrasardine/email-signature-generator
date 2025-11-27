"""Property-based tests for validation logic."""

from hypothesis import given
from hypothesis import strategies as st

from src.email_signature.domain.models import SignatureData
from src.email_signature.domain.validators import InputValidator

# Strategy for generating non-empty strings
non_empty_string = st.text(min_size=1).filter(lambda s: s.strip())

# Strategy for generating empty or whitespace-only strings
empty_or_whitespace = st.one_of(
    st.just(""),
    st.text(max_size=0),
    st.text().filter(lambda s: not s.strip()),
)


@given(
    name=non_empty_string,
    position=non_empty_string,
    address=non_empty_string,
    phone=st.text(),
    mobile=st.text(),
    email=non_empty_string,
    website=st.text(),
)
def test_valid_input_acceptance(
    name: str, position: str, address: str, phone: str, mobile: str, email: str, website: str
) -> None:
    """Feature: email-signature-refactor, Property 1: Valid input acceptance.

    Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6, 1.7

    For any SignatureData object with all required fields populated with valid values,
    the SignatureData should be successfully created without raising exceptions.
    """
    # When creating SignatureData with valid required fields
    signature_data = SignatureData(
        name=name,
        position=position,
        address=address,
        phone=phone,
        mobile=mobile,
        email=email,
        website=website,
    )

    # Then the object should be created successfully
    assert signature_data.name == name
    assert signature_data.position == position
    assert signature_data.address == address
    assert signature_data.phone == phone
    assert signature_data.mobile == mobile
    assert signature_data.email == email
    assert signature_data.website == website


@given(value=empty_or_whitespace, field_name=st.text(min_size=1))
def test_required_field_validation(value: str, field_name: str) -> None:
    """Feature: email-signature-refactor, Property 2: Required field validation.

    Validates: Requirements 2.1, 2.2

    For any input string that is empty or contains only whitespace,
    when validating a required field (name or position), the InputValidator
    should return a validation failure with a clear error message.
    """
    # When validating an empty or whitespace-only value
    is_valid, error_message = InputValidator.validate_required_field(value, field_name)

    # Then validation should fail
    assert not is_valid

    # And error message should be clear and contain the field name
    assert error_message
    assert field_name in error_message
    assert "required" in error_message.lower() or "empty" in error_message.lower()


@given(
    email=st.one_of(
        # Strings without @ symbol
        st.text().filter(lambda s: "@" not in s),
        # Strings with @ but no domain part
        st.text(min_size=1).map(lambda s: s.replace("@", "") + "@"),
        # Empty strings
        st.just(""),
    )
)
def test_email_format_validation(email: str) -> None:
    """Feature: email-signature-refactor, Property 3: Email format validation.

    Validates: Requirements 2.3

    For any string that does not contain both an @ symbol and a domain part,
    the InputValidator should reject it as an invalid email address.
    """
    # When validating an invalid email format
    is_valid, error_message = InputValidator.validate_email(email)

    # Then validation should fail
    assert not is_valid

    # And error message should be clear
    assert error_message
    assert "@" in error_message.lower() or "email" in error_message.lower()


@given(
    phone=st.one_of(
        # Too short numbers (non-empty)
        st.text(alphabet=st.characters(whitelist_categories=["Nd"]), min_size=1, max_size=8),
        # Too long numbers
        st.text(alphabet=st.characters(whitelist_categories=["Nd"]), min_size=15),
        # Invalid characters
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1),
        # Invalid format with wrong prefix
        st.just("+999 123 456 789"),
    )
)
def test_phone_number_validation(phone: str) -> None:
    """Feature: email-signature-refactor, Property 4: Phone number validation.

    Validates: Requirements 2.4

    For any phone number string, the InputValidator should accept valid Portuguese
    phone formats and reject invalid formats with appropriate error messages.
    Note: Empty phone numbers are valid (optional field).
    """
    # When validating an invalid phone number (non-empty)
    is_valid, error_message = InputValidator.validate_phone(phone)

    # Then validation should fail
    assert not is_valid

    # And error message should be clear and mention phone format
    assert error_message
    assert "phone" in error_message.lower() or "format" in error_message.lower()


@given(
    validation_type=st.sampled_from(["required", "email", "phone"]),
    field_name=st.text(min_size=1, max_size=20),
)
def test_validation_error_message_clarity(validation_type: str, field_name: str) -> None:
    """Feature: email-signature-refactor, Property 13: Validation error message clarity.

    Validates: Requirements 2.5, 12.5

    For any validation failure, the error message should contain both the field name
    that failed validation and specific guidance on what constitutes valid input
    for that field.
    """
    # Generate invalid input based on validation type
    if validation_type == "required":
        is_valid, error_message = InputValidator.validate_required_field("", field_name)
    elif validation_type == "email":
        is_valid, error_message = InputValidator.validate_email("invalid-email")
    else:  # phone
        is_valid, error_message = InputValidator.validate_phone("abc123")

    # Then validation should fail
    assert not is_valid

    # And error message should be clear and informative
    assert error_message

    # Error message should contain guidance
    if validation_type == "required":
        # Should mention the field name and that it's required
        assert field_name in error_message
        assert "required" in error_message.lower() or "empty" in error_message.lower()
    elif validation_type == "email":
        # Should mention email format requirements
        assert "email" in error_message.lower() or "@" in error_message
        assert "format" in error_message.lower() or "valid" in error_message.lower()
    else:  # phone
        # Should mention phone format requirements
        assert "phone" in error_message.lower()
        assert "format" in error_message.lower() or "digit" in error_message.lower()
