"""Use cases for email signature generation."""

import logging

from ..domain.config import SignatureConfig
from ..domain.exceptions import (
    FileSystemError,
    ImageRenderError,
    LogoLoadError,
    LogoNotFoundError,
    SignatureGeneratorError,
)
from ..domain.models import SignatureData
from ..infrastructure.file_service import FileSystemService
from ..infrastructure.image_renderer import ImageRenderer
from ..infrastructure.logo_loader import LogoLoader

logger = logging.getLogger(__name__)


class GenerateSignatureUseCase:
    """Orchestrates the signature generation process."""

    def __init__(
        self,
        image_renderer: ImageRenderer,
        logo_loader: LogoLoader,
        file_service: FileSystemService,
        config: SignatureConfig,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            image_renderer: Service for rendering signature images
            logo_loader: Service for loading and processing logos
            file_service: Service for file system operations
            config: Configuration for signature generation
        """
        self.image_renderer = image_renderer
        self.logo_loader = logo_loader
        self.file_service = file_service
        self.config = config
        logger.info("GenerateSignatureUseCase initialized")

    def execute(self, signature_data: SignatureData, output_path: str) -> str:
        """Generate email signature image.

        This method orchestrates the complete signature generation process:
        1. Find and load the logo
        2. Create the signature image with user data
        3. Save the image to the specified path

        Args:
            signature_data: User data for the signature
            output_path: Path where the signature image should be saved

        Returns:
            Path to the generated signature file

        Raises:
            LogoNotFoundError: If logo file cannot be found
            LogoLoadError: If logo file cannot be loaded
            ImageRenderError: If image rendering fails
            FileSystemError: If file cannot be saved
            SignatureGeneratorError: For other unexpected errors
        """
        try:
            logger.info(f"Starting signature generation for {signature_data.name}")

            # Step 1: Find logo file
            logger.debug("Searching for logo file")
            logo_path = self.logo_loader.find_logo()

            if logo_path is None:
                logger.error("Logo file not found in any search path")
                raise LogoNotFoundError(self.logo_loader.search_paths)

            logger.info(f"Logo found at: {logo_path}")

            # Step 2: Load and resize logo
            logger.debug(f"Loading and resizing logo to height {self.config.logo_height}")
            try:
                logo = self.logo_loader.load_and_resize_logo(logo_path, self.config.logo_height)
                logger.info("Logo loaded and resized successfully")
            except LogoLoadError as e:
                logger.error(f"Failed to load logo: {e}")
                raise

            # Step 3: Create signature image
            logger.debug("Rendering signature image")
            try:
                signature_image = self.image_renderer.create_signature_image(signature_data, logo)
                logger.info(f"Signature image created with dimensions {signature_image.size}")
            except Exception as e:
                logger.error(f"Failed to render signature image: {e}")
                # Wrap in ImageRenderError if not already
                if isinstance(e, ImageRenderError):
                    raise
                raise ImageRenderError("image creation", str(e)) from e

            # Step 4: Save image to disk
            logger.debug(f"Saving signature image to {output_path}")
            try:
                self.file_service.save_image(signature_image, output_path)
                logger.info(f"Signature saved successfully to {output_path}")
            except FileSystemError as e:
                logger.error(f"Failed to save signature: {e}")
                raise

            logger.info("Signature generation completed successfully")
            return output_path

        except (LogoNotFoundError, LogoLoadError, ImageRenderError, FileSystemError):
            # Re-raise known exceptions
            raise
        except Exception as e:
            # Catch any unexpected errors
            logger.error(f"Unexpected error during signature generation: {e}", exc_info=True)
            raise SignatureGeneratorError(
                f"Unexpected error during signature generation: {str(e)}"
            ) from e
