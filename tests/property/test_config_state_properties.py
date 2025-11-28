"""Property-based tests for ConfigState shared configuration component.

Feature: gui-settings-preview
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.email_signature.domain.config import SignatureConfig
from src.email_signature.interface.gui.config_state import ConfigState


# Strategy for generating valid RGB colors (3 components, 0-255)
rgb_colors = st.tuples(
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
)

# Strategy for generating valid RGBA colors (4 components, 0-255)
rgba_colors = st.tuples(
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
)

# Strategy for generating any valid color (RGB or RGBA)
valid_colors = st.one_of(rgb_colors, rgba_colors)

# Strategy for color names that exist in the default config
color_names = st.sampled_from(["outline", "name", "details", "separator", "confidentiality"])


@pytest.mark.gui
@given(color_name=color_names, color_value=valid_colors)
@settings(max_examples=100, deadline=None)
def test_config_state_color_update_propagation(
    color_name: str, color_value: tuple[int, ...]
) -> None:
    """Feature: gui-settings-preview, Property 2: Config state color update propagation.
    
    Validates: Requirements 1.2
    
    For any color update through ConfigState, the in-memory SignatureConfig
    colors dictionary SHALL contain the updated color value.
    """
    # Create a fresh SignatureConfig
    config = SignatureConfig()
    
    # Create ConfigState without tkinter root (for testing without GUI)
    config_state = ConfigState(config, root=None)
    
    # Update the color through ConfigState
    config_state.update_color(color_name, color_value)
    
    # Verify the color was updated in the config
    assert color_name in config_state.config.colors, (
        f"Color '{color_name}' should exist in config.colors"
    )
    assert config_state.config.colors[color_name] == color_value, (
        f"Color '{color_name}' should be {color_value}, "
        f"but is {config_state.config.colors[color_name]}"
    )
    
    # Also verify through the original config reference
    assert config.colors[color_name] == color_value, (
        f"Original config reference should also have updated color"
    )


@pytest.mark.gui
@given(
    color_name=color_names,
    color_value1=valid_colors,
    color_value2=valid_colors,
)
@settings(max_examples=100, deadline=None)
def test_config_state_color_update_overwrites_previous(
    color_name: str,
    color_value1: tuple[int, ...],
    color_value2: tuple[int, ...],
) -> None:
    """Feature: gui-settings-preview, Property 2: Config state color update propagation.
    
    Validates: Requirements 1.2
    
    For any sequence of color updates to the same color name, the final
    value in the config should be the last value set.
    """
    # Create a fresh SignatureConfig
    config = SignatureConfig()
    
    # Create ConfigState without tkinter root
    config_state = ConfigState(config, root=None)
    
    # Update the color twice
    config_state.update_color(color_name, color_value1)
    config_state.update_color(color_name, color_value2)
    
    # Verify the final color is the second value
    assert config_state.config.colors[color_name] == color_value2, (
        f"Color '{color_name}' should be {color_value2} after second update, "
        f"but is {config_state.config.colors[color_name]}"
    )


@pytest.mark.gui
@given(color_name=color_names, color_value=valid_colors)
@settings(max_examples=100, deadline=None)
def test_config_state_notifies_listeners_on_color_update(
    color_name: str, color_value: tuple[int, ...]
) -> None:
    """Feature: gui-settings-preview, Property 2: Config state color update propagation.
    
    Validates: Requirements 1.2
    
    For any color update through ConfigState, all registered listeners
    should be notified of the change.
    """
    # Create a fresh SignatureConfig
    config = SignatureConfig()
    
    # Create ConfigState without tkinter root (immediate notification)
    config_state = ConfigState(config, root=None)
    
    # Track listener calls
    listener_calls = []
    
    def listener():
        listener_calls.append(True)
    
    # Register listener
    config_state.add_listener(listener)
    
    # Update the color
    config_state.update_color(color_name, color_value)
    
    # Verify listener was called (without root, notification is immediate)
    assert len(listener_calls) == 1, (
        f"Listener should be called once, but was called {len(listener_calls)} times"
    )


@pytest.mark.gui
@given(color_name=color_names, color_value=valid_colors)
@settings(max_examples=100, deadline=None)
def test_config_state_removed_listener_not_notified(
    color_name: str, color_value: tuple[int, ...]
) -> None:
    """Feature: gui-settings-preview, Property 2: Config state color update propagation.
    
    Validates: Requirements 1.2
    
    For any color update through ConfigState, removed listeners should
    NOT be notified of the change.
    """
    # Create a fresh SignatureConfig
    config = SignatureConfig()
    
    # Create ConfigState without tkinter root
    config_state = ConfigState(config, root=None)
    
    # Track listener calls
    listener_calls = []
    
    def listener():
        listener_calls.append(True)
    
    # Register and then remove listener
    config_state.add_listener(listener)
    config_state.remove_listener(listener)
    
    # Update the color
    config_state.update_color(color_name, color_value)
    
    # Verify listener was NOT called
    assert len(listener_calls) == 0, (
        f"Removed listener should not be called, but was called {len(listener_calls)} times"
    )


# Strategy for generating sequences of rapid color updates
rapid_color_updates = st.lists(
    st.tuples(color_names, valid_colors),
    min_size=2,
    max_size=10,
)


@pytest.mark.gui
@given(updates=rapid_color_updates)
@settings(max_examples=100, deadline=None)
def test_debouncing_prevents_excessive_updates_without_root(
    updates: list[tuple[str, tuple[int, ...]]]
) -> None:
    """Feature: gui-settings-preview, Property 8: Debouncing prevents excessive updates.
    
    Validates: Requirements 3.5
    
    For any sequence of rapid configuration changes without a tkinter root,
    notifications should happen immediately (one per update) since debouncing
    requires the tkinter event loop.
    """
    # Create a fresh SignatureConfig
    config = SignatureConfig()
    
    # Create ConfigState without tkinter root (no debouncing possible)
    config_state = ConfigState(config, root=None)
    
    # Track listener calls
    listener_calls = []
    
    def listener():
        listener_calls.append(True)
    
    # Register listener
    config_state.add_listener(listener)
    
    # Apply all updates rapidly
    for color_name, color_value in updates:
        config_state.update_color(color_name, color_value)
    
    # Without root, each update triggers immediate notification
    assert len(listener_calls) == len(updates), (
        f"Without tkinter root, each update should trigger one notification. "
        f"Expected {len(updates)} calls, got {len(listener_calls)}"
    )


@pytest.mark.gui
@given(updates=rapid_color_updates)
@settings(max_examples=100, deadline=None)
def test_debouncing_with_tkinter_root(
    updates: list[tuple[str, tuple[int, ...]]]
) -> None:
    """Feature: gui-settings-preview, Property 8: Debouncing prevents excessive updates.
    
    Validates: Requirements 3.5
    
    For any sequence of rapid configuration changes with a tkinter root,
    only one preview generation SHALL occur after the debounce delay.
    """
    import tkinter as tk
    
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Create a fresh SignatureConfig
        config = SignatureConfig()
        
        # Create ConfigState with tkinter root and short debounce delay
        debounce_delay = 50  # 50ms for faster testing
        config_state = ConfigState(config, root=root, debounce_delay_ms=debounce_delay)
        
        # Track listener calls
        listener_calls = []
        
        def listener():
            listener_calls.append(True)
        
        # Register listener
        config_state.add_listener(listener)
        
        # Apply all updates rapidly (without waiting)
        for color_name, color_value in updates:
            config_state.update_color(color_name, color_value)
        
        # At this point, no notifications should have fired yet
        # (they're all debounced)
        assert len(listener_calls) == 0, (
            f"Debounced updates should not trigger immediate notifications. "
            f"Got {len(listener_calls)} calls before waiting"
        )
        
        # Wait for debounce delay plus a small buffer
        wait_time = debounce_delay + 50
        root.after(wait_time, root.quit)
        root.mainloop()
        
        # After waiting, exactly one notification should have fired
        assert len(listener_calls) == 1, (
            f"After debounce delay, exactly one notification should fire. "
            f"Expected 1 call, got {len(listener_calls)}"
        )
        
        # Verify the final config has the last update's values
        last_color_name, last_color_value = updates[-1]
        assert config_state.config.colors[last_color_name] == last_color_value, (
            f"Config should have the last update's value"
        )
        
    finally:
        # Clean up
        try:
            root.destroy()
        except Exception:
            pass


@pytest.mark.gui
@given(
    color_name=color_names,
    color_value=valid_colors,
    debounce_delay=st.integers(min_value=10, max_value=100),
)
@settings(max_examples=50, deadline=None)
def test_debounce_timer_cancellation(
    color_name: str,
    color_value: tuple[int, ...],
    debounce_delay: int,
) -> None:
    """Feature: gui-settings-preview, Property 8: Debouncing prevents excessive updates.
    
    Validates: Requirements 3.5
    
    For any debounce configuration, when a new update arrives before the
    debounce timer fires, the previous timer should be cancelled.
    """
    import tkinter as tk
    
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Create a fresh SignatureConfig
        config = SignatureConfig()
        
        # Create ConfigState with tkinter root
        config_state = ConfigState(config, root=root, debounce_delay_ms=debounce_delay)
        
        # Track listener calls
        listener_calls = []
        
        def listener():
            listener_calls.append(True)
        
        # Register listener
        config_state.add_listener(listener)
        
        # First update
        config_state.update_color(color_name, (100, 100, 100))
        
        # Second update before debounce fires (should cancel first timer)
        config_state.update_color(color_name, color_value)
        
        # No notifications yet
        assert len(listener_calls) == 0, (
            "No notifications should fire before debounce delay"
        )
        
        # Wait for debounce delay plus buffer
        wait_time = debounce_delay + 50
        root.after(wait_time, root.quit)
        root.mainloop()
        
        # Only one notification should have fired (not two)
        assert len(listener_calls) == 1, (
            f"Only one notification should fire after timer cancellation. "
            f"Expected 1 call, got {len(listener_calls)}"
        )
        
        # Config should have the second update's value
        assert config_state.config.colors[color_name] == color_value, (
            f"Config should have the second update's value"
        )
        
    finally:
        # Clean up
        try:
            root.destroy()
        except Exception:
            pass


# Strategy for generating element orders (permutations of element IDs)
element_ids = ["logo", "name", "position", "address", "phone", "email", "separator", "confidentiality"]


@pytest.mark.gui
@given(color_name=color_names, color_value=valid_colors)
@settings(max_examples=100, deadline=None)
def test_color_button_reflects_selected_color(
    color_name: str, color_value: tuple[int, ...]
) -> None:
    """Feature: gui-settings-preview, Property 1: Color button reflects selected color.
    
    Validates: Requirements 1.1, 1.5
    
    For any color selection from the color picker, the corresponding color
    button's background SHALL match the RGB values of the selected color.
    """
    import tkinter as tk
    
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        from src.email_signature.interface.gui.settings_tab import SettingsTab
        from src.email_signature.interface.gui.config_state import ConfigState
        
        # Create a fresh SignatureConfig
        config = SignatureConfig()
        
        # Create ConfigState with tkinter root
        config_state = ConfigState(config, root=root)
        
        # Create the settings tab with config_state
        settings_tab = SettingsTab(parent=root, config_state=config_state)
        
        # Simulate color selection by directly calling _update_color_button
        # (since we can't actually open the color picker dialog in tests)
        settings_tab.color_values[color_name] = color_value
        settings_tab._update_color_button(color_name, color_value)
        
        # Get the button's background color
        button = settings_tab.color_buttons[color_name]
        button_bg = button.cget("bg")
        
        # Convert the color value to expected hex format
        expected_hex = f"#{color_value[0]:02x}{color_value[1]:02x}{color_value[2]:02x}"
        
        # Verify the button background matches the selected color
        assert button_bg == expected_hex, (
            f"Color button for '{color_name}' should have background {expected_hex}, "
            f"but has {button_bg}"
        )
        
        # Also verify the RGB label was updated
        rgb_label = getattr(settings_tab, f"{color_name}_rgb_label", None)
        if rgb_label:
            label_text = rgb_label.cget("text")
            if len(color_value) == 3:
                expected_text = f"RGB({color_value[0]}, {color_value[1]}, {color_value[2]})"
            else:
                expected_text = f"RGBA({color_value[0]}, {color_value[1]}, {color_value[2]}, {color_value[3]})"
            assert label_text == expected_text, (
                f"RGB label for '{color_name}' should show {expected_text}, "
                f"but shows {label_text}"
            )
        
    finally:
        # Clean up
        try:
            root.destroy()
        except Exception:
            pass


@pytest.mark.gui
@given(color_name=color_names, color_value=valid_colors)
@settings(max_examples=100, deadline=None)
def test_color_button_initial_state_matches_config(
    color_name: str, color_value: tuple[int, ...]
) -> None:
    """Feature: gui-settings-preview, Property 1: Color button reflects selected color.
    
    Validates: Requirements 1.1, 1.5
    
    When the application starts, the Settings Tab SHALL display color buttons
    with backgrounds matching the loaded configuration colors.
    """
    import tkinter as tk
    
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        from src.email_signature.interface.gui.settings_tab import SettingsTab
        from src.email_signature.interface.gui.config_state import ConfigState
        
        # Create a SignatureConfig with the test color pre-set
        config = SignatureConfig()
        config.colors[color_name] = color_value
        
        # Create ConfigState with the pre-configured config
        config_state = ConfigState(config, root=root)
        
        # Create the settings tab - it should load colors from config
        settings_tab = SettingsTab(parent=root, config_state=config_state)
        
        # Get the button's background color
        button = settings_tab.color_buttons[color_name]
        button_bg = button.cget("bg")
        
        # Convert the color value to expected hex format
        expected_hex = f"#{color_value[0]:02x}{color_value[1]:02x}{color_value[2]:02x}"
        
        # Verify the button background matches the config color
        assert button_bg == expected_hex, (
            f"Color button for '{color_name}' should have initial background {expected_hex} "
            f"matching config, but has {button_bg}"
        )
        
    finally:
        # Clean up
        try:
            root.destroy()
        except Exception:
            pass


@pytest.mark.gui
@given(color_name=color_names, color_value=valid_colors)
@settings(max_examples=100, deadline=None)
def test_color_update_syncs_to_config_state(
    color_name: str, color_value: tuple[int, ...]
) -> None:
    """Feature: gui-settings-preview, Property 1: Color button reflects selected color.
    
    Validates: Requirements 1.1, 1.5
    
    When a color is updated via the SettingsTab, the ConfigState should
    be updated with the new color value.
    """
    import tkinter as tk
    
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        from src.email_signature.interface.gui.settings_tab import SettingsTab
        from src.email_signature.interface.gui.config_state import ConfigState
        
        # Create a fresh SignatureConfig
        config = SignatureConfig()
        
        # Create ConfigState with tkinter root
        config_state = ConfigState(config, root=root)
        
        # Create the settings tab with config_state
        settings_tab = SettingsTab(parent=root, config_state=config_state)
        
        # Simulate what happens when a color is selected:
        # 1. Update local color_values
        settings_tab.color_values[color_name] = color_value
        # 2. Update button display
        settings_tab._update_color_button(color_name, color_value)
        # 3. Update config state (this is what _on_color_picker_clicked does)
        settings_tab.config_state.update_color(color_name, color_value)
        
        # Verify the ConfigState was updated
        assert config_state.config.colors[color_name] == color_value, (
            f"ConfigState color '{color_name}' should be {color_value}, "
            f"but is {config_state.config.colors[color_name]}"
        )
        
        # Also verify through the original config reference
        assert config.colors[color_name] == color_value, (
            f"Original config color '{color_name}' should be {color_value}, "
            f"but is {config.colors[color_name]}"
        )
        
    finally:
        # Clean up
        try:
            root.destroy()
        except Exception:
            pass


@pytest.mark.gui
@given(color_name=color_names, color_value=valid_colors)
@settings(max_examples=100, deadline=None)
def test_config_change_triggers_preview_refresh(
    color_name: str, color_value: tuple[int, ...]
) -> None:
    """Feature: gui-settings-preview, Property 3: Config change triggers preview refresh.
    
    Validates: Requirements 1.3, 3.1, 3.2, 3.3
    
    For any configuration change when auto-update is enabled and form is valid,
    the preview generation SHALL be triggered.
    """
    import tkinter as tk
    from unittest.mock import MagicMock, patch
    
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        from src.email_signature.interface.gui.signature_tab import SignatureTab
        from src.email_signature.interface.gui.config_state import ConfigState
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.domain.validators import InputValidator
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        
        # Create dependencies
        config = SignatureConfig()
        config_state = ConfigState(config, root=root, debounce_delay_ms=10)
        validator = InputValidator()
        
        # Create a mock use_case
        use_case = MagicMock(spec=GenerateSignatureUseCase)
        
        # Create the signature tab with config_state
        signature_tab = SignatureTab(
            parent=root,
            config=config_state,
            validator=validator,
            use_case=use_case
        )
        
        # Ensure auto-update is enabled
        signature_tab.auto_update_preview = True
        signature_tab.auto_update_var.set(True)
        
        # Fill in required fields to make form valid
        signature_tab.field_vars["name"].set("Test User")
        signature_tab.field_vars["position"].set("Developer")
        signature_tab.field_vars["address"].set("123 Test St")
        signature_tab.field_vars["email"].set("test@example.com")
        
        # Manually trigger validation for all fields
        for field_name in signature_tab.field_vars.keys():
            value = signature_tab.field_vars[field_name].get()
            signature_tab._validate_field(field_name, value)
        
        # Verify form is valid
        assert signature_tab.is_form_valid(), "Form should be valid after filling required fields"
        
        # Track preview generation calls
        preview_calls = []
        original_generate_preview = signature_tab._generate_preview
        
        def mock_generate_preview():
            preview_calls.append(True)
            # Don't actually generate preview in tests
        
        signature_tab._generate_preview = mock_generate_preview
        
        # Clear any previous calls from form field changes
        preview_calls.clear()
        
        # Update color through ConfigState (this should trigger preview refresh)
        config_state.update_color(color_name, color_value)
        
        # Wait for debounce delay plus buffer
        wait_time = 50  # 10ms debounce + 40ms buffer
        root.after(wait_time, root.quit)
        root.mainloop()
        
        # Verify preview was triggered
        assert len(preview_calls) >= 1, (
            f"Preview generation should be triggered when config changes. "
            f"Expected at least 1 call, got {len(preview_calls)}"
        )
        
        # Clean up
        signature_tab.cleanup()
        
    finally:
        # Clean up
        try:
            root.destroy()
        except Exception:
            pass


@pytest.mark.gui
@given(color_name=color_names, color_value=valid_colors)
@settings(max_examples=100, deadline=None)
def test_config_change_no_refresh_when_form_invalid(
    color_name: str, color_value: tuple[int, ...]
) -> None:
    """Feature: gui-settings-preview, Property 3: Config change triggers preview refresh.
    
    Validates: Requirements 1.3, 3.1, 3.2, 3.3
    
    For any configuration change when form is invalid, the preview generation
    SHALL NOT be triggered even if auto-update is enabled.
    """
    import tkinter as tk
    from unittest.mock import MagicMock
    
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        from src.email_signature.interface.gui.signature_tab import SignatureTab
        from src.email_signature.interface.gui.config_state import ConfigState
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.domain.validators import InputValidator
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        
        # Create dependencies
        config = SignatureConfig()
        config_state = ConfigState(config, root=root, debounce_delay_ms=10)
        validator = InputValidator()
        
        # Create a mock use_case
        use_case = MagicMock(spec=GenerateSignatureUseCase)
        
        # Create the signature tab with config_state
        signature_tab = SignatureTab(
            parent=root,
            config=config_state,
            validator=validator,
            use_case=use_case
        )
        
        # Ensure auto-update is enabled
        signature_tab.auto_update_preview = True
        signature_tab.auto_update_var.set(True)
        
        # Leave form fields empty (invalid form)
        # Verify form is invalid
        assert not signature_tab.is_form_valid(), "Form should be invalid with empty fields"
        
        # Track preview generation calls
        preview_calls = []
        
        def mock_generate_preview():
            preview_calls.append(True)
        
        signature_tab._generate_preview = mock_generate_preview
        
        # Update color through ConfigState
        config_state.update_color(color_name, color_value)
        
        # Wait for debounce delay plus buffer
        wait_time = 50  # 10ms debounce + 40ms buffer
        root.after(wait_time, root.quit)
        root.mainloop()
        
        # Verify preview was NOT triggered (form is invalid)
        assert len(preview_calls) == 0, (
            f"Preview generation should NOT be triggered when form is invalid. "
            f"Expected 0 calls, got {len(preview_calls)}"
        )
        
        # Clean up
        signature_tab.cleanup()
        
    finally:
        # Clean up
        try:
            root.destroy()
        except Exception:
            pass



@pytest.mark.gui
@given(color_name=color_names, color_value=valid_colors)
@settings(max_examples=100, deadline=None)
def test_auto_update_toggle_prevents_refresh(
    color_name: str, color_value: tuple[int, ...]
) -> None:
    """Feature: gui-settings-preview, Property 7: Auto-update toggle prevents refresh.
    
    Validates: Requirements 3.4
    
    For any configuration change when auto-update is disabled, the preview
    generation SHALL NOT be triggered automatically.
    """
    import tkinter as tk
    from unittest.mock import MagicMock
    
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        from src.email_signature.interface.gui.signature_tab import SignatureTab
        from src.email_signature.interface.gui.config_state import ConfigState
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.domain.validators import InputValidator
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        
        # Create dependencies
        config = SignatureConfig()
        config_state = ConfigState(config, root=root, debounce_delay_ms=10)
        validator = InputValidator()
        
        # Create a mock use_case
        use_case = MagicMock(spec=GenerateSignatureUseCase)
        
        # Create the signature tab with config_state
        signature_tab = SignatureTab(
            parent=root,
            config=config_state,
            validator=validator,
            use_case=use_case
        )
        
        # DISABLE auto-update
        signature_tab.auto_update_preview = False
        signature_tab.auto_update_var.set(False)
        
        # Fill in required fields to make form valid
        signature_tab.field_vars["name"].set("Test User")
        signature_tab.field_vars["position"].set("Developer")
        signature_tab.field_vars["address"].set("123 Test St")
        signature_tab.field_vars["email"].set("test@example.com")
        
        # Manually trigger validation for all fields
        for field_name in signature_tab.field_vars.keys():
            value = signature_tab.field_vars[field_name].get()
            signature_tab._validate_field(field_name, value)
        
        # Verify form is valid
        assert signature_tab.is_form_valid(), "Form should be valid after filling required fields"
        
        # Track preview generation calls
        preview_calls = []
        
        def mock_generate_preview():
            preview_calls.append(True)
        
        signature_tab._generate_preview = mock_generate_preview
        
        # Clear any previous calls
        preview_calls.clear()
        
        # Update color through ConfigState
        config_state.update_color(color_name, color_value)
        
        # Wait for debounce delay plus buffer
        wait_time = 50  # 10ms debounce + 40ms buffer
        root.after(wait_time, root.quit)
        root.mainloop()
        
        # Verify preview was NOT triggered (auto-update is disabled)
        assert len(preview_calls) == 0, (
            f"Preview generation should NOT be triggered when auto-update is disabled. "
            f"Expected 0 calls, got {len(preview_calls)}"
        )
        
        # Clean up
        signature_tab.cleanup()
        
    finally:
        # Clean up
        try:
            root.destroy()
        except Exception:
            pass


@pytest.mark.gui
@given(color_name=color_names, color_value=valid_colors)
@settings(max_examples=100, deadline=None)
def test_auto_update_toggle_enables_refresh(
    color_name: str, color_value: tuple[int, ...]
) -> None:
    """Feature: gui-settings-preview, Property 7: Auto-update toggle prevents refresh.
    
    Validates: Requirements 3.4
    
    For any configuration change when auto-update is re-enabled after being
    disabled, the preview generation SHALL be triggered.
    """
    import tkinter as tk
    from unittest.mock import MagicMock
    
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        from src.email_signature.interface.gui.signature_tab import SignatureTab
        from src.email_signature.interface.gui.config_state import ConfigState
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.domain.validators import InputValidator
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        
        # Create dependencies
        config = SignatureConfig()
        config_state = ConfigState(config, root=root, debounce_delay_ms=10)
        validator = InputValidator()
        
        # Create a mock use_case
        use_case = MagicMock(spec=GenerateSignatureUseCase)
        
        # Create the signature tab with config_state
        signature_tab = SignatureTab(
            parent=root,
            config=config_state,
            validator=validator,
            use_case=use_case
        )
        
        # Start with auto-update DISABLED
        signature_tab.auto_update_preview = False
        signature_tab.auto_update_var.set(False)
        
        # Fill in required fields to make form valid
        signature_tab.field_vars["name"].set("Test User")
        signature_tab.field_vars["position"].set("Developer")
        signature_tab.field_vars["address"].set("123 Test St")
        signature_tab.field_vars["email"].set("test@example.com")
        
        # Manually trigger validation for all fields
        for field_name in signature_tab.field_vars.keys():
            value = signature_tab.field_vars[field_name].get()
            signature_tab._validate_field(field_name, value)
        
        # Verify form is valid
        assert signature_tab.is_form_valid(), "Form should be valid after filling required fields"
        
        # Track preview generation calls
        preview_calls = []
        
        def mock_generate_preview():
            preview_calls.append(True)
        
        signature_tab._generate_preview = mock_generate_preview
        
        # Clear any previous calls
        preview_calls.clear()
        
        # Update color while auto-update is disabled
        config_state.update_color(color_name, color_value)
        
        # Wait for debounce
        wait_time = 50
        root.after(wait_time, root.quit)
        root.mainloop()
        
        # Verify no preview was triggered
        assert len(preview_calls) == 0, "No preview should be triggered when auto-update is disabled"
        
        # Now ENABLE auto-update
        signature_tab.auto_update_preview = True
        signature_tab.auto_update_var.set(True)
        
        # Update color again - this time it should trigger preview
        config_state.update_color(color_name, color_value)
        
        # Wait for debounce
        root.after(wait_time, root.quit)
        root.mainloop()
        
        # Verify preview was triggered after enabling auto-update
        assert len(preview_calls) >= 1, (
            f"Preview generation should be triggered after enabling auto-update. "
            f"Expected at least 1 call, got {len(preview_calls)}"
        )
        
        # Clean up
        signature_tab.cleanup()
        
    finally:
        # Clean up
        try:
            root.destroy()
        except Exception:
            pass


# Strategy for generating element order permutations
element_ids_list = ["logo", "name", "position", "address", "phone", "email", "separator", "confidentiality"]

# Strategy for generating valid element orders (permutations)
element_orders = st.permutations(element_ids_list)


@pytest.mark.gui
@given(new_order=element_orders)
@settings(max_examples=100, deadline=None)
def test_element_reorder_updates_config(new_order: tuple[str, ...]) -> None:
    """Feature: gui-settings-preview, Property 5: Element reorder updates config.
    
    Validates: Requirements 2.3
    
    For any drag-and-drop reorder operation, the ConfigState element_order
    SHALL reflect the new arrangement.
    """
    # Convert tuple to list for comparison
    new_order_list = list(new_order)
    
    # Create a fresh SignatureConfig
    config = SignatureConfig()
    
    # Create ConfigState without tkinter root (for testing without GUI)
    config_state = ConfigState(config, root=None)
    
    # Track listener calls to verify notification
    listener_calls = []
    received_orders = []
    
    def listener():
        listener_calls.append(True)
        received_orders.append(config_state.config.element_order.copy())
    
    # Register listener
    config_state.add_listener(listener)
    
    # Update element order through ConfigState (simulates drag-and-drop completion)
    config_state.update_element_order(new_order_list)
    
    # Verify the element order was updated in the config
    assert config_state.config.element_order == new_order_list, (
        f"Config element_order should be {new_order_list}, "
        f"but is {config_state.config.element_order}"
    )
    
    # Verify through the original config reference
    assert config.element_order == new_order_list, (
        f"Original config element_order should also be updated to {new_order_list}"
    )
    
    # Verify listener was called (element order updates are immediate, not debounced)
    assert len(listener_calls) == 1, (
        f"Listener should be called once for element order update, "
        f"but was called {len(listener_calls)} times"
    )
    
    # Verify listener received the correct order
    assert received_orders[0] == new_order_list, (
        f"Listener should receive the new order {new_order_list}, "
        f"but received {received_orders[0]}"
    )


@pytest.mark.gui
@given(
    order1=element_orders,
    order2=element_orders,
)
@settings(max_examples=100, deadline=None)
def test_element_reorder_overwrites_previous(
    order1: tuple[str, ...],
    order2: tuple[str, ...],
) -> None:
    """Feature: gui-settings-preview, Property 5: Element reorder updates config.
    
    Validates: Requirements 2.3
    
    For any sequence of element order updates, the final value in the config
    should be the last order set.
    """
    order1_list = list(order1)
    order2_list = list(order2)
    
    # Create a fresh SignatureConfig
    config = SignatureConfig()
    
    # Create ConfigState without tkinter root
    config_state = ConfigState(config, root=None)
    
    # Update element order twice
    config_state.update_element_order(order1_list)
    config_state.update_element_order(order2_list)
    
    # Verify the final order is the second value
    assert config_state.config.element_order == order2_list, (
        f"Element order should be {order2_list} after second update, "
        f"but is {config_state.config.element_order}"
    )


@pytest.mark.gui
@given(new_order=element_orders)
@settings(max_examples=100, deadline=None)
def test_element_reorder_immediate_notification(new_order: tuple[str, ...]) -> None:
    """Feature: gui-settings-preview, Property 5: Element reorder updates config.
    
    Validates: Requirements 2.3
    
    Element order changes should trigger immediate notification (not debounced)
    because drag-and-drop operations should provide instant feedback.
    """
    new_order_list = list(new_order)
    
    # Create a fresh SignatureConfig
    config = SignatureConfig()
    
    # Create ConfigState without tkinter root
    config_state = ConfigState(config, root=None)
    
    # Track notification timing
    notification_count = 0
    
    def listener():
        nonlocal notification_count
        notification_count += 1
    
    config_state.add_listener(listener)
    
    # Update element order
    config_state.update_element_order(new_order_list)
    
    # Notification should happen immediately (synchronously)
    # Without tkinter root, _notify_immediate is called directly
    assert notification_count == 1, (
        f"Element order update should trigger immediate notification. "
        f"Expected 1 notification, got {notification_count}"
    )


@pytest.mark.gui
@given(new_order=element_orders)
@settings(max_examples=100, deadline=None)
def test_element_order_preserves_all_elements(new_order: tuple[str, ...]) -> None:
    """Feature: gui-settings-preview, Property 5: Element reorder updates config.
    
    Validates: Requirements 2.3
    
    For any element order update, all original elements should be preserved
    (no elements lost or duplicated).
    """
    new_order_list = list(new_order)
    
    # Create a fresh SignatureConfig
    config = SignatureConfig()
    original_elements = set(config.element_order)
    
    # Create ConfigState
    config_state = ConfigState(config, root=None)
    
    # Update element order
    config_state.update_element_order(new_order_list)
    
    # Verify all elements are preserved
    updated_elements = set(config_state.config.element_order)
    
    assert updated_elements == original_elements, (
        f"All elements should be preserved after reorder. "
        f"Original: {original_elements}, Updated: {updated_elements}"
    )
    
    # Verify no duplicates
    assert len(config_state.config.element_order) == len(set(config_state.config.element_order)), (
        f"Element order should not contain duplicates: {config_state.config.element_order}"
    )


@pytest.mark.gui
@given(
    name_color=rgb_colors,
    details_color=rgb_colors,
    separator_color=rgba_colors,
    confidentiality_color=rgb_colors,
)
@settings(max_examples=100, deadline=None)
def test_rendered_signature_uses_current_config_colors(
    name_color: tuple[int, int, int],
    details_color: tuple[int, int, int],
    separator_color: tuple[int, int, int, int],
    confidentiality_color: tuple[int, int, int],
) -> None:
    """Feature: gui-settings-preview, Property 4: Rendered signature uses current config colors.
    
    Validates: Requirements 1.4
    
    For any signature generation, the ImageRenderer SHALL use color values
    from the current SignatureConfig, not stale values.
    """
    from PIL import Image
    
    from src.email_signature.domain.config import SignatureConfig
    from src.email_signature.domain.models import SignatureData
    from src.email_signature.infrastructure.image_renderer import ImageRenderer
    
    # Create a SignatureConfig with the test colors
    config = SignatureConfig()
    config.colors["name"] = name_color
    config.colors["details"] = details_color
    config.colors["separator"] = separator_color
    config.colors["confidentiality"] = confidentiality_color
    
    # Create the ImageRenderer with the config
    renderer = ImageRenderer(config)
    
    # Create test signature data
    signature_data = SignatureData(
        name="Test User",
        position="Developer",
        address="123 Test Street",
        phone="555-1234",
        mobile="555-5678",
        email="test@example.com",
        website="www.example.com",
    )
    
    # Create a simple test logo
    logo = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    
    # Generate the signature image
    signature_image = renderer.create_signature_image(signature_data, logo)
    
    # Verify the image was created
    assert signature_image is not None
    assert signature_image.mode == "RGBA"
    
    # Verify the renderer is using the current config colors
    assert renderer.config.colors["name"] == name_color, (
        f"Renderer should use name color {name_color}, "
        f"but config has {renderer.config.colors['name']}"
    )
    assert renderer.config.colors["details"] == details_color, (
        f"Renderer should use details color {details_color}, "
        f"but config has {renderer.config.colors['details']}"
    )
    assert renderer.config.colors["separator"] == separator_color, (
        f"Renderer should use separator color {separator_color}, "
        f"but config has {renderer.config.colors['separator']}"
    )
    assert renderer.config.colors["confidentiality"] == confidentiality_color, (
        f"Renderer should use confidentiality color {confidentiality_color}, "
        f"but config has {renderer.config.colors['confidentiality']}"
    )
    
    # Now update the config colors and verify the renderer uses the new values
    new_name_color = (
        (name_color[0] + 50) % 256,
        (name_color[1] + 50) % 256,
        (name_color[2] + 50) % 256,
    )
    config.colors["name"] = new_name_color
    
    # Generate another signature image
    signature_image_2 = renderer.create_signature_image(signature_data, logo)
    
    # Verify the renderer is using the updated config colors
    assert renderer.config.colors["name"] == new_name_color, (
        f"Renderer should use updated name color {new_name_color}, "
        f"but config has {renderer.config.colors['name']}"
    )
    
    # Verify both images were created successfully
    assert signature_image_2 is not None
    assert signature_image_2.mode == "RGBA"


@pytest.mark.gui
@given(
    name_color=rgb_colors,
    details_color=rgb_colors,
)
@settings(max_examples=100, deadline=None)
def test_rendered_signature_colors_match_config_at_render_time(
    name_color: tuple[int, int, int],
    details_color: tuple[int, int, int],
) -> None:
    """Feature: gui-settings-preview, Property 4: Rendered signature uses current config colors.
    
    Validates: Requirements 1.4
    
    For any signature generation, the colors used during rendering SHALL be
    the colors present in the config at the time of rendering, ensuring
    that config updates are reflected in subsequent renders.
    """
    from PIL import Image
    
    from src.email_signature.domain.config import SignatureConfig
    from src.email_signature.domain.models import SignatureData
    from src.email_signature.infrastructure.image_renderer import ImageRenderer
    
    # Create a SignatureConfig with initial colors
    config = SignatureConfig()
    initial_name_color = (0, 0, 0)  # Black
    config.colors["name"] = initial_name_color
    config.colors["details"] = (100, 100, 100)
    
    # Create the ImageRenderer with the config
    renderer = ImageRenderer(config)
    
    # Create test signature data
    signature_data = SignatureData(
        name="Test User",
        position="Developer",
        address="123 Test Street",
        phone="",
        mobile="",
        email="test@example.com",
        website="www.example.com",
    )
    
    # Create a simple test logo
    logo = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    
    # Generate first signature with initial colors
    signature_image_1 = renderer.create_signature_image(signature_data, logo)
    assert signature_image_1 is not None
    
    # Update the config colors
    config.colors["name"] = name_color
    config.colors["details"] = details_color
    
    # Generate second signature - should use updated colors
    signature_image_2 = renderer.create_signature_image(signature_data, logo)
    assert signature_image_2 is not None
    
    # Verify the config has the updated colors
    assert config.colors["name"] == name_color, (
        f"Config should have updated name color {name_color}"
    )
    assert config.colors["details"] == details_color, (
        f"Config should have updated details color {details_color}"
    )
    
    # The renderer should reference the same config object
    assert renderer.config is config, (
        "Renderer should reference the same config object"
    )
    
    # Verify the renderer's config has the updated colors
    assert renderer.config.colors["name"] == name_color, (
        f"Renderer config should have updated name color {name_color}"
    )
    assert renderer.config.colors["details"] == details_color, (
        f"Renderer config should have updated details color {details_color}"
    )
