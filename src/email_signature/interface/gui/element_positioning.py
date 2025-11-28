"""Element positioning widget for drag-and-drop signature element reordering.

This module provides an ElementPositioning widget that allows users to
reorder signature elements using drag-and-drop, with immediate preview feedback.
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .design_system import DesignSystem

if TYPE_CHECKING:
    import tkinter as tk

    from .config_state import ConfigState

logger = logging.getLogger(__name__)


@dataclass
class DragData:
    """Data for tracking drag operation.

    Attributes:
        element_id: ID of the element being dragged
        start_y: Y coordinate where drag started
        source_index: Original index of the element in the list
    """
    element_id: str
    start_y: int
    source_index: int


class ElementPositioning:
    """Widget for drag-and-drop element positioning.

    This widget displays a list of signature elements that can be reordered
    using drag-and-drop. Changes are immediately reflected in the ConfigState,
    triggering preview updates.

    Attributes:
        ELEMENTS: List of (element_id, label) tuples defining available elements
    """

    # Define available signature elements with their display labels
    ELEMENTS = [
        ("logo", "Logo"),
        ("name", "Name"),
        ("position", "Position/Title"),
        ("address", "Address"),
        ("phone", "Phone Numbers"),
        ("email", "Email & Website"),
        ("separator", "Separator Line"),
        ("confidentiality", "Confidentiality Notice"),
    ]

    def __init__(
        self,
        parent: "tk.Widget",
        config_state: "ConfigState",
    ) -> None:
        """Initialize the ElementPositioning widget.

        Args:
            parent: Parent widget to contain this element positioning widget
            config_state: Shared configuration state for real-time updates
        """
        from tkinter import ttk

        self.config_state = config_state
        self.parent = parent

        ds = DesignSystem

        # Create LabelFrame container
        self.frame = ttk.LabelFrame(parent, text="Element Order", padding=ds.spacing.md)

        # Store element item widgets
        self._element_frames: list[tuple[str, tk.Frame]] = []

        # Drag state
        self._drag_data: DragData | None = None
        self._drop_indicator: tk.Frame | None = None

        # Create the element list
        self._create_element_list()

        logger.info("ElementPositioning widget initialized")

    def _create_element_list(self) -> None:
        """Create the list of draggable elements.

        Reads the current element order from config_state and creates
        draggable items for each element in that order.
        """
        import tkinter as tk

        ds = DesignSystem

        # Clear existing elements
        for _, frame in self._element_frames:
            frame.destroy()
        self._element_frames.clear()

        # Get current order from config or use default
        current_order = getattr(
            self.config_state.config,
            'element_order',
            [e[0] for e in self.ELEMENTS]
        )

        # Create a frame for each element in the current order
        for idx, element_id in enumerate(current_order):
            # Find the label for this element
            label = next(
                (e[1] for e in self.ELEMENTS if e[0] == element_id),
                element_id.capitalize()
            )

            # Create element frame
            element_frame = tk.Frame(
                self.frame,
                relief="raised",
                borderwidth=1,
                bg=ds.colors.surface,
                cursor="hand2"
            )
            element_frame.pack(fill="x", padx=ds.spacing.xs, pady=ds.spacing.xs)

            # Store element ID as attribute for later retrieval
            element_frame.element_id = element_id  # type: ignore
            element_frame.element_index = idx  # type: ignore

            # Create drag handle and label
            handle_label = tk.Label(
                element_frame,
                text="≡",
                font=ds.get_font(ds.typography.size_lg),
                bg=ds.colors.surface,
                fg=ds.colors.text_secondary,
                cursor="hand2"
            )
            handle_label.pack(side="left", padx=ds.spacing.sm, pady=ds.spacing.sm)

            text_label = tk.Label(
                element_frame,
                text=label,
                bg=ds.colors.surface,
                fg=ds.colors.text_primary,
                font=ds.get_font(),
                anchor="w"
            )
            text_label.pack(side="left", fill="x", expand=True, padx=ds.spacing.sm, pady=ds.spacing.sm)

            # Bind drag events to the frame and its children
            for widget in [element_frame, handle_label, text_label]:
                widget.bind("<Button-1>", lambda e, eid=element_id, idx=idx: self._on_drag_start(eid, idx, e))
                widget.bind("<B1-Motion>", self._on_drag_motion)
                widget.bind("<ButtonRelease-1>", self._on_drop)

            self._element_frames.append((element_id, element_frame))

        logger.debug(f"Created element list with order: {current_order}")

    def _on_drag_start(self, element_id: str, index: int, event: "tk.Event") -> None:
        """Handle drag start event.

        Args:
            element_id: ID of the element being dragged
            index: Current index of the element
            event: Tkinter event object
        """
        ds = DesignSystem

        self._drag_data = DragData(
            element_id=element_id,
            start_y=event.y_root,
            source_index=index
        )

        # Highlight the dragged element
        for eid, frame in self._element_frames:
            if eid == element_id:
                frame.config(bg=ds.colors.primary_light)
                for child in frame.winfo_children():
                    child.config(bg=ds.colors.primary_light)
                break

        logger.debug(f"Drag started for element '{element_id}' at index {index}")

    def _on_drag_motion(self, event: "tk.Event") -> None:
        """Handle drag motion event.

        Shows a drop indicator at the potential drop position.

        Args:
            event: Tkinter event object
        """
        if self._drag_data is None:
            return

        # Find which element we're hovering over
        target_index = self._get_target_index(event.y_root)

        # Show drop indicator
        self._show_drop_indicator(target_index)

    def _get_target_index(self, y_root: int) -> int:
        """Calculate the target index based on cursor position.

        Args:
            y_root: Y coordinate in root window coordinates

        Returns:
            Target index for dropping the element
        """
        for idx, (_, frame) in enumerate(self._element_frames):
            frame_y = frame.winfo_rooty()
            frame_height = frame.winfo_height()
            frame_center = frame_y + frame_height // 2

            if y_root < frame_center:
                return idx

        # If below all elements, return the last position
        return len(self._element_frames)

    def _show_drop_indicator(self, target_index: int) -> None:
        """Show drop indicator at the target position.

        Args:
            target_index: Index where the element would be dropped
        """
        import tkinter as tk

        ds = DesignSystem

        # Remove existing indicator
        self._hide_drop_indicator()

        # Don't show indicator at the source position or adjacent
        if self._drag_data is not None:
            source_idx = self._drag_data.source_index
            if target_index == source_idx or target_index == source_idx + 1:
                return

        # Create drop indicator line
        self._drop_indicator = tk.Frame(
            self.frame,
            height=3,
            bg=ds.colors.primary
        )

        # Position the indicator
        if target_index < len(self._element_frames):
            # Insert before the target element
            _, target_frame = self._element_frames[target_index]
            self._drop_indicator.pack(before=target_frame, fill="x", padx=ds.spacing.xs)
        else:
            # Insert at the end
            self._drop_indicator.pack(fill="x", padx=ds.spacing.xs)

    def _hide_drop_indicator(self) -> None:
        """Hide the drop indicator."""
        if self._drop_indicator is not None:
            self._drop_indicator.destroy()
            self._drop_indicator = None

    def _on_drop(self, event: "tk.Event") -> None:
        """Handle drop event.

        Performs the reorder operation and updates the config.

        Args:
            event: Tkinter event object
        """
        ds = DesignSystem

        if self._drag_data is None:
            return

        # Get target index
        target_index = self._get_target_index(event.y_root)

        # Perform reorder
        self._reorder_elements(self._drag_data.element_id, self._drag_data.source_index, target_index)

        # Reset drag state
        self._drag_data = None
        self._hide_drop_indicator()

        # Reset element highlighting
        for _, frame in self._element_frames:
            frame.config(bg=ds.colors.surface)
            for child in frame.winfo_children():
                child.config(bg=ds.colors.surface)

    def _reorder_elements(self, source_id: str, source_index: int, target_index: int) -> None:
        """Reorder elements and update config.

        Args:
            source_id: ID of the element being moved
            source_index: Original index of the element
            target_index: Target index for the element
        """
        # Get current order
        current_order = [eid for eid, _ in self._element_frames]

        # Don't reorder if dropping at same position
        if target_index == source_index or target_index == source_index + 1:
            logger.debug("No reorder needed - same position")
            return

        # Remove from current position
        current_order.pop(source_index)

        # Adjust target index if needed (since we removed an element)
        if target_index > source_index:
            target_index -= 1

        # Insert at new position
        current_order.insert(target_index, source_id)

        logger.info(f"Reordered elements: {source_id} moved from {source_index} to {target_index}")
        logger.debug(f"New order: {current_order}")

        # Update config state (triggers immediate preview refresh)
        self.config_state.update_element_order(current_order)

        # Rebuild UI to reflect new order
        self._rebuild_element_list(current_order)

    def _rebuild_element_list(self, new_order: list[str]) -> None:
        """Rebuild the element list UI with the new order.

        Args:
            new_order: List of element IDs in the new order
        """
        # Simply recreate the element list
        # The config_state already has the new order
        self._create_element_list()

    def get_current_order(self) -> list[str]:
        """Get the current element order.

        Returns:
            List of element IDs in current order
        """
        return [eid for eid, _ in self._element_frames]
