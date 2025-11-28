"""Integration tests for theme application to GUI components.

These tests verify that the ThemeManager successfully applies the design system
to a real Tkinter application and that all GUI components render correctly with
the new styling.

Requirements: 1.2, 1.4
"""

import pytest
import tkinter as tk
from tkinter import ttk


@pytest.fixture
def tk_root():
    """Create a Tkinter root window for testing."""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window during tests
        yield root
        root.destroy()
    except tk.TclError:
        pytest.skip("Tkinter not available in test environment")


class TestThemeManagerIntegration:
    """Integration tests for ThemeManager application to real Tkinter widgets.
    
    Requirements: 1.2, 1.4
    """
    
    def test_theme_manager_applies_successfully_to_real_application(self, tk_root):
        """Test ThemeManager applies successfully to real Tkinter application.
        
        This test verifies that the ThemeManager can be initialized and applied
        to a real Tkinter application without errors.
        
        Requirements: 1.2
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        from src.email_signature.interface.gui.design_system import DesignSystem
        
        # Initialize ThemeManager
        theme_manager = ThemeManager(tk_root)
        
        # Verify theme manager is properly initialized
        assert theme_manager is not None
        assert theme_manager.root is tk_root
        assert theme_manager.style is not None
        
        # Verify the theme is set to 'clam'
        assert theme_manager.style.theme_use() == 'clam'
        
        # Create some widgets to verify styling is applied
        frame = ttk.Frame(tk_root)
        label = ttk.Label(frame, text="Test Label")
        button = ttk.Button(frame, text="Test Button")
        entry = ttk.Entry(frame)
        
        # Pack widgets
        frame.pack()
        label.pack()
        button.pack()
        entry.pack()
        
        # Update to ensure widgets are rendered
        tk_root.update_idletasks()
        
        # Verify widgets were created successfully
        assert frame.winfo_exists()
        assert label.winfo_exists()
        assert button.winfo_exists()
        assert entry.winfo_exists()
    
    def test_all_widget_styles_are_accessible(self, tk_root):
        """Test that all configured widget styles are accessible.
        
        Requirements: 1.2
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        
        theme_manager = ThemeManager(tk_root)
        style = theme_manager.style
        
        # List of all styles that should be configured
        required_styles = [
            'TFrame',
            'TLabel',
            'Heading.TLabel',
            'Secondary.TLabel',
            'TEntry',
            'Error.TEntry',
            'Success.TEntry',
            'TButton',
            'Primary.TButton',
            'TLabelframe',
            'TLabelframe.Label',
            'TNotebook',
            'TNotebook.Tab',
            'TCheckbutton',
            'TSeparator'
        ]
        
        # Verify each style can be accessed
        for style_name in required_styles:
            config = style.configure(style_name)
            assert config is not None, f"Style {style_name} not accessible"
    
    def test_primary_button_style_is_visually_distinct(self, tk_root):
        """Test that Primary.TButton style is visually distinct from TButton.
        
        Requirements: 1.4
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        from src.email_signature.interface.gui.design_system import DesignSystem
        
        theme_manager = ThemeManager(tk_root)
        style = theme_manager.style
        
        # Get configurations for both button styles
        primary_config = style.configure('Primary.TButton')
        default_config = style.configure('TButton')
        
        # Verify they have different backgrounds
        assert primary_config.get('background') != default_config.get('background'), \
            "Primary and default buttons should have different backgrounds"
        
        # Verify primary button uses primary color
        assert primary_config.get('background') == DesignSystem.colors.primary
        
        # Verify primary button has bold font
        primary_font = primary_config.get('font')
        assert 'bold' in str(primary_font).lower() or primary_font[2] == 'bold'
    
    def test_validation_state_styles_exist(self, tk_root):
        """Test that validation state styles (Error, Success) exist and are distinct.
        
        Requirements: 1.4
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        from src.email_signature.interface.gui.design_system import DesignSystem
        
        theme_manager = ThemeManager(tk_root)
        style = theme_manager.style
        
        # Get configurations for validation states
        error_config = style.configure('Error.TEntry')
        success_config = style.configure('Success.TEntry')
        normal_config = style.configure('TEntry')
        
        # Verify error state uses error colors
        assert error_config.get('fieldbackground') == DesignSystem.colors.error_light
        assert error_config.get('bordercolor') == DesignSystem.colors.error
        
        # Verify success state uses success colors
        assert success_config.get('fieldbackground') == DesignSystem.colors.success_light
        assert success_config.get('bordercolor') == DesignSystem.colors.success
        
        # Verify they're different from normal state
        assert error_config.get('fieldbackground') != normal_config.get('fieldbackground')
        assert success_config.get('fieldbackground') != normal_config.get('fieldbackground')


class TestGUIComponentRendering:
    """Integration tests for GUI component rendering with design system.
    
    Requirements: 1.2, 1.4
    """
    
    def test_notebook_tabs_render_correctly(self, tk_root):
        """Test that notebook tabs render correctly with new styling.
        
        Requirements: 1.2
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        
        theme_manager = ThemeManager(tk_root)
        
        # Create a notebook with multiple tabs
        notebook = ttk.Notebook(tk_root)
        
        # Create tab frames
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        
        # Add tabs
        notebook.add(tab1, text="Tab 1")
        notebook.add(tab2, text="Tab 2")
        
        # Pack notebook
        notebook.pack(fill='both', expand=True)
        
        # Update to ensure rendering
        tk_root.update_idletasks()
        
        # Verify notebook exists and has tabs
        assert notebook.winfo_exists()
        assert len(notebook.tabs()) == 2
    
    def test_labelframe_renders_with_styled_label(self, tk_root):
        """Test that LabelFrame renders correctly with styled label.
        
        Requirements: 1.2
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        
        theme_manager = ThemeManager(tk_root)
        
        # Create a LabelFrame
        labelframe = ttk.LabelFrame(tk_root, text="Test Section")
        labelframe.pack(fill='both', expand=True)
        
        # Add some content
        label = ttk.Label(labelframe, text="Content")
        label.pack()
        
        # Update to ensure rendering
        tk_root.update_idletasks()
        
        # Verify labelframe exists
        assert labelframe.winfo_exists()
        assert label.winfo_exists()
    
    def test_form_elements_render_correctly(self, tk_root):
        """Test that form elements (labels, entries, buttons) render correctly.
        
        Requirements: 1.2
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        
        theme_manager = ThemeManager(tk_root)
        
        # Create a form-like structure
        frame = ttk.Frame(tk_root)
        frame.pack(fill='both', expand=True)
        
        # Add form elements
        label = ttk.Label(frame, text="Name:")
        label.grid(row=0, column=0, sticky='w')
        
        entry = ttk.Entry(frame)
        entry.grid(row=0, column=1, sticky='ew')
        
        button = ttk.Button(frame, text="Submit", style='Primary.TButton')
        button.grid(row=1, column=0, columnspan=2)
        
        # Update to ensure rendering
        tk_root.update_idletasks()
        
        # Verify all elements exist
        assert frame.winfo_exists()
        assert label.winfo_exists()
        assert entry.winfo_exists()
        assert button.winfo_exists()


class TestInteractiveElementStates:
    """Integration tests for interactive element states.
    
    Requirements: 1.4
    """
    
    def test_button_has_hover_state_defined(self, tk_root):
        """Test that buttons have hover (active) state defined.
        
        Requirements: 1.4
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        from src.email_signature.interface.gui.design_system import DesignSystem
        
        theme_manager = ThemeManager(tk_root)
        style = theme_manager.style
        
        # Get the state map for TButton
        button_map = style.map('TButton')
        
        # Verify hover state is defined
        assert 'background' in button_map
        bg_states = button_map['background']
        
        # Check that active state is defined
        active_states = [state for state in bg_states if 'active' in state]
        assert len(active_states) > 0, "Button should have active (hover) state"
        
        # Verify active state uses surface_hover color
        for state in bg_states:
            if 'active' in state:
                assert state[1] == DesignSystem.colors.surface_hover
    
    def test_button_has_disabled_state_defined(self, tk_root):
        """Test that buttons have disabled state defined.
        
        Requirements: 1.4
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        
        theme_manager = ThemeManager(tk_root)
        style = theme_manager.style
        
        # Get the state map for TButton
        button_map = style.map('TButton')
        
        # Verify disabled state is defined for both background and foreground
        assert 'background' in button_map
        assert 'foreground' in button_map
        
        bg_states = button_map['background']
        fg_states = button_map['foreground']
        
        # Check that disabled state is defined
        disabled_bg = [state for state in bg_states if 'disabled' in state]
        disabled_fg = [state for state in fg_states if 'disabled' in state]
        
        assert len(disabled_bg) > 0, "Button should have disabled background state"
        assert len(disabled_fg) > 0, "Button should have disabled foreground state"
    
    def test_entry_has_focus_state_defined(self, tk_root):
        """Test that entry fields have focus state defined.
        
        Requirements: 1.4
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        from src.email_signature.interface.gui.design_system import DesignSystem
        
        theme_manager = ThemeManager(tk_root)
        style = theme_manager.style
        
        # Get the state map for TEntry
        entry_map = style.map('TEntry')
        
        # Verify focus state is defined
        assert 'bordercolor' in entry_map
        border_states = entry_map['bordercolor']
        
        # Check that focus state is defined
        focus_states = [state for state in border_states if 'focus' in state]
        assert len(focus_states) > 0, "Entry should have focus state"
        
        # Verify focus state uses border_focus color
        for state in border_states:
            if 'focus' in state:
                assert state[1] == DesignSystem.colors.border_focus
    
    def test_primary_button_has_hover_state(self, tk_root):
        """Test that primary buttons have hover state defined.
        
        Requirements: 1.4
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        from src.email_signature.interface.gui.design_system import DesignSystem
        
        theme_manager = ThemeManager(tk_root)
        style = theme_manager.style
        
        # Get the state map for Primary.TButton
        primary_map = style.map('Primary.TButton')
        
        # Verify hover state is defined
        assert 'background' in primary_map
        bg_states = primary_map['background']
        
        # Check that active state is defined
        active_states = [state for state in bg_states if 'active' in state]
        assert len(active_states) > 0, "Primary button should have active (hover) state"
        
        # Verify active state uses primary_hover color
        for state in bg_states:
            if 'active' in state:
                assert state[1] == DesignSystem.colors.primary_hover


class TestDesignSystemConsistency:
    """Integration tests for design system consistency across components.
    
    Requirements: 1.2
    """
    
    def test_all_labels_use_design_system_fonts(self, tk_root):
        """Test that all label styles use fonts from design system.
        
        Requirements: 1.2
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        from src.email_signature.interface.gui.design_system import DesignSystem
        
        theme_manager = ThemeManager(tk_root)
        style = theme_manager.style
        
        # Check TLabel
        label_config = style.configure('TLabel')
        assert 'font' in label_config
        
        # Check Heading.TLabel
        heading_config = style.configure('Heading.TLabel')
        assert 'font' in heading_config
        heading_font = heading_config['font']
        # Font is returned as a string or tuple, need to parse it
        # Verify it contains the expected size and weight
        font_str = str(heading_font)
        assert str(DesignSystem.typography.size_xl) in font_str
        assert 'bold' in font_str.lower()
        
        # Check Secondary.TLabel
        secondary_config = style.configure('Secondary.TLabel')
        assert 'font' in secondary_config
        secondary_font = secondary_config['font']
        # Verify it contains the expected size
        font_str = str(secondary_font)
        assert str(DesignSystem.typography.size_sm) in font_str
    
    def test_all_frames_use_design_system_background(self, tk_root):
        """Test that all frame styles use background from design system.
        
        Requirements: 1.2
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        from src.email_signature.interface.gui.design_system import DesignSystem
        
        theme_manager = ThemeManager(tk_root)
        style = theme_manager.style
        
        # Check TFrame
        frame_config = style.configure('TFrame')
        assert frame_config.get('background') == DesignSystem.colors.background
        
        # Check TLabelframe
        labelframe_config = style.configure('TLabelframe')
        assert labelframe_config.get('background') == DesignSystem.colors.background
    
    def test_all_buttons_use_design_system_spacing(self, tk_root):
        """Test that all button styles use spacing from design system.
        
        Requirements: 1.2
        """
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        from src.email_signature.interface.gui.design_system import DesignSystem
        
        theme_manager = ThemeManager(tk_root)
        style = theme_manager.style
        
        # Check TButton padding
        button_config = style.configure('TButton')
        assert 'padding' in button_config
        button_padding = button_config['padding']
        # Padding is returned as a string, need to parse it
        padding_str = str(button_padding)
        # Should contain design system spacing values
        assert str(DesignSystem.spacing.md) in padding_str
        assert str(DesignSystem.spacing.sm) in padding_str
        
        # Check Primary.TButton padding
        primary_config = style.configure('Primary.TButton')
        assert 'padding' in primary_config
        primary_padding = primary_config['padding']
        # Should contain design system spacing values
        padding_str = str(primary_padding)
        assert str(DesignSystem.spacing.lg) in padding_str
        assert str(DesignSystem.spacing.sm) in padding_str
