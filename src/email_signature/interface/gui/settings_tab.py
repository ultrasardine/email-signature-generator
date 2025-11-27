"""Settings tab for editing configuration."""

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import tkinter as tk
    from ...domain.config import SignatureConfig

logger = logging.getLogger(__name__)


class SettingsTab:
    """Tab for editing configuration settings.
    
    This tab provides:
    - Colors section with color picker buttons
    - Dimensions section with validated numeric inputs
    - Fonts section with file path text inputs
    - Load current configuration values on initialization
    """

    def __init__(
        self,
        parent: "tk.Widget",
        config: "SignatureConfig",
    ) -> None:
        """Initialize the settings tab.
        
        Args:
            parent: Parent widget (typically a notebook)
            config: Configuration for signature generation
        """
        from tkinter import ttk
        
        self.config = config
        
        # Create main frame for this tab
        self.frame = ttk.Frame(parent, padding="10")
        
        # Store field widgets and their variables
        self.dimension_vars: dict[str, "tk.IntVar"] = {}
        self.dimension_widgets: dict[str, "tk.Entry"] = {}
        self.color_buttons: dict[str, "tk.Button"] = {}
        self.color_values: dict[str, tuple[int, ...]] = {}
        self.font_vars: dict[str, "tk.StringVar"] = {}
        self.font_widgets: dict[str, "tk.Entry"] = {}
        
        # Create the UI components
        self._create_colors_section()
        self._create_dimensions_section()
        self._create_fonts_section()
        self._create_save_button()
        
        # Status label for messages
        self.status_label: Optional["tk.Label"] = None
        self._create_status_label()
        
        logger.info("SettingsTab initialized")
    
    def _create_colors_section(self) -> None:
        """Create colors section with color picker buttons."""
        import tkinter as tk
        from tkinter import ttk
        
        # Create a frame for the colors section
        colors_frame = ttk.LabelFrame(self.frame, text="Colors", padding="10")
        colors_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure grid weights
        colors_frame.columnconfigure(1, weight=1)
        
        # Define color fields
        color_fields = [
            ("outline", "Outline Color"),
            ("name", "Name Color"),
            ("details", "Details Color"),
            ("separator", "Separator Color"),
            ("confidentiality", "Confidentiality Color"),
        ]
        
        # Create label and color picker button for each color
        for idx, (color_name, label_text) in enumerate(color_fields):
            # Create label
            label = ttk.Label(colors_frame, text=label_text + ":")
            label.grid(row=idx, column=0, sticky="w", padx=5, pady=5)
            
            # Get current color value from config
            current_color = self.config.colors.get(color_name, (0, 0, 0))
            self.color_values[color_name] = current_color
            
            # Create color display button
            color_button = tk.Button(
                colors_frame,
                text="  ",
                width=10,
                command=lambda cn=color_name: self._on_color_picker_clicked(cn)
            )
            color_button.grid(row=idx, column=1, sticky="w", padx=5, pady=5)
            self.color_buttons[color_name] = color_button
            
            # Set button background to current color
            self._update_color_button(color_name, current_color)
            
            # Create RGB label to show current values
            rgb_text = self._format_rgb(current_color)
            rgb_label = ttk.Label(colors_frame, text=rgb_text)
            rgb_label.grid(row=idx, column=2, sticky="w", padx=5, pady=5)
            
            # Store reference to RGB label for updates
            setattr(self, f"{color_name}_rgb_label", rgb_label)
        
        logger.debug("Colors section created")
    
    def _format_rgb(self, color: tuple[int, ...]) -> str:
        """Format RGB/RGBA tuple as string.
        
        Args:
            color: RGB or RGBA tuple
            
        Returns:
            Formatted string like "RGB(255, 255, 255)" or "RGBA(255, 255, 255, 200)"
        """
        if len(color) == 3:
            return f"RGB({color[0]}, {color[1]}, {color[2]})"
        elif len(color) == 4:
            return f"RGBA({color[0]}, {color[1]}, {color[2]}, {color[3]})"
        else:
            return str(color)
    
    def _update_color_button(self, color_name: str, color: tuple[int, ...]) -> None:
        """Update color button background.
        
        Args:
            color_name: Name of the color field
            color: RGB or RGBA tuple
        """
        # Convert RGB to hex for Tkinter
        if len(color) >= 3:
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            button = self.color_buttons[color_name]
            button.config(bg=hex_color)
            
            # Update RGB label
            rgb_label = getattr(self, f"{color_name}_rgb_label", None)
            if rgb_label:
                rgb_label.config(text=self._format_rgb(color))
    
    def _on_color_picker_clicked(self, color_name: str) -> None:
        """Handle color picker button click.
        
        Args:
            color_name: Name of the color field
        """
        from tkinter import colorchooser
        
        # Get current color
        current_color = self.color_values[color_name]
        
        # Convert to hex for color chooser
        if len(current_color) >= 3:
            initial_color = f"#{current_color[0]:02x}{current_color[1]:02x}{current_color[2]:02x}"
        else:
            initial_color = "#000000"
        
        # Open color picker dialog
        color_result = colorchooser.askcolor(
            title=f"Choose {color_name} color",
            initialcolor=initial_color,
            parent=self.frame
        )
        
        # If user selected a color (not cancelled)
        if color_result[0] is not None:
            # color_result is ((r, g, b), "#rrggbb")
            rgb = color_result[0]
            
            # Convert to integers
            r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
            
            # Preserve alpha channel if it exists
            if len(current_color) == 4:
                new_color = (r, g, b, current_color[3])
            else:
                new_color = (r, g, b)
            
            # Update stored value
            self.color_values[color_name] = new_color
            
            # Update button display
            self._update_color_button(color_name, new_color)
            
            logger.info(f"Color '{color_name}' changed to {new_color}")
    
    def _create_dimensions_section(self) -> None:
        """Create dimensions section with validated numeric inputs."""
        import tkinter as tk
        from tkinter import ttk
        
        # Create a frame for the dimensions section
        dimensions_frame = ttk.LabelFrame(self.frame, text="Dimensions", padding="10")
        dimensions_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure grid weights
        dimensions_frame.columnconfigure(1, weight=1)
        
        # Define dimension fields
        dimension_fields = [
            ("logo_height", "Logo Height (px)"),
            ("margin", "Margin (px)"),
            ("logo_margin_right", "Logo Margin Right (px)"),
            ("line_height", "Line Height (px)"),
            ("outline_width_name", "Outline Width Name (px)"),
            ("outline_width_text", "Outline Width Text (px)"),
        ]
        
        # Create label and entry for each dimension
        for idx, (field_name, label_text) in enumerate(dimension_fields):
            # Create label
            label = ttk.Label(dimensions_frame, text=label_text + ":")
            label.grid(row=idx, column=0, sticky="w", padx=5, pady=5)
            
            # Create IntVar for this field
            var = tk.IntVar()
            
            # Get current value from config
            current_value = getattr(self.config, field_name, 0)
            var.set(current_value)
            
            self.dimension_vars[field_name] = var
            
            # Create entry widget with validation
            entry = ttk.Entry(dimensions_frame, textvariable=var, width=15)
            entry.grid(row=idx, column=1, sticky="w", padx=5, pady=5)
            self.dimension_widgets[field_name] = entry
            
            # Set up validation
            vcmd = (entry.register(self._validate_dimension), '%P')
            entry.config(validate='key', validatecommand=vcmd)
        
        logger.debug("Dimensions section created")
    
    def _validate_dimension(self, value: str) -> bool:
        """Validate dimension input (must be positive integer or empty).
        
        Args:
            value: Input value to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Allow empty string (for clearing the field)
        if value == "":
            return True
        
        # Check if it's a valid integer
        try:
            int_value = int(value)
            # Must be positive
            return int_value > 0
        except ValueError:
            return False
    
    def _create_fonts_section(self) -> None:
        """Create fonts section with file path text inputs."""
        import tkinter as tk
        from tkinter import ttk
        import platform
        
        # Create a frame for the fonts section
        fonts_frame = ttk.LabelFrame(self.frame, text="Fonts", padding="10")
        fonts_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure grid weights
        fonts_frame.columnconfigure(1, weight=1)
        
        # Get current platform
        current_platform = platform.system().lower()
        if current_platform == "darwin":
            # Try both "darwin" and "macos" keys for compatibility
            platform_key = "darwin"
            # Check if config uses "macos" instead
            if "macos" in self.config.font_paths and "darwin" not in self.config.font_paths:
                platform_key = "macos"
        elif current_platform == "windows":
            platform_key = "windows"
        else:
            platform_key = "linux"
        
        # Store platform key for later use in save
        self.current_platform_key = platform_key
        
        # Define font fields for current platform
        font_fields = [
            (f"{platform_key}_bold", f"{platform_key.capitalize()} Bold Font"),
            (f"{platform_key}_regular", f"{platform_key.capitalize()} Regular Font"),
        ]
        
        # Get current font paths from config
        current_fonts = self.config.font_paths.get(platform_key, [])
        
        # Create label and entry for each font
        for idx, (field_name, label_text) in enumerate(font_fields):
            # Create label
            label = ttk.Label(fonts_frame, text=label_text + ":")
            label.grid(row=idx, column=0, sticky="w", padx=5, pady=5)
            
            # Create StringVar for this field
            var = tk.StringVar()
            
            # Get current value from config
            if idx < len(current_fonts):
                var.set(current_fonts[idx])
            else:
                var.set("")
            
            self.font_vars[field_name] = var
            
            # Create entry widget
            entry = ttk.Entry(fonts_frame, textvariable=var, width=50)
            entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=5)
            self.font_widgets[field_name] = entry
        
        logger.debug("Fonts section created")
    
    def _create_save_button(self) -> None:
        """Create save settings button."""
        from tkinter import ttk
        
        # Create a frame for the save button
        button_frame = ttk.Frame(self.frame, padding="10")
        button_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=10)
        
        # Create save button
        save_button = ttk.Button(
            button_frame,
            text="Save Settings",
            command=self._on_save_settings_clicked
        )
        save_button.pack(side="left", padx=5)
        
        logger.debug("Save button created")
    
    def _create_status_label(self) -> None:
        """Create status label for messages."""
        import tkinter as tk
        from tkinter import ttk
        
        # Create a frame for the status label
        status_frame = ttk.Frame(self.frame, padding="5")
        status_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        
        # Create status label
        self.status_label = tk.Label(
            status_frame,
            text="",
            anchor="w",
            fg="black"
        )
        self.status_label.pack(fill="x")
        
        logger.debug("Status label created")
    
    def _validate_all_settings(self) -> tuple[bool, str]:
        """Validate all settings before saving.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate dimensions
        for field_name, var in self.dimension_vars.items():
            try:
                value = var.get()
                if value <= 0:
                    return False, f"Dimension '{field_name}' must be a positive integer"
            except Exception:
                return False, f"Dimension '{field_name}' has an invalid value"
        
        # All validations passed
        return True, ""
    
    def _on_save_settings_clicked(self) -> None:
        """Handle save settings button click."""
        import platform
        from pathlib import Path
        import yaml
        
        from ...infrastructure.platform_utils import LineEndingHandler, PathManager
        
        logger.info("Save settings button clicked")
        
        # Validate all settings
        is_valid, error_message = self._validate_all_settings()
        if not is_valid:
            self._show_error(error_message)
            return
        
        # Determine config file path
        config_path = Path("config/default_config.yaml")
        
        try:
            # Read existing config file to preserve format and comments
            if config_path.exists():
                # Use LineEndingHandler to read with universal line ending support
                content = LineEndingHandler.read_text_universal(config_path)
                config_data = yaml.safe_load(content)
                if config_data is None:
                    config_data = {}
            else:
                config_data = {}
            
            # Ensure signature section exists
            if "signature" not in config_data:
                config_data["signature"] = {}
            
            sig_data = config_data["signature"]
            
            # Update dimensions
            if "dimensions" not in sig_data:
                sig_data["dimensions"] = {}
            
            for field_name, var in self.dimension_vars.items():
                sig_data["dimensions"][field_name] = var.get()
            
            # Update colors
            if "colors" not in sig_data:
                sig_data["colors"] = {}
            
            for color_name, color_value in self.color_values.items():
                sig_data["colors"][color_name] = list(color_value)
            
            # Update fonts
            if "fonts" not in sig_data:
                sig_data["fonts"] = {}
            
            # Use the platform key determined during initialization
            platform_key = getattr(self, 'current_platform_key', 'linux')
            
            # Collect font paths for current platform
            font_paths = []
            for field_name, var in self.font_vars.items():
                if field_name.startswith(platform_key):
                    path = var.get().strip()
                    if path:
                        font_paths.append(path)
            
            if font_paths:
                sig_data["fonts"][platform_key] = font_paths
            
            # Ensure parent directory exists using PathManager
            PathManager.ensure_parent_dirs(config_path)
            
            # Write updated config back to file with platform-native line endings
            yaml_content = yaml.dump(config_data, default_flow_style=False, sort_keys=False)
            LineEndingHandler.write_text_platform(config_path, yaml_content)
            
            self._show_success(f"Settings saved successfully to {config_path}")
            logger.info(f"Settings saved to {config_path}")
            
        except Exception as e:
            error_msg = f"Failed to save settings: {str(e)}"
            self._show_error(error_msg)
            logger.error(error_msg, exc_info=True)
    
    def _show_success(self, message: str) -> None:
        """Show success message.
        
        Args:
            message: Success message to display
        """
        if self.status_label:
            self.status_label.config(text=message, fg="green")
    
    def _show_error(self, message: str) -> None:
        """Show error message.
        
        Args:
            message: Error message to display
        """
        if self.status_label:
            self.status_label.config(text=message, fg="red")

