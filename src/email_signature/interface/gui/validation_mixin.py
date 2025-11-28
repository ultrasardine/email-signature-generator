"""Validation feedback mixin for GUI widgets."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tkinter as tk

from .design_system import DesignSystem

logger = logging.getLogger(__name__)


class ValidationMixin:
    """Mixin class providing visual validation feedback for form widgets.

    This mixin provides methods to show validation errors and set field
    validity states with visual indicators (colors, borders, etc.).
    """

    def __init__(self) -> None:
        """Initialize the validation mixin."""
        # Store validation error labels for each widget
        self._validation_labels: dict[tk.Widget, tk.Label] = {}
        # Store original widget configurations for restoration
        self._original_configs: dict[tk.Widget, dict] = {}

    def show_validation_error(self, widget: "tk.Widget", message: str) -> None:
        """Show a validation error message for a widget.

        Args:
            widget: The widget to show the error for
            message: The error message to display
        """
        from tkinter import ttk

        ds = DesignSystem

        # Set the widget to invalid state
        self.set_field_invalid(widget)

        # Check if we already have a label for this widget
        if widget in self._validation_labels:
            error_label = self._validation_labels[widget]
            error_label.config(text=message)
        else:
            # Create a new error label
            # Get the parent frame
            parent = widget.master

            # Create error label with semantic error color
            error_label = ttk.Label(
                parent,
                text=message,
                foreground=ds.colors.error_text,
                font=ds.get_font(ds.typography.size_sm)
            )

            # Store the label reference
            self._validation_labels[widget] = error_label

            # Position the error label below the widget
            # Get the widget's grid info
            grid_info = widget.grid_info()
            if grid_info:
                row = int(grid_info.get("row", 0))
                column = int(grid_info.get("column", 0))
                columnspan = int(grid_info.get("columnspan", 1))

                # Place error label in the next row
                error_label.grid(
                    row=row + 1,
                    column=column,
                    columnspan=columnspan,
                    sticky="w",
                    padx=(ds.spacing.sm, 0)
                )
            else:
                # If not using grid, try pack
                error_label.pack(anchor="w", padx=ds.spacing.sm)

        logger.debug(f"Showing validation error for widget: {message}")

    def clear_validation_error(self, widget: "tk.Widget") -> None:
        """Clear the validation error for a widget.

        Args:
            widget: The widget to clear the error for
        """
        from tkinter import ttk

        # Remove error label if it exists
        if widget in self._validation_labels:
            error_label = self._validation_labels[widget]
            error_label.grid_forget()  # Remove from grid
            error_label.destroy()
            del self._validation_labels[widget]

        # Restore default widget appearance
        try:
            if isinstance(widget, ttk.Entry):
                # Reset to default TEntry style
                widget.configure(style="TEntry")
            elif hasattr(widget, 'configure'):
                # For standard tk widgets, restore to default background
                ds = DesignSystem
                widget.configure(background=ds.colors.background)
        except Exception as e:
            logger.warning(f"Failed to restore widget appearance: {e}")

        logger.debug("Cleared validation error for widget")

    def set_field_valid(self, widget: "tk.Widget") -> None:
        """Set a field to valid state with success styling.

        Args:
            widget: The widget to mark as valid
        """
        from tkinter import ttk

        ds = DesignSystem

        # Clear any existing error
        self.clear_validation_error(widget)

        # For ttk widgets, use the Success.TEntry style
        try:
            if isinstance(widget, ttk.Entry):
                widget.configure(style="Success.TEntry")
            elif hasattr(widget, 'configure'):
                # For standard tk widgets, use design system colors
                widget.configure(background=ds.colors.success_light)
        except Exception as e:
            logger.warning(f"Failed to set valid indicator: {e}")

        logger.debug("Set field to valid state")

    def set_field_invalid(self, widget: "tk.Widget") -> None:
        """Set a field to invalid state with error styling.

        Args:
            widget: The widget to mark as invalid
        """
        from tkinter import ttk

        ds = DesignSystem

        # For ttk widgets, use the Error.TEntry style
        try:
            if isinstance(widget, ttk.Entry):
                widget.configure(style="Error.TEntry")
            elif hasattr(widget, 'configure'):
                # For standard tk widgets, use design system colors
                widget.configure(background=ds.colors.error_light)
        except Exception as e:
            logger.warning(f"Failed to set invalid indicator: {e}")

        logger.debug("Set field to invalid state")
