"""Design system module providing centralized styling constants and utilities.

This module defines the core design system for the Email Signature Generator GUI,
including color palettes, typography scales, spacing constants, and helper utilities
for consistent styling across all GUI components.
"""

import platform
from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPalette:
    """Immutable color palette for the application."""

    # Primary colors - main brand and actions
    primary: str = "#2563EB"          # Blue 600 - primary actions
    primary_hover: str = "#1D4ED8"    # Blue 700 - hover state
    primary_active: str = "#1E40AF"   # Blue 800 - active state
    primary_light: str = "#DBEAFE"    # Blue 100 - light backgrounds

    # Secondary colors - supporting elements
    secondary: str = "#64748B"        # Slate 500 - secondary text
    secondary_hover: str = "#475569"  # Slate 600 - hover state
    secondary_light: str = "#F1F5F9"  # Slate 100 - light backgrounds

    # Accent colors - highlights and focus
    accent: str = "#8B5CF6"           # Violet 500 - accents
    accent_light: str = "#EDE9FE"     # Violet 100 - light backgrounds

    # Neutral colors - backgrounds and borders
    background: str = "#FFFFFF"       # White - main background
    surface: str = "#F8FAFC"          # Slate 50 - elevated surfaces
    surface_hover: str = "#F1F5F9"    # Slate 100 - hover surfaces
    border: str = "#E2E8F0"           # Slate 200 - borders
    border_focus: str = "#64748B"     # Slate 500 - focus borders (5.1:1 contrast)

    # Text colors - with proper contrast
    text_primary: str = "#0F172A"     # Slate 900 - primary text (16.9:1 contrast)
    text_secondary: str = "#475569"   # Slate 600 - secondary text (7.5:1 contrast)
    text_tertiary: str = "#64748B"    # Slate 500 - tertiary text (5.1:1 contrast)
    text_disabled: str = "#94A3B8"    # Slate 400 - disabled text
    text_on_primary: str = "#FFFFFF"  # White text on primary color

    # Semantic colors - status and feedback
    success: str = "#047857"          # Green 700 - meets 4.5:1 contrast on white
    success_light: str = "#D1FAE5"    # Green 100
    success_text: str = "#065F46"     # Green 800

    warning: str = "#B45309"          # Amber 700 - meets 4.5:1 contrast on white
    warning_light: str = "#FEF3C7"    # Amber 100
    warning_text: str = "#92400E"     # Amber 800

    error: str = "#B91C1C"            # Red 700 - meets 4.5:1 contrast on white
    error_light: str = "#FEE2E2"      # Red 100
    error_text: str = "#991B1B"       # Red 800

    info: str = "#1D4ED8"             # Blue 700 - meets 4.5:1 contrast on white
    info_light: str = "#DBEAFE"       # Blue 100
    info_text: str = "#1E40AF"        # Blue 800


@dataclass(frozen=True)
class Typography:
    """Typography scale and font definitions."""

    # Font families (platform-specific fallbacks handled by Tkinter)
    font_family: str = "Segoe UI"     # Windows default
    font_family_mac: str = "SF Pro Text"  # macOS
    font_family_linux: str = "Ubuntu"     # Linux
    font_family_fallback: str = "sans-serif"

    # Font sizes (in points for Tkinter)
    size_xs: int = 9
    size_sm: int = 10
    size_base: int = 11
    size_lg: int = 13
    size_xl: int = 15
    size_2xl: int = 18
    size_3xl: int = 22

    # Font weights
    weight_normal: str = "normal"
    weight_bold: str = "bold"

    # Line heights (multipliers)
    line_height_tight: float = 1.2
    line_height_normal: float = 1.5
    line_height_relaxed: float = 1.75


@dataclass(frozen=True)
class Spacing:
    """Spacing scale for consistent layout."""

    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 24
    xxl: int = 32
    xxxl: int = 48


@dataclass(frozen=True)
class BorderRadius:
    """Border radius values for rounded corners."""

    none: int = 0
    sm: int = 2
    md: int = 4
    lg: int = 6
    xl: int = 8
    full: int = 9999  # Fully rounded


class DesignSystem:
    """Central design system providing all styling constants and utilities."""

    colors = ColorPalette()
    typography = Typography()
    spacing = Spacing()
    radius = BorderRadius()

    @staticmethod
    def get_font_family() -> str:
        """Get platform-appropriate font family.

        Returns:
            Font family name appropriate for the current platform
        """
        system = platform.system()
        if system == "Darwin":
            return DesignSystem.typography.font_family_mac
        elif system == "Windows":
            return DesignSystem.typography.font_family
        else:
            return DesignSystem.typography.font_family_linux

    @staticmethod
    def get_font(size: int = None, weight: str = "normal") -> tuple[str, int, str]:
        """Get font tuple for Tkinter widgets.

        Args:
            size: Font size in points (default: base size)
            weight: Font weight ("normal" or "bold")

        Returns:
            Tuple of (family, size, weight) for Tkinter font configuration
        """
        if size is None:
            size = DesignSystem.typography.size_base
        return (DesignSystem.get_font_family(), size, weight)

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple.

        Args:
            hex_color: Hex color string (e.g., "#2563EB")

        Returns:
            RGB tuple (r, g, b)

        Raises:
            ValueError: If hex_color is not a valid hex color format
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color format: #{hex_color}")
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError as e:
            raise ValueError(f"Invalid hex color format: #{hex_color}") from e

    @staticmethod
    def calculate_contrast_ratio(color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors.

        Args:
            color1: First hex color
            color2: Second hex color

        Returns:
            Contrast ratio (1.0 to 21.0)

        Raises:
            ValueError: If either color is not a valid hex color format
        """
        def relative_luminance(rgb: tuple[int, int, int]) -> float:
            """Calculate relative luminance of RGB color."""
            r, g, b = [x / 255.0 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        lum1 = relative_luminance(DesignSystem.hex_to_rgb(color1))
        lum2 = relative_luminance(DesignSystem.hex_to_rgb(color2))

        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)

        return (lighter + 0.05) / (darker + 0.05)
