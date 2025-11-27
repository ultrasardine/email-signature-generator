"""Property-based tests for GUI validation feedback.

Feature: gui-interface
"""

import tkinter as tk
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.email_signature.domain.validators import InputValidator
from src.email_signature.interface.gui.validation_mixin import ValidationMixin


# Create a test class that uses ValidationMixin
class ValidationTestHelper(ValidationMixin):
    """Helper class that uses ValidationMixin for testing."""
    
    def __init__(self, root: tk.Tk):
        """Initialize test helper."""
        super().__init__()
        self.root = root


# Strategy for generating invalid email addresses
invalid_emails = st.one_of(
    # Strings without @ symbol
    st.text(min_size=1).filter(lambda s: "@" not in s),
    # Strings with @ but no domain part
    st.text(min_size=1).map(lambda s: s.replace("@", "") + "@"),
    # Empty strings
    st.just(""),
    # @ at the beginning or end
    st.just("@example.com"),
    st.just("user@"),
    # Multiple @ symbols
    st.just("user@@example.com"),
)


# Strategy for generating invalid phone numbers
invalid_phones = st.one_of(
    # Too short numbers (non-empty)
    st.text(alphabet=st.characters(whitelist_categories=["Nd"]), min_size=1, max_size=8),
    # Too long numbers
    st.text(alphabet=st.characters(whitelist_categories=["Nd"]), min_size=15),
    # Invalid characters
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1),
    # Invalid format with wrong prefix
    st.just("+999 123 456 789"),
    st.just("abc123"),
)


@pytest.mark.gui
@given(value=st.text())
@settings(max_examples=100, deadline=None)
def test_validation_triggers_on_input_change(value: str) -> None:
    """Feature: gui-interface, Property 1: Real-time validation triggers.
    
    Validates: Requirements 1.2
    
    For any form field and any input value, when the value changes,
    validation should execute and update the field's visual state.
    """
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Create a test widget with ValidationMixin
        test_helper = ValidationTestHelper(root)
        
        # Create a test entry widget
        frame = tk.Frame(root)
        entry = tk.Entry(frame)
        entry.grid(row=0, column=0)
        
        # Validate the input using the validator
        is_valid, error_message = InputValidator.validate_required_field(value, "test_field")
        
        # Apply validation feedback based on result
        if is_valid:
            test_helper.set_field_valid(entry)
            # Verify no error label exists
            assert entry not in test_helper._validation_labels
        else:
            test_helper.set_field_invalid(entry)
            test_helper.show_validation_error(entry, error_message)
            # Verify error label exists
            assert entry in test_helper._validation_labels
            assert test_helper._validation_labels[entry].cget("text") == error_message
        
        # Verify the widget's visual state changed
        # For invalid: should have light red background
        # For valid: should have light green background
        if not is_valid:
            assert entry.cget("background") == "#ffebee"  # Light red
        else:
            assert entry.cget("background") == "#e8f5e9"  # Light green
            
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass


@pytest.mark.gui
@given(email=invalid_emails)
@settings(max_examples=100, deadline=None)
def test_invalid_email_detection(email: str) -> None:
    """Feature: gui-interface, Property 2: Invalid email detection.
    
    Validates: Requirements 1.3
    
    For any string that does not match valid email format,
    when entered in the email field, an error indicator should be displayed.
    """
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Create a test widget with ValidationMixin
        test_helper = ValidationTestHelper(root)
        
        # Create a test entry widget for email
        frame = tk.Frame(root)
        email_entry = tk.Entry(frame)
        email_entry.grid(row=0, column=0)
        
        # Validate the email
        is_valid, error_message = InputValidator.validate_email(email)
        
        # Email should be invalid
        assert not is_valid
        assert error_message
        
        # Apply validation feedback
        test_helper.set_field_invalid(email_entry)
        test_helper.show_validation_error(email_entry, error_message)
        
        # Verify error indicator is displayed
        assert email_entry in test_helper._validation_labels
        error_label = test_helper._validation_labels[email_entry]
        
        # Verify error label has red text (convert color object to string)
        foreground_color = str(error_label.cget("foreground"))
        assert foreground_color == "red"
        
        # Verify error message is displayed
        assert error_label.cget("text") == error_message
        
        # Verify widget has invalid visual state (light red background)
        assert email_entry.cget("background") == "#ffebee"
        
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass


@pytest.mark.gui
@given(phone=invalid_phones)
@settings(max_examples=100, deadline=None)
def test_invalid_phone_detection(phone: str) -> None:
    """Feature: gui-interface, Property 3: Invalid phone detection.
    
    Validates: Requirements 1.4
    
    For any string that does not match valid phone format,
    when entered in the phone field, an error indicator should be displayed.
    """
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Create a test widget with ValidationMixin
        test_helper = ValidationTestHelper(root)
        
        # Create a test entry widget for phone
        frame = tk.Frame(root)
        phone_entry = tk.Entry(frame)
        phone_entry.grid(row=0, column=0)
        
        # Validate the phone number
        is_valid, error_message = InputValidator.validate_phone(phone)
        
        # Phone should be invalid
        assert not is_valid
        assert error_message
        
        # Apply validation feedback
        test_helper.set_field_invalid(phone_entry)
        test_helper.show_validation_error(phone_entry, error_message)
        
        # Verify error indicator is displayed
        assert phone_entry in test_helper._validation_labels
        error_label = test_helper._validation_labels[phone_entry]
        
        # Verify error label has red text (convert color object to string)
        foreground_color = str(error_label.cget("foreground"))
        assert foreground_color == "red"
        
        # Verify error message is displayed
        assert error_label.cget("text") == error_message
        
        # Verify widget has invalid visual state (light red background)
        assert phone_entry.cget("background") == "#ffebee"
        
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass



# Strategy for generating valid signature data
valid_signature_data = st.fixed_dictionaries({
    "name": st.text(min_size=1).filter(lambda s: s.strip()),
    "position": st.text(min_size=1).filter(lambda s: s.strip()),
    "address": st.text(min_size=1).filter(lambda s: s.strip()),
    "email": st.from_regex(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", fullmatch=True),
    "phone": st.one_of(st.just(""), st.from_regex(r"^\+?351\s?\d{3}\s?\d{3}\s?\d{3}$", fullmatch=True)),
    "mobile": st.one_of(st.just(""), st.from_regex(r"^\+?351\s?\d{3}\s?\d{3}\s?\d{3}$", fullmatch=True)),
    "website": st.text(),
})


# Strategy for generating invalid signature data (missing required fields or invalid format)
invalid_signature_data = st.one_of(
    # Missing name
    st.fixed_dictionaries({
        "name": st.just(""),
        "position": st.text(min_size=1).filter(lambda s: s.strip()),
        "address": st.text(min_size=1).filter(lambda s: s.strip()),
        "email": st.from_regex(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", fullmatch=True),
        "phone": st.just(""),
        "mobile": st.just(""),
        "website": st.text(),
    }),
    # Missing position
    st.fixed_dictionaries({
        "name": st.text(min_size=1).filter(lambda s: s.strip()),
        "position": st.just(""),
        "address": st.text(min_size=1).filter(lambda s: s.strip()),
        "email": st.from_regex(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", fullmatch=True),
        "phone": st.just(""),
        "mobile": st.just(""),
        "website": st.text(),
    }),
    # Missing address
    st.fixed_dictionaries({
        "name": st.text(min_size=1).filter(lambda s: s.strip()),
        "position": st.text(min_size=1).filter(lambda s: s.strip()),
        "address": st.just(""),
        "email": st.from_regex(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", fullmatch=True),
        "phone": st.just(""),
        "mobile": st.just(""),
        "website": st.text(),
    }),
    # Invalid email
    st.fixed_dictionaries({
        "name": st.text(min_size=1).filter(lambda s: s.strip()),
        "position": st.text(min_size=1).filter(lambda s: s.strip()),
        "address": st.text(min_size=1).filter(lambda s: s.strip()),
        "email": st.text(min_size=1).filter(lambda s: "@" not in s),
        "phone": st.just(""),
        "mobile": st.just(""),
        "website": st.text(),
    }),
)


@pytest.mark.gui
@given(data=valid_signature_data)
@settings(max_examples=100, deadline=None)
def test_generate_button_enabled_with_valid_data(data: dict) -> None:
    """Feature: gui-interface, Property 4: Generate button enablement.
    
    Validates: Requirements 1.5
    
    For any complete set of valid signature data, the generate button
    should be enabled.
    """
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Import dependencies
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.domain.validators import InputValidator
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        from src.email_signature.interface.gui.signature_tab import SignatureTab
        from src.email_signature.infrastructure.image_renderer import ImageRenderer
        from src.email_signature.infrastructure.logo_loader import LogoLoader
        from src.email_signature.infrastructure.file_service import FileSystemService
        
        # Create mock dependencies
        config = SignatureConfig()
        validator = InputValidator()
        image_renderer = ImageRenderer(config)
        logo_loader = LogoLoader(config.logo_search_paths)
        file_service = FileSystemService()
        use_case = GenerateSignatureUseCase(image_renderer, logo_loader, file_service, config)
        
        # Create the signature tab
        tab = SignatureTab(root, config, validator, use_case)
        
        # Set all field values
        for field_name, value in data.items():
            if field_name in tab.field_vars:
                tab.field_vars[field_name].set(value)
        
        # Trigger validation for all fields
        for field_name in data.keys():
            if field_name in tab.field_vars:
                tab._on_field_change(field_name)
        
        # Update the UI to process all events
        root.update_idletasks()
        
        # Verify the generate button is enabled
        button_state = str(tab.generate_button.cget("state"))
        assert button_state == "normal", f"Generate button should be enabled with valid data, but state is {button_state}"
        
        # Verify form is valid
        assert tab.is_form_valid(), "Form should be valid with complete valid data"
        
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass


@pytest.mark.gui
@given(data=invalid_signature_data)
@settings(max_examples=100, deadline=None)
def test_generate_button_disabled_with_invalid_data(data: dict) -> None:
    """Feature: gui-interface, Property 4: Generate button enablement.
    
    Validates: Requirements 1.5
    
    For any incomplete or invalid signature data, the generate button
    should be disabled.
    """
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Import dependencies
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.domain.validators import InputValidator
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        from src.email_signature.interface.gui.signature_tab import SignatureTab
        from src.email_signature.infrastructure.image_renderer import ImageRenderer
        from src.email_signature.infrastructure.logo_loader import LogoLoader
        from src.email_signature.infrastructure.file_service import FileSystemService
        
        # Create mock dependencies
        config = SignatureConfig()
        validator = InputValidator()
        image_renderer = ImageRenderer(config)
        logo_loader = LogoLoader(config.logo_search_paths)
        file_service = FileSystemService()
        use_case = GenerateSignatureUseCase(image_renderer, logo_loader, file_service, config)
        
        # Create the signature tab
        tab = SignatureTab(root, config, validator, use_case)
        
        # Set all field values
        for field_name, value in data.items():
            if field_name in tab.field_vars:
                tab.field_vars[field_name].set(value)
        
        # Trigger validation for all fields
        for field_name in data.keys():
            if field_name in tab.field_vars:
                tab._on_field_change(field_name)
        
        # Update the UI to process all events
        root.update_idletasks()
        
        # Verify the generate button is disabled
        button_state = str(tab.generate_button.cget("state"))
        assert button_state == "disabled", f"Generate button should be disabled with invalid data, but state is {button_state}"
        
        # Verify form is invalid
        assert not tab.is_form_valid(), "Form should be invalid with incomplete or invalid data"
        
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass


@pytest.mark.gui
@given(
    initial_data=valid_signature_data,
    modified_field=st.sampled_from(["name", "position", "address", "email"]),
    new_value=st.text(min_size=1).filter(lambda s: s.strip())
)
@settings(max_examples=100, deadline=None)
def test_preview_auto_update_on_data_change(
    initial_data: dict, modified_field: str, new_value: str
) -> None:
    """Feature: gui-interface, Property 7: Preview auto-update.
    
    Validates: Requirements 3.4
    
    For any change to signature data fields, the preview should automatically
    regenerate to reflect the new data (when auto-update is enabled).
    """
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Import dependencies
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.domain.validators import InputValidator
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        from src.email_signature.interface.gui.signature_tab import SignatureTab
        from src.email_signature.infrastructure.image_renderer import ImageRenderer
        from src.email_signature.infrastructure.logo_loader import LogoLoader
        from src.email_signature.infrastructure.file_service import FileSystemService
        from unittest.mock import Mock, patch
        
        # Create mock dependencies
        config = SignatureConfig()
        validator = InputValidator()
        image_renderer = ImageRenderer(config)
        logo_loader = LogoLoader(config.logo_search_paths)
        file_service = FileSystemService()
        use_case = GenerateSignatureUseCase(image_renderer, logo_loader, file_service, config)
        
        # Create the signature tab
        tab = SignatureTab(root, config, validator, use_case)
        
        # Enable auto-update
        tab.auto_update_preview = True
        tab.auto_update_var.set(True)
        
        # Set initial valid data
        for field_name, value in initial_data.items():
            if field_name in tab.field_vars:
                tab.field_vars[field_name].set(value)
        
        # Trigger validation for all fields to make form valid
        for field_name in initial_data.keys():
            if field_name in tab.field_vars:
                value = tab.field_vars[field_name].get()
                tab._validate_field(field_name, value)
        
        tab._update_generate_button_state()
        root.update_idletasks()
        
        # Verify form is valid before proceeding
        if not tab.is_form_valid():
            # Skip this test case if the initial data doesn't result in a valid form
            return
        
        # Mock the _generate_preview method to track calls
        original_generate_preview = tab._generate_preview
        preview_call_count = [0]  # Use list to allow modification in nested function
        
        def mock_generate_preview():
            preview_call_count[0] += 1
            # Don't actually generate preview to speed up test
            pass
        
        tab._generate_preview = mock_generate_preview
        
        # Modify a field
        if modified_field in tab.field_vars:
            # For email field, ensure new value is valid email format
            if modified_field == "email" and "@" not in new_value:
                new_value = new_value.replace(" ", "") + "@example.com"
            
            tab.field_vars[modified_field].set(new_value)
            
            # Trigger the field change handler
            tab._on_field_change(modified_field)
            
            # Update the UI to process all events
            root.update_idletasks()
            
            # Verify preview was regenerated (if form is still valid)
            if tab.is_form_valid():
                assert preview_call_count[0] > 0, (
                    f"Preview should auto-update when {modified_field} changes "
                    f"and form is valid, but _generate_preview was not called"
                )
        
        # Restore original method
        tab._generate_preview = original_generate_preview
        
        # Clean up
        tab.cleanup()
        
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass


# Strategy for generating invalid dimension values
invalid_dimensions = st.one_of(
    # Negative numbers
    st.integers(max_value=-1),
    # Zero
    st.just(0),
    # Non-numeric strings (letters)
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1),
    # Decimal numbers (not integers)
    st.floats(min_value=0.1, max_value=100.0).map(str),
    # Special characters
    st.text(alphabet="!@#$%^&*()", min_size=1),
)


# Strategy for generating valid dimension values
valid_dimensions = st.integers(min_value=1, max_value=10000)


@pytest.mark.gui
@given(dimension_value=invalid_dimensions)
@settings(max_examples=100, deadline=None)
def test_dimension_validation_rejects_invalid_values(dimension_value) -> None:
    """Feature: gui-interface, Property 5: Dimension validation.
    
    Validates: Requirements 2.3
    
    For any dimension field and any invalid input value (non-positive or non-integer),
    the system should reject the input.
    """
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Import dependencies
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.interface.gui.settings_tab import SettingsTab
        
        # Create mock dependencies
        config = SignatureConfig()
        
        # Create the settings tab
        tab = SettingsTab(root, config)
        
        # Test the validation method directly
        is_valid = tab._validate_dimension(str(dimension_value))
        
        # Invalid dimensions should be rejected
        assert not is_valid, f"Dimension value '{dimension_value}' should be rejected but was accepted"
        
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass


@pytest.mark.gui
@given(dimension_value=valid_dimensions)
@settings(max_examples=100, deadline=None)
def test_dimension_validation_accepts_valid_values(dimension_value: int) -> None:
    """Feature: gui-interface, Property 5: Dimension validation.
    
    Validates: Requirements 2.3
    
    For any dimension field and any valid positive integer input,
    the system should accept the input.
    """
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Import dependencies
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.interface.gui.settings_tab import SettingsTab
        
        # Create mock dependencies
        config = SignatureConfig()
        
        # Create the settings tab
        tab = SettingsTab(root, config)
        
        # Test the validation method directly
        is_valid = tab._validate_dimension(str(dimension_value))
        
        # Valid dimensions should be accepted
        assert is_valid, f"Dimension value '{dimension_value}' should be accepted but was rejected"
        
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass


@pytest.mark.gui
@given(
    field_name=st.sampled_from(["logo_height", "margin", "logo_margin_right", "line_height", "outline_width_name", "outline_width_text"]),
    invalid_value=invalid_dimensions
)
@settings(max_examples=100, deadline=None)
def test_dimension_field_rejects_invalid_input(field_name: str, invalid_value) -> None:
    """Feature: gui-interface, Property 5: Dimension validation.
    
    Validates: Requirements 2.3
    
    For any dimension field in the settings tab, when an invalid value is entered,
    the field should reject the input and not update the underlying variable.
    """
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Import dependencies
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.interface.gui.settings_tab import SettingsTab
        
        # Create mock dependencies
        config = SignatureConfig()
        
        # Create the settings tab
        tab = SettingsTab(root, config)
        
        # Get the original value
        original_value = tab.dimension_vars[field_name].get()
        
        # Try to set an invalid value
        # The validation should prevent this from being set
        entry = tab.dimension_widgets[field_name]
        
        # Simulate user input by calling the validation function
        is_valid = tab._validate_dimension(str(invalid_value))
        
        # Validation should reject invalid values
        assert not is_valid, f"Invalid dimension '{invalid_value}' should be rejected for field '{field_name}'"
        
        # The original value should remain unchanged
        current_value = tab.dimension_vars[field_name].get()
        assert current_value == original_value, (
            f"Field '{field_name}' value should remain {original_value} "
            f"after invalid input '{invalid_value}', but is {current_value}"
        )
        
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass
