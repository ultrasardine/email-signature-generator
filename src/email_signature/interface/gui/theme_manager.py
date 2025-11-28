"""Theme manager module for configuring ttk.Style with design system.

This module provides the ThemeManager class which applies the design system
colors, fonts, and spacing to ttk widgets through ttk.Style configuration.
"""

import tkinter as tk
from tkinter import ttk

from .design_system import DesignSystem


class ThemeManager:
    """Manages ttk.Style configuration and theme application."""

    def __init__(self, root: tk.Tk):
        """Initialize theme manager.

        Args:
            root: Root Tkinter window
        """
        self.root = root
        self.style = ttk.Style(root)
        self._configure_theme()

    def _configure_theme(self) -> None:
        """Configure ttk theme with design system colors."""
        ds = DesignSystem

        # Use 'clam' theme as base (most customizable)
        self.style.theme_use('clam')

        # Configure TFrame
        self.style.configure(
            'TFrame',
            background=ds.colors.background
        )

        # Configure TLabel
        self.style.configure(
            'TLabel',
            background=ds.colors.background,
            foreground=ds.colors.text_primary,
            font=ds.get_font()
        )

        # Configure heading labels
        self.style.configure(
            'Heading.TLabel',
            background=ds.colors.background,
            foreground=ds.colors.text_primary,
            font=ds.get_font(ds.typography.size_xl, 'bold')
        )

        # Configure secondary labels
        self.style.configure(
            'Secondary.TLabel',
            background=ds.colors.background,
            foreground=ds.colors.text_secondary,
            font=ds.get_font(ds.typography.size_sm)
        )

        # Configure TEntry
        self.style.configure(
            'TEntry',
            fieldbackground=ds.colors.background,
            foreground=ds.colors.text_primary,
            bordercolor=ds.colors.border,
            lightcolor=ds.colors.border,
            darkcolor=ds.colors.border,
            insertcolor=ds.colors.text_primary,
            font=ds.get_font()
        )

        self.style.map(
            'TEntry',
            fieldbackground=[('focus', ds.colors.background)],
            bordercolor=[('focus', ds.colors.border_focus)],
            lightcolor=[('focus', ds.colors.border_focus)],
            darkcolor=[('focus', ds.colors.border_focus)]
        )

        # Configure error state for Entry
        self.style.configure(
            'Error.TEntry',
            fieldbackground=ds.colors.error_light,
            foreground=ds.colors.text_primary,
            bordercolor=ds.colors.error,
            lightcolor=ds.colors.error,
            darkcolor=ds.colors.error,
            insertcolor=ds.colors.text_primary,
            font=ds.get_font()
        )

        # Configure success state for Entry
        self.style.configure(
            'Success.TEntry',
            fieldbackground=ds.colors.success_light,
            foreground=ds.colors.text_primary,
            bordercolor=ds.colors.success,
            lightcolor=ds.colors.success,
            darkcolor=ds.colors.success,
            insertcolor=ds.colors.text_primary,
            font=ds.get_font()
        )

        # Configure TButton (default/secondary)
        self.style.configure(
            'TButton',
            background=ds.colors.surface,
            foreground=ds.colors.text_primary,
            bordercolor=ds.colors.border,
            lightcolor=ds.colors.surface,
            darkcolor=ds.colors.border,
            font=ds.get_font(),
            padding=(ds.spacing.md, ds.spacing.sm)
        )

        self.style.map(
            'TButton',
            background=[
                ('active', ds.colors.surface_hover),
                ('disabled', ds.colors.surface)
            ],
            foreground=[('disabled', ds.colors.text_disabled)]
        )

        # Configure primary button
        self.style.configure(
            'Primary.TButton',
            background=ds.colors.primary,
            foreground=ds.colors.text_on_primary,
            bordercolor=ds.colors.primary,
            lightcolor=ds.colors.primary,
            darkcolor=ds.colors.primary,
            font=ds.get_font(weight='bold'),
            padding=(ds.spacing.lg, ds.spacing.sm)
        )

        self.style.map(
            'Primary.TButton',
            background=[
                ('active', ds.colors.primary_hover),
                ('disabled', ds.colors.text_disabled)
            ],
            foreground=[('disabled', ds.colors.background)]
        )

        # Configure TLabelFrame
        self.style.configure(
            'TLabelframe',
            background=ds.colors.background,
            bordercolor=ds.colors.border,
            lightcolor=ds.colors.border,
            darkcolor=ds.colors.border
        )

        self.style.configure(
            'TLabelframe.Label',
            background=ds.colors.background,
            foreground=ds.colors.text_primary,
            font=ds.get_font(ds.typography.size_lg, 'bold')
        )

        # Configure TNotebook (tabs)
        self.style.configure(
            'TNotebook',
            background=ds.colors.surface,
            bordercolor=ds.colors.border,
            lightcolor=ds.colors.border,
            darkcolor=ds.colors.border
        )

        self.style.configure(
            'TNotebook.Tab',
            background=ds.colors.surface,
            foreground=ds.colors.text_secondary,
            padding=(ds.spacing.lg, ds.spacing.sm),
            font=ds.get_font()
        )

        self.style.map(
            'TNotebook.Tab',
            background=[
                ('selected', ds.colors.background),
                ('active', ds.colors.surface_hover)
            ],
            foreground=[('selected', ds.colors.text_primary)],
            expand=[('selected', [1, 1, 1, 0])]
        )

        # Configure TCheckbutton
        self.style.configure(
            'TCheckbutton',
            background=ds.colors.background,
            foreground=ds.colors.text_primary,
            font=ds.get_font()
        )

        # Configure TSeparator
        self.style.configure(
            'TSeparator',
            background=ds.colors.border
        )

    def apply_to_widget(self, widget: tk.Widget) -> None:
        """Apply design system styling to a standard Tkinter widget.

        Args:
            widget: Tkinter widget to style
        """
        ds = DesignSystem

        # Apply background color
        if hasattr(widget, 'configure'):
            try:
                widget.configure(bg=ds.colors.background)
            except tk.TclError:
                pass  # Some widgets don't support bg

            # Apply foreground color for labels
            if isinstance(widget, tk.Label):
                widget.configure(
                    fg=ds.colors.text_primary,
                    font=ds.get_font()
                )
