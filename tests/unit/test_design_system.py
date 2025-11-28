"""Unit tests for GUI design system."""

import platform
import pytest

from src.email_signature.interface.gui.design_system import (
    BorderRadius,
    ColorPalette,
    DesignSystem,
    Spacing,
    Typography,
)


class TestColorPalette:
    """Tests for ColorPalette dataclass."""
    
    def test_color_palette_has_required_attributes(self) -> None:
        """Test that ColorPalette has all required color attributes."""
        colors = ColorPalette()
        
        # Primary colors
        assert hasattr(colors, 'primary')
        assert hasattr(colors, 'primary_hover')
        assert hasattr(colors, 'primary_active')
        assert hasattr(colors, 'primary_light')
        
        # Secondary colors
        assert hasattr(colors, 'secondary')
        assert hasattr(colors, 'secondary_hover')
        assert hasattr(colors, 'secondary_light')
        
        # Accent colors
        assert hasattr(colors, 'accent')
        assert hasattr(colors, 'accent_light')
        
        # Neutral colors
        assert hasattr(colors, 'background')
        assert hasattr(colors, 'surface')
        assert hasattr(colors, 'surface_hover')
        assert hasattr(colors, 'border')
        assert hasattr(colors, 'border_focus')
        
        # Text colors
        assert hasattr(colors, 'text_primary')
        assert hasattr(colors, 'text_secondary')
        assert hasattr(colors, 'text_tertiary')
        assert hasattr(colors, 'text_disabled')
        assert hasattr(colors, 'text_on_primary')
        
        # Semantic colors
        assert hasattr(colors, 'success')
        assert hasattr(colors, 'success_light')
        assert hasattr(colors, 'success_text')
        assert hasattr(colors, 'warning')
        assert hasattr(colors, 'warning_light')
        assert hasattr(colors, 'warning_text')
        assert hasattr(colors, 'error')
        assert hasattr(colors, 'error_light')
        assert hasattr(colors, 'error_text')
        assert hasattr(colors, 'info')
        assert hasattr(colors, 'info_light')
        assert hasattr(colors, 'info_text')
    
    def test_color_palette_is_immutable(self) -> None:
        """Test that ColorPalette is immutable (frozen dataclass)."""
        colors = ColorPalette()
        
        with pytest.raises(AttributeError):
            colors.primary = "#000000"


class TestTypography:
    """Tests for Typography dataclass."""
    
    def test_typography_has_required_attributes(self) -> None:
        """Test that Typography has all required font attributes."""
        typo = Typography()
        
        # Font families
        assert hasattr(typo, 'font_family')
        assert hasattr(typo, 'font_family_mac')
        assert hasattr(typo, 'font_family_linux')
        assert hasattr(typo, 'font_family_fallback')
        
        # Font sizes
        assert hasattr(typo, 'size_xs')
        assert hasattr(typo, 'size_sm')
        assert hasattr(typo, 'size_base')
        assert hasattr(typo, 'size_lg')
        assert hasattr(typo, 'size_xl')
        assert hasattr(typo, 'size_2xl')
        assert hasattr(typo, 'size_3xl')
        
        # Font weights
        assert hasattr(typo, 'weight_normal')
        assert hasattr(typo, 'weight_bold')
        
        # Line heights
        assert hasattr(typo, 'line_height_tight')
        assert hasattr(typo, 'line_height_normal')
        assert hasattr(typo, 'line_height_relaxed')
    
    def test_base_font_size_meets_minimum(self) -> None:
        """Test that base font size meets minimum readability requirement (11pt)."""
        typo = Typography()
        assert typo.size_base >= 11
    
    def test_typography_is_immutable(self) -> None:
        """Test that Typography is immutable (frozen dataclass)."""
        typo = Typography()
        
        with pytest.raises(AttributeError):
            typo.size_base = 20


class TestSpacing:
    """Tests for Spacing dataclass."""
    
    def test_spacing_has_required_attributes(self) -> None:
        """Test that Spacing has all required spacing attributes."""
        spacing = Spacing()
        
        assert hasattr(spacing, 'xs')
        assert hasattr(spacing, 'sm')
        assert hasattr(spacing, 'md')
        assert hasattr(spacing, 'lg')
        assert hasattr(spacing, 'xl')
        assert hasattr(spacing, 'xxl')
        assert hasattr(spacing, 'xxxl')
    
    def test_spacing_values_are_consistent_scale(self) -> None:
        """Test that spacing values follow a consistent scale."""
        spacing = Spacing()
        
        # Verify spacing values are in ascending order
        assert spacing.xs < spacing.sm < spacing.md < spacing.lg < spacing.xl < spacing.xxl < spacing.xxxl
    
    def test_spacing_is_immutable(self) -> None:
        """Test that Spacing is immutable (frozen dataclass)."""
        spacing = Spacing()
        
        with pytest.raises(AttributeError):
            spacing.md = 20


class TestBorderRadius:
    """Tests for BorderRadius dataclass."""
    
    def test_border_radius_has_required_attributes(self) -> None:
        """Test that BorderRadius has all required attributes."""
        radius = BorderRadius()
        
        assert hasattr(radius, 'none')
        assert hasattr(radius, 'sm')
        assert hasattr(radius, 'md')
        assert hasattr(radius, 'lg')
        assert hasattr(radius, 'xl')
        assert hasattr(radius, 'full')
    
    def test_border_radius_is_immutable(self) -> None:
        """Test that BorderRadius is immutable (frozen dataclass)."""
        radius = BorderRadius()
        
        with pytest.raises(AttributeError):
            radius.md = 10


class TestDesignSystemHelpers:
    """Tests for DesignSystem helper methods."""
    
    def test_get_font_returns_correct_tuple_format(self) -> None:
        """Test get_font() returns correct tuple format for Tkinter.
        
        Requirements: 5.1, 5.4
        """
        # Test with default parameters
        font = DesignSystem.get_font()
        assert isinstance(font, tuple)
        assert len(font) == 3
        assert isinstance(font[0], str)  # family
        assert isinstance(font[1], int)  # size
        assert isinstance(font[2], str)  # weight
        
        # Test with custom size
        font = DesignSystem.get_font(size=14)
        assert font[1] == 14
        
        # Test with custom weight
        font = DesignSystem.get_font(weight='bold')
        assert font[2] == 'bold'
        
        # Test with both custom size and weight
        font = DesignSystem.get_font(size=16, weight='bold')
        assert font[1] == 16
        assert font[2] == 'bold'
    
    def test_get_font_uses_platform_appropriate_family(self) -> None:
        """Test get_font() uses appropriate font family for platform."""
        font = DesignSystem.get_font()
        font_family = font[0]
        
        system = platform.system()
        if system == "Darwin":
            assert font_family == DesignSystem.typography.font_family_mac
        elif system == "Windows":
            assert font_family == DesignSystem.typography.font_family
        else:
            assert font_family == DesignSystem.typography.font_family_linux
    
    def test_hex_to_rgb_converts_colors_correctly(self) -> None:
        """Test hex_to_rgb() converts hex colors to RGB tuples correctly.
        
        Requirements: 5.1, 5.4
        """
        # Test with # prefix
        rgb = DesignSystem.hex_to_rgb("#FFFFFF")
        assert rgb == (255, 255, 255)
        
        rgb = DesignSystem.hex_to_rgb("#000000")
        assert rgb == (0, 0, 0)
        
        rgb = DesignSystem.hex_to_rgb("#FF0000")
        assert rgb == (255, 0, 0)
        
        rgb = DesignSystem.hex_to_rgb("#00FF00")
        assert rgb == (0, 255, 0)
        
        rgb = DesignSystem.hex_to_rgb("#0000FF")
        assert rgb == (0, 0, 255)
        
        # Test without # prefix
        rgb = DesignSystem.hex_to_rgb("FFFFFF")
        assert rgb == (255, 255, 255)
        
        # Test with lowercase
        rgb = DesignSystem.hex_to_rgb("#ffffff")
        assert rgb == (255, 255, 255)
        
        # Test with mixed case
        rgb = DesignSystem.hex_to_rgb("#FfFfFf")
        assert rgb == (255, 255, 255)
    
    def test_hex_to_rgb_raises_error_for_invalid_format(self) -> None:
        """Test hex_to_rgb() raises ValueError for invalid hex colors."""
        # Too short
        with pytest.raises(ValueError):
            DesignSystem.hex_to_rgb("#FFF")
        
        # Too long
        with pytest.raises(ValueError):
            DesignSystem.hex_to_rgb("#FFFFFFF")
        
        # Invalid characters
        with pytest.raises(ValueError):
            DesignSystem.hex_to_rgb("#GGGGGG")
        
        # Empty string
        with pytest.raises(ValueError):
            DesignSystem.hex_to_rgb("")
    
    def test_calculate_contrast_ratio_calculates_correctly(self) -> None:
        """Test calculate_contrast_ratio() calculates WCAG ratios correctly.
        
        Requirements: 5.1, 5.4
        """
        # Black on white should be maximum contrast (21:1)
        ratio = DesignSystem.calculate_contrast_ratio("#000000", "#FFFFFF")
        assert abs(ratio - 21.0) < 0.1
        
        # White on black should also be 21:1 (symmetric)
        ratio = DesignSystem.calculate_contrast_ratio("#FFFFFF", "#000000")
        assert abs(ratio - 21.0) < 0.1
        
        # Same color should be minimum contrast (1:1)
        ratio = DesignSystem.calculate_contrast_ratio("#FFFFFF", "#FFFFFF")
        assert abs(ratio - 1.0) < 0.01
        
        ratio = DesignSystem.calculate_contrast_ratio("#000000", "#000000")
        assert abs(ratio - 1.0) < 0.01
        
        # Test a known contrast ratio
        # #767676 on white has approximately 4.5:1 contrast
        ratio = DesignSystem.calculate_contrast_ratio("#767676", "#FFFFFF")
        assert 4.4 < ratio < 4.6
    
    def test_calculate_contrast_ratio_is_symmetric(self) -> None:
        """Test that contrast ratio is symmetric (order doesn't matter)."""
        color1 = "#2563EB"
        color2 = "#FFFFFF"
        
        ratio1 = DesignSystem.calculate_contrast_ratio(color1, color2)
        ratio2 = DesignSystem.calculate_contrast_ratio(color2, color1)
        
        assert abs(ratio1 - ratio2) < 0.01
    
    def test_calculate_contrast_ratio_returns_valid_range(self) -> None:
        """Test that contrast ratio is always in valid range (1.0 to 21.0)."""
        test_colors = [
            "#FFFFFF", "#000000", "#FF0000", "#00FF00", "#0000FF",
            "#2563EB", "#0F172A", "#64748B", "#10B981", "#EF4444"
        ]
        
        for color1 in test_colors:
            for color2 in test_colors:
                ratio = DesignSystem.calculate_contrast_ratio(color1, color2)
                assert 1.0 <= ratio <= 21.0


class TestDesignSystemIntegration:
    """Integration tests for DesignSystem class."""
    
    def test_design_system_has_all_components(self) -> None:
        """Test that DesignSystem provides access to all design components."""
        assert isinstance(DesignSystem.colors, ColorPalette)
        assert isinstance(DesignSystem.typography, Typography)
        assert isinstance(DesignSystem.spacing, Spacing)
        assert isinstance(DesignSystem.radius, BorderRadius)
    
    def test_design_system_helper_methods_exist(self) -> None:
        """Test that DesignSystem provides all required helper methods."""
        assert callable(DesignSystem.get_font_family)
        assert callable(DesignSystem.get_font)
        assert callable(DesignSystem.hex_to_rgb)
        assert callable(DesignSystem.calculate_contrast_ratio)


class TestThemeManager:
    """Unit tests for ThemeManager class.
    
    Requirements: 5.5
    """
    
    def test_theme_manager_initializes_without_errors(self) -> None:
        """Test ThemeManager initializes without errors."""
        import tkinter as tk
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
        except tk.TclError:
            pytest.skip("Tkinter not available in test environment")
        
        try:
            theme_manager = ThemeManager(root)
            assert theme_manager is not None
            assert theme_manager.root is root
            assert theme_manager.style is not None
        finally:
            root.destroy()
    
    def test_theme_manager_configures_all_required_widget_styles(self) -> None:
        """Test all required widget styles are configured."""
        import tkinter as tk
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
        except tk.TclError:
            pytest.skip("Tkinter not available in test environment")
        
        try:
            theme_manager = ThemeManager(root)
            style = theme_manager.style
            
            # Test that all required widget styles are configured
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
            
            for style_name in required_styles:
                # Verify style exists by trying to get its configuration
                # If style doesn't exist, this would return empty dict or raise error
                config = style.configure(style_name)
                assert config is not None, f"Style {style_name} not configured"
        finally:
            root.destroy()
    
    def test_theme_manager_uses_clam_theme(self) -> None:
        """Test ThemeManager uses 'clam' theme as base."""
        import tkinter as tk
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
        except tk.TclError:
            pytest.skip("Tkinter not available in test environment")
        
        try:
            theme_manager = ThemeManager(root)
            # After initialization, the theme should be 'clam'
            assert theme_manager.style.theme_use() == 'clam'
        finally:
            root.destroy()
    
    def test_apply_to_widget_handles_standard_widgets(self) -> None:
        """Test apply_to_widget() method works with standard Tkinter widgets."""
        import tkinter as tk
        from src.email_signature.interface.gui.theme_manager import ThemeManager
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
        except tk.TclError:
            pytest.skip("Tkinter not available in test environment")
        
        try:
            theme_manager = ThemeManager(root)
            
            # Test with Label widget
            label = tk.Label(root, text="Test")
            theme_manager.apply_to_widget(label)
            # Should not raise any errors
            
            # Test with Frame widget
            frame = tk.Frame(root)
            theme_manager.apply_to_widget(frame)
            # Should not raise any errors
        finally:
            root.destroy()
