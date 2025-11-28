"""Shared configuration state with change notification for GUI components.

This module provides a ConfigState class that holds the current SignatureConfig
and notifies listeners when changes occur, enabling real-time preview updates.
"""

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import tkinter as tk

    from ...domain.config import SignatureConfig

logger = logging.getLogger(__name__)


class ConfigState:
    """Shared configuration state with change notification.

    This class manages the in-memory SignatureConfig and provides:
    - Property access to the current configuration
    - Methods to update colors, dimensions, and element order
    - Listener registration for change notifications
    - Debounced notifications to prevent excessive updates

    Attributes:
        config: The current SignatureConfig instance
    """

    def __init__(
        self,
        config: "SignatureConfig",
        root: Optional["tk.Tk"] = None,
        debounce_delay_ms: int = 300,
    ) -> None:
        """Initialize the ConfigState.

        Args:
            config: SignatureConfig instance to manage
            root: Optional Tkinter root for debouncing with after()
            debounce_delay_ms: Delay in milliseconds for debouncing (default 300ms)
        """
        self._config = config
        self._root = root
        self._listeners: list[Callable[[], None]] = []
        self._debounce_timer: str | None = None
        self._debounce_delay_ms = debounce_delay_ms

        logger.debug(
            f"ConfigState initialized with debounce delay {debounce_delay_ms}ms"
        )

    @property
    def config(self) -> "SignatureConfig":
        """Get the current configuration.

        Returns:
            The current SignatureConfig instance
        """
        return self._config

    def update_color(self, color_name: str, color_value: tuple[int, ...]) -> None:
        """Update a color value and notify listeners with debouncing.

        Args:
            color_name: Name of the color to update (e.g., 'name', 'details')
            color_value: RGB or RGBA tuple for the new color
        """
        self._config.colors[color_name] = color_value
        logger.debug(f"Color '{color_name}' updated to {color_value}")
        self._notify_debounced()

    def update_dimension(self, dimension_name: str, value: int) -> None:
        """Update a dimension value and notify listeners with debouncing.

        Args:
            dimension_name: Name of the dimension attribute to update
            value: New integer value for the dimension
        """
        if hasattr(self._config, dimension_name):
            setattr(self._config, dimension_name, value)
            logger.debug(f"Dimension '{dimension_name}' updated to {value}")
            self._notify_debounced()
        else:
            logger.warning(
                f"Attempted to update unknown dimension: {dimension_name}"
            )

    def update_element_order(self, order: list[str]) -> None:
        """Update element order and notify listeners immediately.

        Element order changes are notified immediately (not debounced)
        because drag-and-drop operations should provide instant feedback.

        Args:
            order: List of element IDs in the new order
        """
        self._config.element_order = order
        logger.debug(f"Element order updated to {order}")
        self._notify_immediate()

    def add_listener(self, callback: Callable[[], None]) -> None:
        """Register a callback for configuration changes.

        Args:
            callback: Function to call when configuration changes
        """
        if callback not in self._listeners:
            self._listeners.append(callback)
            logger.debug(f"Listener added, total listeners: {len(self._listeners)}")

    def remove_listener(self, callback: Callable[[], None]) -> None:
        """Unregister a callback.

        Args:
            callback: Function to remove from listeners
        """
        if callback in self._listeners:
            self._listeners.remove(callback)
            logger.debug(
                f"Listener removed, total listeners: {len(self._listeners)}"
            )

    def _notify_debounced(self) -> None:
        """Notify listeners with debouncing for rapid changes.

        This method cancels any pending notification and schedules a new one
        after the debounce delay. This prevents excessive preview regeneration
        when the user is rapidly changing settings.
        """
        # Cancel pending notification if exists
        if self._debounce_timer is not None and self._root is not None:
            try:
                self._root.after_cancel(self._debounce_timer)
                logger.debug("Cancelled pending debounced notification")
            except Exception:
                # Timer may have already fired
                pass
            self._debounce_timer = None

        # Schedule new notification
        if self._root is not None:
            self._debounce_timer = self._root.after(
                self._debounce_delay_ms,
                self._notify_immediate
            )
            logger.debug(
                f"Scheduled debounced notification in {self._debounce_delay_ms}ms"
            )
        else:
            # No root available, notify immediately
            self._notify_immediate()

    def _notify_immediate(self) -> None:
        """Notify all listeners immediately.

        This method calls all registered listener callbacks. If a callback
        raises an exception, it is logged but does not prevent other
        listeners from being notified.
        """
        self._debounce_timer = None
        logger.debug(f"Notifying {len(self._listeners)} listeners")

        for listener in self._listeners:
            try:
                listener()
            except Exception as e:
                logger.error(
                    f"Error in config change listener: {e}",
                    exc_info=True
                )

    def set_root(self, root: "tk.Tk") -> None:
        """Set the Tkinter root for debouncing.

        This allows setting the root after initialization if it wasn't
        available at construction time.

        Args:
            root: Tkinter root window
        """
        self._root = root
        logger.debug("Tkinter root set for debouncing")
