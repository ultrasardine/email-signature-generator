"""File system operations for email signature generation."""

from pathlib import Path

from PIL import Image

from .platform_utils import PathManager, ErrorMessageFormatter


class FileSystemError(Exception):
    """Raised when file operations fail."""

    def __init__(self, operation: str, path: str, original_error: Exception | None = None) -> None:
        """Initialize with operation details.

        Args:
            operation: The operation that failed (e.g., "save", "read")
            path: Path where the operation failed
            original_error: The original exception if any
        """
        path_obj = PathManager.normalize(path)
        
        if original_error:
            # Use ErrorMessageFormatter for platform-specific error messages
            formatted_error = ErrorMessageFormatter.format_path_error(path_obj, original_error)
            message = f"Failed to {operation} file:\n{formatted_error}"
        else:
            native_path = str(path_obj)
            message = f"Failed to {operation} file at '{native_path}'"

        super().__init__(message)
        self.operation = operation
        self.path = path
        self.original_error = original_error


class FileSystemService:
    """Handles file system operations."""

    @staticmethod
    def save_image(image: Image.Image, path: str) -> None:
        """Save image to disk.

        Args:
            image: PIL Image object to save
            path: Destination file path

        Raises:
            FileSystemError: If the image cannot be saved
        """
        try:
            # Normalize path and ensure parent directory exists
            path_obj = PathManager.normalize(path)
            PathManager.ensure_parent_dirs(path_obj)

            # Save the image
            image.save(str(path_obj), format="PNG")

        except Exception as e:
            raise FileSystemError("save", path, e) from e

    @staticmethod
    def file_exists(path: str) -> bool:
        """Check if file exists.

        Args:
            path: File path to check

        Returns:
            True if file exists, False otherwise
        """
        path_obj = PathManager.normalize(path)
        return PathManager.exists(path_obj)
