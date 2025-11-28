"""Signature tab for entering signature data and generating signatures."""

import logging
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    import tkinter as tk

    from ...application.use_cases import GenerateSignatureUseCase
    from ...domain.config import SignatureConfig
    from ...domain.validators import InputValidator
    from .config_state import ConfigState

from ...infrastructure.platform_utils import SystemCommandExecutor, ErrorMessageFormatter
from .design_system import DesignSystem
from .element_positioning import ElementPositioning
from .preview_generator import PreviewGenerator
from .profile_manager import ProfileManager
from .validation_mixin import ValidationMixin

logger = logging.getLogger(__name__)


class SignatureTab(ValidationMixin):
    """Tab for entering signature data and generating signatures.

    This tab provides:
    - Form fields for all signature data (name, position, address, phone, mobile, email, website)
    - Real-time validation with visual feedback
    - Generate button that is enabled only when form is valid
    - Status bar for messages
    """

    def __init__(
        self,
        parent: "tk.Widget",
        config: Union["SignatureConfig", "ConfigState"],
        validator: "InputValidator",
        use_case: "GenerateSignatureUseCase",
    ) -> None:
        """Initialize the signature tab.

        Args:
            parent: Parent widget (typically a notebook)
            config: Configuration for signature generation (SignatureConfig or ConfigState)
            validator: Input validator for form fields
            use_case: Use case for generating signatures
        """
        from tkinter import ttk

        from .config_state import ConfigState

        # Initialize ValidationMixin
        super().__init__()

        # Support both ConfigState and SignatureConfig for backward compatibility
        if isinstance(config, ConfigState):
            self.config_state: ConfigState | None = config
            self.config = config.config
        else:
            self.config_state = None
            self.config = config

        self.validator = validator
        self.use_case = use_case

        # Create preview generator
        self.preview_generator = PreviewGenerator(use_case)

        # Create profile manager
        self.profile_manager = ProfileManager()

        # Create main frame for this tab
        self.frame = ttk.Frame(parent, padding="10")

        # Store field widgets and their StringVars
        self.field_vars: dict[str, tk.StringVar] = {}
        self.field_widgets: dict[str, tk.Entry] = {}

        # Track validation state for each field
        self.field_valid: dict[str, bool] = {}

        # Logo selection state
        self.selected_logo_path: str | None = None
        self.logo_preview_label: tk.Label | None = None

        # Preview state
        self.preview_image_label: tk.Label | None = None
        self.preview_photo: tk.PhotoImage | None = None
        self.auto_update_preview: bool = True

        # Element positioning widget (will be set if ConfigState is available)
        self.element_positioning: ElementPositioning | None = None

        # Create the UI components with 2-column responsive layout
        self._create_main_layout()

        # Register as listener for config changes if using ConfigState
        if self.config_state is not None:
            self.config_state.add_listener(self._on_config_changed)

        logger.info("SignatureTab initialized")

    def _create_main_layout(self) -> None:
        """Create the main 2-column responsive layout."""
        import tkinter as tk
        from tkinter import ttk

        ds = DesignSystem

        # Configure main frame grid - 2 columns
        self.frame.columnconfigure(0, weight=1)  # Left column (form + logo)
        self.frame.columnconfigure(1, weight=1)  # Right column (preview)
        self.frame.rowconfigure(0, weight=1)     # Main content row
        self.frame.rowconfigure(1, weight=0)     # Action buttons row
        self.frame.rowconfigure(2, weight=0)     # Status bar row

        # Left panel - contains form and logo
        left_panel = ttk.Frame(self.frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, ds.spacing.sm))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=0)  # Form
        left_panel.rowconfigure(1, weight=0)  # Logo
        left_panel.rowconfigure(2, weight=1)  # Element positioning (expandable)

        # Right panel - contains preview
        right_panel = ttk.Frame(self.frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(ds.spacing.sm, 0))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        # Create components in their respective panels
        self._create_form_fields(left_panel)
        self._create_logo_section(left_panel)
        self._create_element_positioning_section(left_panel)
        self._create_preview_section(right_panel)
        self._create_action_buttons()
        self._create_status_bar()

    def _create_form_fields(self, parent: "tk.Widget") -> None:
        """Create form fields for signature data."""
        import tkinter as tk
        from tkinter import ttk

        ds = DesignSystem

        # Create a frame for the form
        form_frame = ttk.LabelFrame(parent, text="Signature Information", padding=ds.spacing.md)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=ds.spacing.sm, pady=ds.spacing.sm)

        # Configure grid weights for proper resizing
        form_frame.columnconfigure(1, weight=1)

        # Define fields: (field_name, label_text, is_required)
        fields = [
            ("name", "Name:", True),
            ("position", "Position:", True),
            ("address", "Address:", True),
            ("phone", "Phone:", False),
            ("mobile", "Mobile:", False),
            ("email", "Email:", True),
            ("website", "Website:", False),
        ]

        # Create label and entry for each field
        # Use single row per field (no extra row for error - errors shown inline)
        for idx, (field_name, label_text, is_required) in enumerate(fields):
            row = idx

            # Create label
            label = ttk.Label(form_frame, text=label_text)
            label.grid(row=row, column=0, sticky="w", padx=ds.spacing.sm, pady=(ds.spacing.xs, ds.spacing.xs))

            # Add asterisk for required fields
            if is_required:
                required_label = ttk.Label(form_frame, text="*", foreground=ds.colors.error)
                required_label.grid(row=row, column=0, sticky="e")

            # Create StringVar for this field
            var = tk.StringVar()
            self.field_vars[field_name] = var

            # Create entry widget
            entry = ttk.Entry(form_frame, textvariable=var, width=40)
            entry.grid(row=row, column=1, sticky="ew", padx=ds.spacing.sm, pady=(ds.spacing.xs, ds.spacing.xs))
            self.field_widgets[field_name] = entry

            # Initialize validation state
            self.field_valid[field_name] = False

            # Set up real-time validation
            # Use trace to trigger validation on any change
            var.trace_add("write", lambda *args, fn=field_name: self._on_field_change(fn))

        # Set default value for website
        self.field_vars["website"].set("www.example.com")

        logger.debug("Form fields created")

    def _create_element_positioning_section(self, parent: "tk.Widget") -> None:
        """Create element positioning section for drag-and-drop reordering.

        This section is only created if ConfigState is available, as it requires
        the shared configuration state for real-time updates.

        Requirements: 2.1
        """
        # Only create element positioning if we have ConfigState
        if self.config_state is None:
            logger.debug("Skipping element positioning section: no ConfigState available")
            return

        # Create ElementPositioning widget
        self.element_positioning = ElementPositioning(
            parent=parent,
            config_state=self.config_state
        )

        # Position the element positioning frame
        ds = DesignSystem
        self.element_positioning.frame.grid(row=2, column=0, sticky="nsew", padx=ds.spacing.sm, pady=ds.spacing.sm)

        logger.debug("Element positioning section created")

    def _create_logo_section(self, parent: "tk.Widget") -> None:
        """Create logo selection and preview section."""
        import tkinter as tk
        from tkinter import ttk

        ds = DesignSystem

        # Create a frame for the logo section
        logo_frame = ttk.LabelFrame(parent, text="Logo", padding=ds.spacing.md)
        logo_frame.grid(row=1, column=0, sticky="nsew", padx=ds.spacing.sm, pady=ds.spacing.sm)

        # Configure grid weights
        logo_frame.columnconfigure(1, weight=1)

        # Logo path display
        path_label = ttk.Label(logo_frame, text="Logo File:")
        path_label.grid(row=0, column=0, sticky="w", padx=ds.spacing.sm, pady=ds.spacing.sm)

        self.logo_path_var = tk.StringVar()
        self.logo_path_var.set("(using default logo)")

        self.logo_path_display = ttk.Label(
            logo_frame,
            textvariable=self.logo_path_var,
            relief="sunken",
            padding=ds.spacing.sm
        )
        self.logo_path_display.grid(row=0, column=1, sticky="ew", padx=ds.spacing.sm, pady=ds.spacing.sm)

        # Browse button
        browse_button = ttk.Button(
            logo_frame,
            text="Browse...",
            command=self._on_browse_logo_clicked
        )
        browse_button.grid(row=0, column=2, sticky="w", padx=ds.spacing.sm, pady=ds.spacing.sm)

        # Logo preview
        preview_label = ttk.Label(logo_frame, text="Preview:")
        preview_label.grid(row=1, column=0, sticky="nw", padx=ds.spacing.sm, pady=ds.spacing.sm)

        # Create a frame for the logo preview image
        preview_frame = ttk.Frame(logo_frame, relief="sunken", borderwidth=2)
        preview_frame.grid(row=1, column=1, columnspan=2, sticky="w", padx=ds.spacing.sm, pady=ds.spacing.sm)

        # Logo preview label (will hold the image)
        self.logo_preview_label = ttk.Label(preview_frame, text="No logo selected")
        self.logo_preview_label.pack(padx=ds.spacing.sm, pady=ds.spacing.sm)

        # Store reference to prevent garbage collection
        self.logo_preview_image = None

        logger.debug("Logo section created")

    def _on_browse_logo_clicked(self) -> None:
        """Handle browse logo button click."""
        import os
        from tkinter import filedialog


        # Open file picker dialog with PNG/JPG filter
        file_path = filedialog.askopenfilename(
            title="Select Logo File",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )

        # If user selected a file
        if file_path:
            self.selected_logo_path = file_path

            # Update the path display
            # Show just the filename if it's too long
            display_path = file_path
            if len(file_path) > 50:
                display_path = "..." + file_path[-47:]
            self.logo_path_var.set(display_path)

            # Update the preview
            self._update_logo_preview(file_path)

            self.set_status(f"Logo selected: {os.path.basename(file_path)}")
            logger.info(f"Logo file selected: {file_path}")
        else:
            logger.debug("Logo file selection cancelled")

    def _update_logo_preview(self, logo_path: str) -> None:
        """Update the logo preview thumbnail.

        Args:
            logo_path: Path to the logo file
        """

        from PIL import Image, ImageTk

        try:
            # Load the image
            image = Image.open(logo_path)

            # Create thumbnail (max 150x150)
            thumbnail_size = (150, 150)
            image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)

            # Convert to PhotoImage for Tkinter
            photo = ImageTk.PhotoImage(image)

            # Update the preview label
            self.logo_preview_label.config(image=photo, text="")

            # Store reference to prevent garbage collection
            self.logo_preview_image = photo

            logger.debug(f"Logo preview updated for: {logo_path}")

        except Exception as e:
            error_msg = f"Failed to load logo preview: {str(e)}"
            self.logo_preview_label.config(text="Preview unavailable", image="")
            self.logo_preview_image = None
            self.set_status(error_msg)
            logger.error(error_msg)

    def get_selected_logo_path(self) -> str | None:
        """Get the currently selected logo path.

        Returns:
            Path to selected logo file, or None if using default
        """
        return self.selected_logo_path

    def _create_preview_section(self, parent: "tk.Widget") -> None:
        """Create preview section with image display widget."""
        import tkinter as tk
        from tkinter import ttk

        ds = DesignSystem

        # Create a frame for the preview section
        preview_frame = ttk.LabelFrame(parent, text="Preview", padding=ds.spacing.md)
        preview_frame.grid(row=0, column=0, sticky="nsew", padx=ds.spacing.sm, pady=ds.spacing.sm)

        # Configure grid weights
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)

        # Preview button
        button_container = ttk.Frame(preview_frame)
        button_container.grid(row=0, column=0, sticky="w", padx=ds.spacing.sm, pady=ds.spacing.sm)

        self.preview_button = ttk.Button(
            button_container,
            text="Generate Preview",
            command=self._on_preview_clicked
        )
        self.preview_button.pack(side="left", padx=ds.spacing.sm)

        # Auto-update checkbox
        self.auto_update_var = tk.BooleanVar(value=True)
        auto_update_check = ttk.Checkbutton(
            button_container,
            text="Auto-update preview",
            variable=self.auto_update_var,
            command=self._on_auto_update_toggled
        )
        auto_update_check.pack(side="left", padx=ds.spacing.sm)

        # Create a canvas with scrollbar for the preview image
        canvas_frame = ttk.Frame(preview_frame, relief="sunken", borderwidth=2)
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=ds.spacing.sm, pady=ds.spacing.sm)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        # Canvas for displaying the preview
        self.preview_canvas = tk.Canvas(
            canvas_frame,
            bg=ds.colors.background,
            highlightthickness=0
        )
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.preview_canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.preview_canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.preview_canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        # Label to show preview or message
        self.preview_image_label = ttk.Label(
            self.preview_canvas,
            text="Click 'Generate Preview' to see your signature",
            anchor="center"
        )
        self.preview_canvas.create_window(
            0, 0,
            window=self.preview_image_label,
            anchor="nw",
            tags="preview_label"
        )

        logger.debug("Preview section created")

    def _on_preview_clicked(self) -> None:
        """Handle preview button click."""
        logger.info("Preview button clicked")
        self._generate_preview()

    def _on_auto_update_toggled(self) -> None:
        """Handle auto-update checkbox toggle."""
        self.auto_update_preview = self.auto_update_var.get()
        logger.debug(f"Auto-update preview: {self.auto_update_preview}")

        # If auto-update is enabled and form is valid, generate preview
        if self.auto_update_preview and self.is_form_valid():
            self._generate_preview()

    def _on_config_changed(self) -> None:
        """Handle configuration changes from Settings tab or other sources.

        This callback is invoked by ConfigState when colors, dimensions,
        or element order changes. It triggers a preview refresh if:
        - Auto-update preview is enabled
        - The form is valid (all required fields are filled)

        Requirements: 1.3, 3.1, 3.2, 3.3
        """
        logger.debug("Config change notification received")

        # Only refresh preview if auto-update is enabled and form is valid
        if self.auto_update_preview and self.is_form_valid():
            logger.debug("Triggering preview refresh due to config change")
            self._generate_preview()
        else:
            logger.debug(
                f"Skipping preview refresh: auto_update={self.auto_update_preview}, "
                f"form_valid={self.is_form_valid()}"
            )

    def _generate_preview(self) -> None:
        """Generate and display the signature preview."""
        import threading

        from ...domain.models import SignatureData

        # Check if form is valid
        if not self.is_form_valid():
            self.set_status("Cannot generate preview: form has validation errors")
            logger.warning("Preview generation skipped: form is invalid")
            return

        # Get signature data from form
        form_data = self.get_signature_data()

        try:
            signature_data = SignatureData(
                name=form_data["name"],
                position=form_data["position"],
                address=form_data["address"],
                phone=form_data.get("phone", ""),
                mobile=form_data.get("mobile", ""),
                email=form_data["email"],
                website=form_data.get("website", "")
            )
        except ValueError as e:
            error_msg = f"Invalid signature data: {str(e)}"
            self.set_status(error_msg)
            logger.error(error_msg)
            return

        # Disable preview button and show loading indicator
        self.preview_button.config(state="disabled")
        self.set_status("Generating preview...")
        self._show_preview_loading()

        # Run preview generation in background thread
        def generate_preview_in_background():
            try:
                logger.info(f"Generating preview for {signature_data.name}")

                # Generate preview (this is the slow operation)
                preview_image = self.preview_generator.generate_preview(
                    signature_data,
                    self.selected_logo_path
                )

                # Update UI from main thread (check if widget still exists)
                try:
                    self.frame.after(0, lambda: self._on_preview_success(preview_image))
                except RuntimeError:
                    # Widget was destroyed or no main loop running (e.g., in tests)
                    logger.debug("Cannot update UI: no main loop running")

            except Exception as e:
                error_msg = f"Failed to generate preview: {str(e)}"
                logger.error(error_msg, exc_info=True)
                # Update UI from main thread (check if widget still exists)
                try:
                    self.frame.after(0, lambda: self._on_preview_error(error_msg))
                except RuntimeError:
                    # Widget was destroyed or no main loop running (e.g., in tests)
                    logger.debug("Cannot update UI: no main loop running")

        # Start background thread
        thread = threading.Thread(target=generate_preview_in_background, daemon=True)
        thread.start()

    def _show_preview_loading(self) -> None:
        """Show loading indicator in preview area."""
        self.preview_image_label.config(
            text="Generating preview...\nPlease wait...",
            image=""
        )
        self.preview_photo = None

    def _on_preview_success(self, preview_image) -> None:
        """Handle successful preview generation.

        Args:
            preview_image: PIL Image object containing the preview
        """
        from PIL import ImageTk

        # Re-enable preview button
        self.preview_button.config(state="normal")

        # Convert to PhotoImage for Tkinter
        photo = ImageTk.PhotoImage(preview_image)

        # Update the preview display
        self.preview_image_label.config(image=photo, text="")
        self.preview_photo = photo  # Keep reference to prevent garbage collection

        # Update canvas scroll region
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

        self.set_status("Preview generated successfully")
        logger.info("Preview generated and displayed successfully")

    def _on_preview_error(self, error_message: str) -> None:
        """Handle preview generation error.

        Args:
            error_message: Error message to display
        """
        # Re-enable preview button
        self.preview_button.config(state="normal")

        # Update status
        self.set_status(error_message)

        # Show error in preview area
        self.preview_image_label.config(
            text=f"Preview generation failed:\n{error_message}",
            image=""
        )
        self.preview_photo = None
        logger.error(f"Preview generation failed: {error_message}")

    def _create_action_buttons(self) -> None:
        """Create action buttons (generate, profile operations, etc.)."""
        from tkinter import ttk

        ds = DesignSystem

        # Create a frame for action buttons - spans both columns
        button_frame = ttk.Frame(self.frame, padding=ds.spacing.md)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=ds.spacing.sm, pady=ds.spacing.sm)

        # Create generate button (initially disabled) - styled as primary
        self.generate_button = ttk.Button(
            button_frame,
            text="Generate Signature",
            command=self._on_generate_clicked,
            state="disabled",
            style="Primary.TButton"
        )
        self.generate_button.pack(side="left", padx=ds.spacing.sm)

        # Add separator
        ttk.Separator(button_frame, orient="vertical").pack(side="left", fill="y", padx=ds.spacing.md)

        # Profile action buttons (secondary styling - default TButton)
        ttk.Label(button_frame, text="Profiles:").pack(side="left", padx=ds.spacing.sm)

        self.save_profile_button = ttk.Button(
            button_frame,
            text="Save Profile",
            command=self._on_save_profile_clicked
        )
        self.save_profile_button.pack(side="left", padx=ds.spacing.sm)

        self.load_profile_button = ttk.Button(
            button_frame,
            text="Load Profile",
            command=self._on_load_profile_clicked
        )
        self.load_profile_button.pack(side="left", padx=ds.spacing.sm)

        self.delete_profile_button = ttk.Button(
            button_frame,
            text="Delete Profile",
            command=self._on_delete_profile_clicked
        )
        self.delete_profile_button.pack(side="left", padx=ds.spacing.sm)

        logger.debug("Action buttons created")

    def _create_status_bar(self) -> None:
        """Create status bar for messages."""
        from tkinter import ttk

        ds = DesignSystem

        # Create a frame for status bar - spans both columns
        status_frame = ttk.Frame(self.frame, relief="sunken", padding=ds.spacing.xs)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=ds.spacing.sm, pady=ds.spacing.sm)

        # Create status label with secondary text color
        self.status_label = ttk.Label(status_frame, text="Ready", anchor="w", style="Secondary.TLabel")
        self.status_label.pack(fill="x")

        logger.debug("Status bar created")

    def _on_field_change(self, field_name: str) -> None:
        """Handle field value change and trigger validation.

        Args:
            field_name: Name of the field that changed
        """
        value = self.field_vars[field_name].get()
        self._validate_field(field_name, value)
        self._update_generate_button_state()

        # Auto-update preview if enabled and form is valid
        if self.auto_update_preview and self.is_form_valid():
            self._generate_preview()

    def _validate_field(self, field_name: str, value: str) -> bool:
        """Validate a single field and update visual feedback.

        Args:
            field_name: Name of the field to validate
            value: Current value of the field

        Returns:
            True if field is valid, False otherwise
        """
        widget = self.field_widgets[field_name]

        # Determine which validation to apply
        if field_name == "email":
            is_valid, error_message = self.validator.validate_email(value)
        elif field_name in ("phone", "mobile"):
            is_valid, error_message = self.validator.validate_phone(value)
        elif field_name in ("name", "position", "address"):
            # Required fields
            is_valid, error_message = self.validator.validate_required_field(value, field_name.capitalize())
        else:
            # Optional fields (website)
            is_valid = True
            error_message = ""

        # Update visual feedback
        if is_valid:
            self.clear_validation_error(widget)
            self.set_field_valid(widget)
        else:
            self.set_field_invalid(widget)
            self.show_validation_error(widget, error_message)

        # Update validation state
        self.field_valid[field_name] = is_valid

        logger.debug(f"Field '{field_name}' validation: {is_valid}")
        return is_valid

    def _update_generate_button_state(self) -> None:
        """Update the generate button enabled/disabled state based on form validity."""
        # Check if all required fields are valid
        required_fields = ["name", "position", "address", "email"]

        # All required fields must be valid
        all_valid = all(
            self.field_valid.get(field, False) for field in required_fields
        )

        # Enable button if all required fields are valid
        if all_valid:
            self.generate_button.config(state="normal")
            logger.debug("Generate button enabled")
        else:
            self.generate_button.config(state="disabled")
            logger.debug("Generate button disabled")

    def _on_generate_clicked(self) -> None:
        """Handle generate button click."""
        import threading
        from tkinter import filedialog, messagebox

        from ...domain.models import SignatureData

        logger.info("Generate button clicked")

        # Check if form is valid
        if not self.is_form_valid():
            self.set_status("Cannot generate signature: form has validation errors")
            logger.warning("Signature generation skipped: form is invalid")
            return

        # Ask user for output path
        default_filename = "email_signature.png"
        file_path = filedialog.asksaveasfilename(
            title="Save Signature As",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ],
            initialfile=default_filename
        )

        # If user cancelled the dialog
        if not file_path:
            logger.debug("Signature generation cancelled by user")
            return

        # Get signature data from form
        form_data = self.get_signature_data()

        try:
            signature_data = SignatureData(
                name=form_data["name"],
                position=form_data["position"],
                address=form_data["address"],
                phone=form_data.get("phone", ""),
                mobile=form_data.get("mobile", ""),
                email=form_data["email"],
                website=form_data.get("website", "")
            )
        except ValueError as e:
            error_msg = f"Invalid signature data: {str(e)}"
            self.set_status(error_msg)
            messagebox.showerror("Validation Error", error_msg)
            logger.error(error_msg)
            return

        # Disable generate button and show loading indicator
        self.generate_button.config(state="disabled")
        self.set_status("Generating signature... Please wait...")
        self._show_generation_loading()

        # Run generation in background thread to avoid blocking UI
        def generate_in_background():
            try:
                logger.info(f"Generating signature for {signature_data.name} to {file_path}")

                # Use the use case to generate the signature
                # If a custom logo is selected, temporarily override the logo loader
                if self.selected_logo_path:
                    # Save original search paths
                    original_paths = self.use_case.logo_loader.search_paths
                    # Set custom logo path
                    self.use_case.logo_loader.search_paths = [self.selected_logo_path]
                    try:
                        output_path = self.use_case.execute(signature_data, file_path)
                    finally:
                        # Restore original search paths
                        self.use_case.logo_loader.search_paths = original_paths
                else:
                    output_path = self.use_case.execute(signature_data, file_path)

                # Update UI from main thread (check if widget still exists)
                try:
                    self.frame.after(0, lambda: self._on_generation_success(output_path))
                except RuntimeError:
                    # Widget was destroyed or no main loop running (e.g., in tests)
                    logger.debug("Cannot update UI: no main loop running")

            except Exception as e:
                error_msg = f"Failed to generate signature: {str(e)}"
                logger.error(error_msg, exc_info=True)
                # Update UI from main thread (check if widget still exists)
                try:
                    self.frame.after(0, lambda: self._on_generation_error(error_msg))
                except RuntimeError:
                    # Widget was destroyed or no main loop running (e.g., in tests)
                    logger.debug("Cannot update UI: no main loop running")

        # Start background thread
        thread = threading.Thread(target=generate_in_background, daemon=True)
        thread.start()

    def _show_generation_loading(self) -> None:
        """Show loading indicator during signature generation."""
        # Update button text to show it's working
        self.generate_button.config(text="Generating...")
        # Force UI update
        self.frame.update_idletasks()

    def _on_generation_success(self, output_path: str) -> None:
        """Handle successful signature generation.

        Args:
            output_path: Path where signature was saved
        """
        import os
        from pathlib import Path
        from tkinter import messagebox

        from ...infrastructure.platform_utils import (
            ErrorMessageFormatter,
            SystemCommandExecutor,
            get_platform,
        )

        # Re-enable generate button and restore text
        self.generate_button.config(state="normal", text="Generate Signature")

        # Update status
        self.set_status(f"Signature saved successfully to {output_path}")
        logger.info(f"Signature generation completed: {output_path}")

        # Get platform-appropriate success message
        platform_name = get_platform()
        platform_display = {
            'windows': 'Windows',
            'darwin': 'macOS',
            'linux': 'Linux'
        }.get(platform_name, platform_name)

        # Show success message with option to open containing folder
        result = messagebox.askyesno(
            "Success",
            f"Signature saved successfully!\n\n{output_path}\n\nWould you like to open the containing folder?",
            icon="info"
        )

        if result:
            # Open the containing folder using SystemCommandExecutor
            folder_path = Path(os.path.dirname(output_path))
            success = SystemCommandExecutor.open_folder(folder_path)

            if success:
                logger.info(f"Opened folder: {folder_path}")
                self.set_status(f"Opened folder in {platform_display} file manager")
            else:
                # Format platform-specific error message
                error_msg = ErrorMessageFormatter.format_command_error(
                    SystemCommandExecutor.get_open_folder_command(folder_path),
                    f"Could not open folder in {platform_display} file manager"
                )
                logger.error(f"Failed to open folder: {folder_path}")
                messagebox.showwarning(
                    "Warning",
                    f"Signature saved successfully, but could not open the folder.\n\n{error_msg}"
                )

    def _on_generation_error(self, error_message: str) -> None:
        """Handle signature generation error.

        Args:
            error_message: Error message to display
        """
        from tkinter import messagebox

        # Re-enable generate button and restore text
        self.generate_button.config(state="normal", text="Generate Signature")

        # Update status
        self.set_status(error_message)

        # Show error dialog
        messagebox.showerror("Generation Error", error_message)
        logger.error(f"Signature generation failed: {error_message}")

    def set_status(self, message: str) -> None:
        """Update the status bar message.

        Args:
            message: Status message to display
        """
        self.status_label.config(text=message)
        logger.debug(f"Status updated: {message}")

    def get_signature_data(self) -> dict[str, str]:
        """Get the current signature data from the form.

        Returns:
            Dictionary of field names to values
        """
        return {
            field_name: var.get()
            for field_name, var in self.field_vars.items()
        }

    def is_form_valid(self) -> bool:
        """Check if the entire form is valid.

        Returns:
            True if all required fields are valid, False otherwise
        """
        required_fields = ["name", "position", "address", "email"]
        return all(
            self.field_valid.get(field, False) for field in required_fields
        )

    def _on_save_profile_clicked(self) -> None:
        """Handle save profile button click."""
        from tkinter import messagebox, simpledialog

        from ...domain.models import SignatureData

        logger.info("Save profile button clicked")

        # Prompt user for profile name
        profile_name = simpledialog.askstring(
            "Save Profile",
            "Enter a name for this profile:",
            parent=self.frame
        )

        # If user cancelled
        if not profile_name:
            logger.debug("Save profile cancelled by user")
            return

        try:
            # Get signature data from form
            form_data = self.get_signature_data()
            signature_data = SignatureData(
                name=form_data["name"],
                position=form_data["position"],
                address=form_data["address"],
                phone=form_data.get("phone", ""),
                mobile=form_data.get("mobile", ""),
                email=form_data["email"],
                website=form_data.get("website", "")
            )

            # Save the profile
            self.profile_manager.save_profile(profile_name, signature_data)

            # Show success message
            self.set_status(f"Profile '{profile_name}' saved successfully")
            messagebox.showinfo(
                "Success",
                f"Profile '{profile_name}' has been saved successfully.",
                parent=self.frame
            )
            logger.info(f"Profile '{profile_name}' saved successfully")

        except ValueError as e:
            error_msg = f"Invalid profile data: {str(e)}"
            self.set_status(error_msg)
            messagebox.showerror("Validation Error", error_msg, parent=self.frame)
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"Failed to save profile: {str(e)}"
            self.set_status(error_msg)
            messagebox.showerror("Error", error_msg, parent=self.frame)
            logger.error(error_msg, exc_info=True)

    def _on_load_profile_clicked(self) -> None:
        """Handle load profile button click."""
        import tkinter as tk
        from tkinter import messagebox, ttk

        logger.info("Load profile button clicked")

        # Get list of available profiles
        try:
            profiles = self.profile_manager.list_profiles()
        except Exception as e:
            error_msg = f"Failed to list profiles: {str(e)}"
            self.set_status(error_msg)
            messagebox.showerror("Error", error_msg, parent=self.frame)
            logger.error(error_msg, exc_info=True)
            return

        # Check if there are any profiles
        if not profiles:
            messagebox.showinfo(
                "No Profiles",
                "No saved profiles found. Save a profile first.",
                parent=self.frame
            )
            logger.debug("No profiles available to load")
            return

        # Create a dialog to select a profile
        dialog = tk.Toplevel(self.frame)
        dialog.title("Load Profile")
        dialog.transient(self.frame)
        dialog.grab_set()

        # Center the dialog
        dialog.geometry("300x400")

        # Create frame for content
        content_frame = ttk.Frame(dialog, padding="10")
        content_frame.pack(fill="both", expand=True)

        # Label
        ttk.Label(content_frame, text="Select a profile to load:").pack(pady=5)

        # Listbox with scrollbar
        list_frame = ttk.Frame(content_frame)
        list_frame.pack(fill="both", expand=True, pady=5)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        # Populate listbox
        for profile in profiles:
            listbox.insert(tk.END, profile)

        # Select first item by default
        if profiles:
            listbox.selection_set(0)

        # Variable to store selected profile
        selected_profile = [None]

        def on_load():
            selection = listbox.curselection()
            if selection:
                selected_profile[0] = listbox.get(selection[0])
                dialog.destroy()

        def on_cancel():
            dialog.destroy()

        # Double-click to load
        listbox.bind("<Double-Button-1>", lambda e: on_load())

        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="Load", command=on_load).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="left", padx=5)

        # Wait for dialog to close
        dialog.wait_window()

        # If a profile was selected, load it
        if selected_profile[0]:
            self._load_profile(selected_profile[0])

    def _load_profile(self, profile_name: str) -> None:
        """Load a profile and populate form fields.

        Args:
            profile_name: Name of the profile to load
        """
        from tkinter import messagebox

        try:
            # Load the profile
            signature_data = self.profile_manager.load_profile(profile_name)

            # Populate form fields
            self.field_vars["name"].set(signature_data.name)
            self.field_vars["position"].set(signature_data.position)
            self.field_vars["address"].set(signature_data.address)
            self.field_vars["phone"].set(signature_data.phone)
            self.field_vars["mobile"].set(signature_data.mobile)
            self.field_vars["email"].set(signature_data.email)
            self.field_vars["website"].set(signature_data.website)

            # Trigger validation for all fields
            for field_name in self.field_vars.keys():
                value = self.field_vars[field_name].get()
                self._validate_field(field_name, value)

            # Update generate button state
            self._update_generate_button_state()

            # Show success message
            self.set_status(f"Profile '{profile_name}' loaded successfully")
            messagebox.showinfo(
                "Success",
                f"Profile '{profile_name}' has been loaded successfully.",
                parent=self.frame
            )
            logger.info(f"Profile '{profile_name}' loaded successfully")

            # Auto-update preview if enabled
            if self.auto_update_preview and self.is_form_valid():
                self._generate_preview()

        except FileNotFoundError:
            error_msg = f"Profile '{profile_name}' not found"
            self.set_status(error_msg)
            messagebox.showerror("Error", error_msg, parent=self.frame)
            logger.error(error_msg)
        except ValueError as e:
            error_msg = f"Invalid profile data: {str(e)}"
            self.set_status(error_msg)
            messagebox.showerror("Validation Error", error_msg, parent=self.frame)
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"Failed to load profile: {str(e)}"
            self.set_status(error_msg)
            messagebox.showerror("Error", error_msg, parent=self.frame)
            logger.error(error_msg, exc_info=True)

    def _on_delete_profile_clicked(self) -> None:
        """Handle delete profile button click."""
        import tkinter as tk
        from tkinter import messagebox, ttk

        logger.info("Delete profile button clicked")

        # Get list of available profiles
        try:
            profiles = self.profile_manager.list_profiles()
        except Exception as e:
            error_msg = f"Failed to list profiles: {str(e)}"
            self.set_status(error_msg)
            messagebox.showerror("Error", error_msg, parent=self.frame)
            logger.error(error_msg, exc_info=True)
            return

        # Check if there are any profiles
        if not profiles:
            messagebox.showinfo(
                "No Profiles",
                "No saved profiles found.",
                parent=self.frame
            )
            logger.debug("No profiles available to delete")
            return

        # Create a dialog to select a profile
        dialog = tk.Toplevel(self.frame)
        dialog.title("Delete Profile")
        dialog.transient(self.frame)
        dialog.grab_set()

        # Center the dialog
        dialog.geometry("300x400")

        # Create frame for content
        content_frame = ttk.Frame(dialog, padding="10")
        content_frame.pack(fill="both", expand=True)

        # Label
        ttk.Label(content_frame, text="Select a profile to delete:").pack(pady=5)

        # Listbox with scrollbar
        list_frame = ttk.Frame(content_frame)
        list_frame.pack(fill="both", expand=True, pady=5)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        # Populate listbox
        for profile in profiles:
            listbox.insert(tk.END, profile)

        # Select first item by default
        if profiles:
            listbox.selection_set(0)

        # Variable to store selected profile
        selected_profile = [None]

        def on_delete():
            selection = listbox.curselection()
            if selection:
                selected_profile[0] = listbox.get(selection[0])
                dialog.destroy()

        def on_cancel():
            dialog.destroy()

        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="Delete", command=on_delete).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="left", padx=5)

        # Wait for dialog to close
        dialog.wait_window()

        # If a profile was selected, confirm and delete it
        if selected_profile[0]:
            # Confirm deletion
            result = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete the profile '{selected_profile[0]}'?\n\nThis action cannot be undone.",
                parent=self.frame,
                icon="warning"
            )

            if result:
                self._delete_profile(selected_profile[0])

    def _delete_profile(self, profile_name: str) -> None:
        """Delete a profile.

        Args:
            profile_name: Name of the profile to delete
        """
        from tkinter import messagebox

        try:
            # Delete the profile
            self.profile_manager.delete_profile(profile_name)

            # Show success message
            self.set_status(f"Profile '{profile_name}' deleted successfully")
            messagebox.showinfo(
                "Success",
                f"Profile '{profile_name}' has been deleted successfully.",
                parent=self.frame
            )
            logger.info(f"Profile '{profile_name}' deleted successfully")

        except FileNotFoundError:
            error_msg = f"Profile '{profile_name}' not found"
            self.set_status(error_msg)
            messagebox.showerror("Error", error_msg, parent=self.frame)
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"Failed to delete profile: {str(e)}"
            self.set_status(error_msg)
            messagebox.showerror("Error", error_msg, parent=self.frame)
            logger.error(error_msg, exc_info=True)

    def cleanup(self) -> None:
        """Clean up resources (temp files, listeners, etc.)."""
        logger.info("Cleaning up SignatureTab resources")

        # Unregister from config state listener if registered
        if self.config_state is not None:
            self.config_state.remove_listener(self._on_config_changed)
            logger.debug("Unregistered from ConfigState listener")

        self.preview_generator.cleanup()
