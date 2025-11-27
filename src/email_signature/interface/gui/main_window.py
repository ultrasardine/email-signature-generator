"""Main window for the email signature generator GUI."""

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...application.use_cases import GenerateSignatureUseCase
    from ...domain.config import SignatureConfig
    from ...domain.validators import InputValidator

logger = logging.getLogger(__name__)


def check_tkinter_available() -> bool:
    """Check if Tkinter is available on the system.

    Returns:
        True if Tkinter is available, False otherwise
    """
    try:
        import tkinter as tk
        # Try to create a test instance to verify it works
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        return True
    except ImportError:
        return False
    except Exception:
        # Tkinter might be importable but not functional (e.g., no display)
        return False


def get_tkinter_install_instructions() -> str:
    """Get platform-specific Tkinter installation instructions.

    Returns:
        Installation instructions string
    """
    if sys.platform == "darwin":
        return (
            "Tkinter is not available. On macOS, you can install it with:\n"
            "  brew install python-tk\n"
            "Or reinstall Python with Tkinter support:\n"
            "  brew reinstall python@3.x --with-tcl-tk"
        )
    elif sys.platform == "win32":
        return (
            "Tkinter is not available. On Windows, Tkinter should be included\n"
            "with Python. Try reinstalling Python and ensure 'tcl/tk and IDLE'\n"
            "is selected during installation."
        )
    else:  # Linux
        return (
            "Tkinter is not available. On Linux, install it with:\n"
            "  Ubuntu/Debian: sudo apt-get install python3-tk\n"
            "  Fedora: sudo dnf install python3-tkinter\n"
            "  Arch: sudo pacman -S tk"
        )


class MainWindow:
    """Main application window for the email signature generator GUI."""

    def __init__(
        self,
        config: "SignatureConfig",
        validator: "InputValidator",
        use_case: "GenerateSignatureUseCase",
    ) -> None:
        """Initialize the main window.

        Args:
            config: Configuration for signature generation
            validator: Input validator for form fields
            use_case: Use case for generating signatures
        """
        import tkinter as tk

        self.config = config
        self.validator = validator
        self.use_case = use_case

        # Create root window
        self.root = tk.Tk()
        self.root.title("Email Signature Generator")

        # Set window size and position
        window_width = 800
        window_height = 600

        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Set minimum size
        self.root.minsize(600, 400)

        # Configure close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Set up the main layout
        self._setup_ui()

        logger.info("MainWindow initialized successfully")

    def _setup_ui(self) -> None:
        """Set up the main user interface."""
        from tkinter import ttk
        from .signature_tab import SignatureTab
        from .settings_tab import SettingsTab

        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # Header
        self.root.rowconfigure(1, weight=1)  # Main content
        self.root.rowconfigure(2, weight=0)  # Status bar

        # Header frame
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.grid(row=0, column=0, sticky="ew")

        title_label = ttk.Label(
            header_frame,
            text="Email Signature Generator",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack()

        # Main content frame with notebook
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Create notebook widget for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Create SignatureTab
        self.signature_tab = SignatureTab(
            parent=self.notebook,
            config=self.config,
            validator=self.validator,
            use_case=self.use_case
        )
        
        # Add SignatureTab to notebook
        self.notebook.add(self.signature_tab.frame, text="Signature")

        # Create SettingsTab
        self.settings_tab = SettingsTab(
            parent=self.notebook,
            config=self.config
        )
        
        # Add SettingsTab to notebook
        self.notebook.add(self.settings_tab.frame, text="Settings")

        # Status bar
        self.status_frame = ttk.Frame(self.root, padding="5")
        self.status_frame.grid(row=2, column=0, sticky="ew")

        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready",
            anchor="w"
        )
        self.status_label.pack(fill="x")

    def set_status(self, message: str) -> None:
        """Update the status bar message.

        Args:
            message: Status message to display
        """
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def _on_closing(self) -> None:
        """Handle window close event."""
        from ...infrastructure.platform_utils import TempFileManager
        
        logger.info("Closing application")

        # Clean up signature tab resources (preview temp files)
        if hasattr(self, 'signature_tab'):
            self.signature_tab.cleanup()
        
        # Clean up any remaining temporary files using TempFileManager
        TempFileManager.cleanup_temp_files()

        # Destroy the window
        self.root.destroy()

        logger.info("Application closed cleanly")

    def run(self) -> None:
        """Start the Tkinter main loop."""
        logger.info("Starting GUI main loop")
        self.root.mainloop()
