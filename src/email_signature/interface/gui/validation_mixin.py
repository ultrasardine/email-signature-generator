"""Validation feedback mixin for GUI widgets."""

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import tkinter as tk

logger = logging.getLogger(__name__)


class ValidationMixin:
    """Mixin class providing visual validation feedback for form widgets.
    
    This mixin provides methods to show validation errors and set field
    validity states with visual indicators (colors, borders, etc.).
    """

    def __init__(self) -> None:
        """Initialize the validation mixin."""
        # Store validation error labels for each widget
        self._validation_labels: dict["tk.Widget", "tk.Label"] = {}
        # Store original widget configurations for restoration
        self._original_configs: dict["tk.Widget", dict] = {}

    def show_validation_error(self, widget: "tk.Widget", message: str) -> None:
        """Show a validation error message for a widget.
        
        Args:
            widget: The widget to show the error for
            message: The error message to display
        """
        import tkinter as tk
        from tkinter import ttk

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
            
            # Create error label with red text
            error_label = ttk.Label(
                parent,
                text=message,
                foreground="red",
                font=("Helvetica", 9)
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
                    padx=(5, 0)
                )
            else:
                # If not using grid, try pack
                error_label.pack(anchor="w", padx=5)

        logger.debug(f"Showing validation error for widget: {message}")

    def clear_validation_error(self, widget: "tk.Widget") -> None:
        """Clear the validation error for a widget.
        
        Args:
            widget: The widget to clear the error for
        """
        # Remove error label if it exists
        if widget in self._validation_labels:
            error_label = self._validation_labels[widget]
            error_label.grid_forget()  # Remove from grid
            error_label.destroy()
            del self._validation_labels[widget]

        # Restore original widget appearance
        if widget in self._original_configs:
            try:
                # Restore original configuration
                original = self._original_configs[widget]
                if hasattr(widget, 'configure'):
                    # Only restore style-related configs
                    if 'background' in original:
                        widget.configure(background=original['background'])
                    if 'foreground' in original:
                        widget.configure(foreground=original['foreground'])
            except Exception as e:
                logger.warning(f"Failed to restore original config: {e}")
            
            del self._original_configs[widget]

        logger.debug("Cleared validation error for widget")

    def set_field_valid(self, widget: "tk.Widget") -> None:
        """Set a field to valid state with green indicator.
        
        Args:
            widget: The widget to mark as valid
        """
        # Clear any existing error
        self.clear_validation_error(widget)

        # Store original config if not already stored
        if widget not in self._original_configs:
            try:
                config = {}
                if hasattr(widget, 'cget'):
                    try:
                        config['background'] = widget.cget('background')
                    except:
                        pass
                    try:
                        config['foreground'] = widget.cget('foreground')
                    except:
                        pass
                self._original_configs[widget] = config
            except Exception as e:
                logger.warning(f"Failed to store original config: {e}")
                self._original_configs[widget] = {}

        # Set green border/background to indicate valid
        try:
            # For Entry widgets, we can set a light green background
            if hasattr(widget, 'configure'):
                widget.configure(background="#e8f5e9")  # Light green
        except Exception as e:
            logger.warning(f"Failed to set valid indicator: {e}")

        logger.debug("Set field to valid state")

    def set_field_invalid(self, widget: "tk.Widget") -> None:
        """Set a field to invalid state with red indicator.
        
        Args:
            widget: The widget to mark as invalid
        """
        # Store original config if not already stored
        if widget not in self._original_configs:
            try:
                config = {}
                if hasattr(widget, 'cget'):
                    try:
                        config['background'] = widget.cget('background')
                    except:
                        pass
                    try:
                        config['foreground'] = widget.cget('foreground')
                    except:
                        pass
                self._original_configs[widget] = config
            except Exception as e:
                logger.warning(f"Failed to store original config: {e}")
                self._original_configs[widget] = {}

        # Set red border/background to indicate invalid
        try:
            # For Entry widgets, we can set a light red background
            if hasattr(widget, 'configure'):
                widget.configure(background="#ffebee")  # Light red
        except Exception as e:
            logger.warning(f"Failed to set invalid indicator: {e}")

        logger.debug("Set field to invalid state")
