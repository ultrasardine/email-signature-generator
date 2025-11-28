"""Preview generator for signature images."""

import logging

from PIL import Image

from ...application.use_cases import GenerateSignatureUseCase
from ...domain.models import SignatureData
from ...infrastructure.platform_utils import TempFileManager

logger = logging.getLogger(__name__)


class PreviewGenerator:
    """Generates temporary preview images for signature display in GUI."""

    def __init__(self, use_case: GenerateSignatureUseCase) -> None:
        """Initialize preview generator with use case.

        Args:
            use_case: The signature generation use case to use for creating previews
        """
        self.use_case = use_case
        logger.info("PreviewGenerator initialized")

    def generate_preview(
        self, data: SignatureData, logo_path: str | None = None
    ) -> Image.Image:
        """Generate a preview image for the signature.

        Creates a temporary signature image file and returns it as a PIL Image
        for display in the GUI. The temporary file is tracked for cleanup.

        Args:
            data: Signature data to generate preview for
            logo_path: Optional custom logo path to use instead of default

        Returns:
            PIL Image object containing the signature preview

        Raises:
            Exception: If preview generation fails (propagates from use case)
        """
        logger.debug(f"Generating preview for {data.name}")

        # Create temporary file for preview using TempFileManager
        temp_path = TempFileManager.create_temp_file(suffix=".png", prefix="signature_preview_")
        logger.debug(f"Created temporary file: {temp_path}")

        try:
            # If custom logo path provided, temporarily override logo loader
            if logo_path:
                original_paths = self.use_case.logo_loader.search_paths
                self.use_case.logo_loader.search_paths = [logo_path]
                try:
                    self.use_case.execute(data, str(temp_path))
                finally:
                    self.use_case.logo_loader.search_paths = original_paths
            else:
                self.use_case.execute(data, str(temp_path))
            logger.info(f"Preview generated successfully at {temp_path}")

            # Load and return as PIL Image
            preview_image = Image.open(temp_path)
            logger.debug(f"Preview image loaded with size {preview_image.size}")
            return preview_image

        except Exception as e:
            logger.error(f"Failed to generate preview: {e}")
            # Clean up the failed temp file
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception as cleanup_error:
                    logger.warning(f"Failed to remove temporary file {temp_path}: {cleanup_error}")
            raise

    def cleanup(self) -> None:
        """Clean up all temporary preview files.

        Removes all temporary files created during preview generation.
        Safe to call multiple times.
        """
        # Get count of tracked files before cleanup
        tracked_files = TempFileManager.get_tracked_files()
        preview_files = [f for f in tracked_files if f.name.startswith("signature_preview_")]

        logger.info(f"Cleaning up {len(preview_files)} temporary preview files")

        # Clean up only preview files (those with signature_preview_ prefix)
        TempFileManager.cleanup_temp_files(pattern="signature_preview_*")

        logger.info("Cleanup completed")
