"""Logo loading and processing for email signature generation."""

from pathlib import Path
from typing import Any

from PIL import Image

from .platform_utils import PathManager, ErrorMessageFormatter


class LogoNotFoundError(Exception):
    """Raised when logo file cannot be found in any search path."""

    def __init__(self, search_paths: list[str]) -> None:
        """Initialize with searched paths.

        Args:
            search_paths: List of paths that were searched
        """
        # Normalize paths to use native separators
        native_paths = [str(PathManager.normalize(p)) for p in search_paths]
        paths_str = "\n  - ".join(native_paths)
        super().__init__(
            f"Logo file not found. Searched in the following locations:\n  - {paths_str}\n"
            f"Please place a logo file (PNG or JPG) in one of these locations."
        )
        self.search_paths = search_paths


class LogoLoadError(Exception):
    """Raised when logo file cannot be loaded or is corrupted."""

    def __init__(self, logo_path: str, original_error: Exception) -> None:
        """Initialize with path and original error.

        Args:
            logo_path: Path to the logo file that failed to load
            original_error: The original exception that occurred
        """
        path_obj = PathManager.normalize(logo_path)
        # Use ErrorMessageFormatter for platform-specific error messages
        formatted_error = ErrorMessageFormatter.format_path_error(path_obj, original_error)
        super().__init__(
            f"Failed to load logo:\n{formatted_error}\n"
            f"Please ensure the file is a valid PNG or JPG image."
        )
        self.logo_path = logo_path
        self.original_error = original_error


class LogoLoader:
    """Handles logo file loading and processing."""

    def __init__(self, search_paths: list[str]) -> None:
        """Initialize LogoLoader with search paths.

        Args:
            search_paths: List of file paths to search for logo
        """
        self.search_paths = search_paths

    def find_logo(self) -> str | None:
        """Search for logo file in configured paths.

        Returns:
            Path to logo file if found, None otherwise
        """
        for path_str in self.search_paths:
            path = PathManager.normalize(path_str)
            if PathManager.exists(path) and path.is_file():
                return str(path)
        return None

    def load_and_resize_logo(self, logo_path: str, target_height: int) -> Any:
        """Load logo and resize maintaining aspect ratio.

        Args:
            logo_path: Path to the logo file
            target_height: Target height in pixels

        Returns:
            Resized logo image in RGBA format

        Raises:
            LogoLoadError: If logo cannot be loaded or is corrupted
        """
        try:
            # Normalize path and load the image
            path = PathManager.normalize(logo_path)
            logo: Any = Image.open(str(path))

            # Convert to RGBA format
            if logo.mode != "RGBA":
                logo = logo.convert("RGBA")

            # Calculate new dimensions maintaining aspect ratio
            original_width, original_height = logo.size
            aspect_ratio = original_width / original_height
            target_width = int(target_height * aspect_ratio)

            # Ensure minimum width of 1 pixel
            target_width = max(1, target_width)

            # Resize the logo
            resized_logo = logo.resize((target_width, target_height), Image.Resampling.LANCZOS)

            return resized_logo

        except Exception as e:
            raise LogoLoadError(logo_path, e) from e
