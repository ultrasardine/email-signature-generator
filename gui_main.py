"""
GUI entry point for the email signature generator application.

This module initializes all dependencies, checks for Tkinter availability,
and launches the graphical user interface.
"""

import logging
import sys
from pathlib import Path


def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> None:
    """Main entry point for the GUI application."""
    # Set up logging first
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting Email Signature Generator GUI")

    # Step 1: Check all GUI dependencies
    from src.email_signature.infrastructure.platform_utils import DependencyChecker
    
    all_ok, errors = DependencyChecker.check_gui_dependencies()
    if not all_ok:
        logger.error("Missing required dependencies for GUI")
        print("\nError: Missing required dependencies\n")
        for error in errors:
            print(error)
            print()
        sys.exit(1)

    logger.info("All dependencies available")

    try:
        # Step 2: Load configuration
        from src.email_signature.domain.config import ConfigLoader

        logger.debug("Loading configuration")
        config_path = Path("config/default_config.yaml")

        if config_path.exists():
            config = ConfigLoader.load(str(config_path))
            logger.info(f"Configuration loaded from {config_path}")
        else:
            config = ConfigLoader.load(None)
            logger.info("Using default configuration")

        # Step 3: Initialize dependencies
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        from src.email_signature.domain.validators import InputValidator
        from src.email_signature.infrastructure.file_service import FileSystemService
        from src.email_signature.infrastructure.image_renderer import ImageRenderer
        from src.email_signature.infrastructure.logo_loader import LogoLoader

        logger.debug("Initializing dependencies")

        # Create validator
        validator = InputValidator()

        # Create logo loader
        logo_loader = LogoLoader(config.logo_search_paths)

        # Create image renderer
        image_renderer = ImageRenderer(config)

        # Create file system service
        file_service = FileSystemService()

        # Create use case
        use_case = GenerateSignatureUseCase(
            image_renderer=image_renderer,
            logo_loader=logo_loader,
            file_service=file_service,
            config=config,
        )

        logger.info("All dependencies initialized successfully")

        # Step 4: Create and run the main window
        from src.email_signature.interface.gui.main_window import MainWindow

        main_window = MainWindow(
            config=config,
            validator=validator,
            use_case=use_case,
        )

        logger.info("Launching GUI")
        main_window.run()

        logger.info("GUI closed normally")

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nError: An unexpected error occurred: {e}")
        print("Please check the logs for more details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
