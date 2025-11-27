#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legacy email signature generator script.

⚠️  DEPRECATED: This script is maintained for backward compatibility only.
    Please use 'python main.py' for the new architecture-based implementation.
    
    This legacy wrapper will be removed in a future version.

This script generates professional email signatures as PNG images with
transparent backgrounds and outlined text for readability in both light
and dark mode email clients.
"""

import logging
import sys
from pathlib import Path

from src.email_signature.application.use_cases import GenerateSignatureUseCase
from src.email_signature.domain.config import ConfigLoader
from src.email_signature.domain.exceptions import (
    LogoNotFoundError,
    LogoLoadError,
    ImageRenderError,
    FileSystemError,
    ValidationError,
    SignatureGeneratorError,
)
from src.email_signature.domain.validators import InputValidator
from src.email_signature.infrastructure.file_service import FileSystemService
from src.email_signature.infrastructure.image_renderer import ImageRenderer
from src.email_signature.infrastructure.logo_loader import LogoLoader
from src.email_signature.interface.cli import CLI


def display_deprecation_notice() -> None:
    """Display deprecation notice to users."""
    print("\n" + "=" * 70)
    print("⚠️  DEPRECATION NOTICE")
    print("=" * 70)
    print("This script (email_signature_generator.py) is deprecated.")
    print("Please use 'python main.py' for the new implementation.")
    print("This legacy wrapper will be removed in a future version.")
    print("=" * 70 + "\n")


def main() -> None:
    """
    Legacy entry point that wraps the new architecture.
    
    This function maintains backward compatibility by using the same
    command-line behavior as the original script while leveraging
    the new clean architecture implementation.
    """
    # Display deprecation notice
    display_deprecation_notice()
    
    # Set up minimal logging (less verbose than main.py)
    logging.basicConfig(
        level=logging.WARNING,
        format='%(levelname)s: %(message)s'
    )
    logger = logging.getLogger(__name__)

    try:
        # Step 1: Load configuration
        config_path = Path("config/default_config.yaml")
        
        if config_path.exists():
            config = ConfigLoader.load(str(config_path))
        else:
            config = ConfigLoader.load(None)

        # Step 2: Initialize dependencies
        validator = InputValidator()
        logo_loader = LogoLoader(config.logo_search_paths)
        image_renderer = ImageRenderer(config)
        file_service = FileSystemService()
        
        use_case = GenerateSignatureUseCase(
            image_renderer=image_renderer,
            logo_loader=logo_loader,
            file_service=file_service,
            config=config
        )

        # Step 3: Create CLI and collect user data
        cli = CLI(validator)
        cli.display_welcome()
        
        signature_data = cli.collect_user_data()

        # Step 4: Execute use case to generate signature
        output_path = "email_signature.png"
        result_path = use_case.execute(signature_data, output_path)

        # Step 5: Display success message
        from PIL import Image
        generated_image = Image.open(result_path)
        dimensions = generated_image.size
        generated_image.close()

        cli.display_success(result_path, dimensions)

    except LogoNotFoundError as e:
        logger.error(f"Logo not found: {e}")
        if 'cli' in locals():
            cli.display_error(str(e))
        else:
            print(f"\n❌ Erro: {e}")
        sys.exit(1)

    except LogoLoadError as e:
        logger.error(f"Logo load error: {e}")
        if 'cli' in locals():
            cli.display_error(str(e))
        else:
            print(f"\n❌ Erro: {e}")
        sys.exit(1)

    except ImageRenderError as e:
        logger.error(f"Image render error: {e}")
        if 'cli' in locals():
            cli.display_error(str(e))
        else:
            print(f"\n❌ Erro: {e}")
        sys.exit(1)

    except FileSystemError as e:
        logger.error(f"File system error: {e}")
        if 'cli' in locals():
            cli.display_error(str(e))
        else:
            print(f"\n❌ Erro: {e}")
        sys.exit(1)

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        if 'cli' in locals():
            cli.display_error(str(e))
        else:
            print(f"\n❌ Erro: {e}")
        sys.exit(1)

    except SignatureGeneratorError as e:
        logger.error(f"Signature generator error: {e}")
        if 'cli' in locals():
            cli.display_error(f"An error occurred: {e}")
        else:
            print(f"\n❌ Erro: {e}")
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
            print(f"\n❌ Erro: {error_message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
