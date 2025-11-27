"""
Main entry point for the email signature generator application.

This module initializes all dependencies, sets up logging, and orchestrates
the signature generation process through the CLI interface.
"""

import logging
import sys
from pathlib import Path

from src.email_signature.application.use_cases import GenerateSignatureUseCase
from src.email_signature.domain.config import ConfigLoader
from src.email_signature.domain.exceptions import (
    FileSystemError,
    ImageRenderError,
    LogoLoadError,
    LogoNotFoundError,
    SignatureGeneratorError,
    ValidationError,
)
from src.email_signature.domain.validators import InputValidator
from src.email_signature.infrastructure.file_service import FileSystemService
from src.email_signature.infrastructure.image_renderer import ImageRenderer
from src.email_signature.infrastructure.logo_loader import LogoLoader
from src.email_signature.interface.cli import CLI


def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main() -> None:
    """Main entry point for the email signature generator."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Check dependencies before proceeding
    from src.email_signature.infrastructure.platform_utils import DependencyChecker
    
    all_ok, errors = DependencyChecker.check_all_dependencies()
    if not all_ok:
        logger.error("Missing required dependencies")
        print("\nError: Missing required dependencies\n")
        for error in errors:
            print(error)
            print()
        sys.exit(1)

    try:
        logger.info("Starting Email Signature Generator")

        # Step 1: Load configuration
        logger.debug("Loading configuration")
        config_path = Path("config/default_config.yaml")

        if config_path.exists():
            config = ConfigLoader.load(str(config_path))
            logger.info(f"Configuration loaded from {config_path}")
        else:
            config = ConfigLoader.load(None)
            logger.info("Using default configuration")

        # Step 2: Initialize dependencies
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
            config=config
        )

        logger.info("All dependencies initialized successfully")

        # Step 3: Create CLI and collect user data
        cli = CLI(validator)
        cli.display_welcome()

        logger.debug("Collecting user data")
        signature_data = cli.collect_user_data()
        logger.info(f"User data collected for {signature_data.name}")

        # Step 4: Execute use case to generate signature
        output_path = "email_signature.png"
        logger.info(f"Generating signature to {output_path}")

        result_path = use_case.execute(signature_data, output_path)

        # Step 5: Display success message
        # Load the generated image to get dimensions
        from PIL import Image
        generated_image = Image.open(result_path)
        dimensions = generated_image.size
        generated_image.close()

        cli.display_success(result_path, dimensions)
        logger.info("Signature generation completed successfully")

    except LogoNotFoundError as e:
        logger.error(f"Logo not found: {e}")
        if 'cli' in locals():
            cli.display_error(str(e))
        else:
            print(f"\nError: {e}")
        sys.exit(1)

    except LogoLoadError as e:
        logger.error(f"Logo load error: {e}")
        if 'cli' in locals():
            cli.display_error(str(e))
        else:
            print(f"\nError: {e}")
        sys.exit(1)

    except ImageRenderError as e:
        logger.error(f"Image render error: {e}")
        if 'cli' in locals():
            cli.display_error(str(e))
        else:
            print(f"\nError: {e}")
        sys.exit(1)

    except FileSystemError as e:
        logger.error(f"File system error: {e}")
        if 'cli' in locals():
            cli.display_error(str(e))
        else:
            print(f"\nError: {e}")
        sys.exit(1)

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        if 'cli' in locals():
            cli.display_error(str(e))
        else:
            print(f"\nError: {e}")
        sys.exit(1)

    except SignatureGeneratorError as e:
        logger.error(f"Signature generator error: {e}")
        if 'cli' in locals():
            cli.display_error(f"An error occurred: {e}")
        else:
            print(f"\nError: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("\n\nOperation cancelled by user.")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        error_message = (
            f"An unexpected error occurred: {str(e)}\n"
            "Please check the logs for more details."
        )
        if 'cli' in locals():
            cli.display_error(error_message)
        else:
            print(f"\nError: {error_message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
