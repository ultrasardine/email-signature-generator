"""
Custom exception hierarchy for the email signature generator.

This module defines all custom exceptions used throughout the application,
providing clear error messages and proper exception hierarchy.
"""

from pathlib import Path
from typing import List


class SignatureGeneratorError(Exception):
    """
    Base exception for all signature generator errors.

    All custom exceptions in the application inherit from this base class,
    allowing for easy catching of all application-specific errors.
    """

    def __init__(self, message: str = "An error occurred in the signature generator"):
        self.message = message
        super().__init__(self.message)


class ValidationError(SignatureGeneratorError):
    """
    Raised when input validation fails.

    This exception is raised when user-provided data does not meet
    validation requirements (e.g., invalid email format, empty required fields).

    Attributes:
        field_name: The name of the field that failed validation
        invalid_value: The value that failed validation
        message: Detailed error message with guidance
    """

    def __init__(self, field_name: str, invalid_value: str, message: str):
        self.field_name = field_name
        self.invalid_value = invalid_value
        full_message = f"Validation failed for field '{field_name}': {message}"
        super().__init__(full_message)


class LogoNotFoundError(SignatureGeneratorError):
    """
    Raised when the logo file cannot be found in any configured location.

    This exception provides information about all locations that were searched,
    helping users understand where to place their logo file.

    Attributes:
        searched_paths: List of paths that were searched for the logo
    """

    def __init__(self, searched_paths: list[str]):
        from ..infrastructure.platform_utils import PathManager
        
        self.searched_paths = searched_paths
        # Normalize paths to use native separators
        native_paths = [str(PathManager.normalize(p)) for p in searched_paths]
        paths_str = "\n  - ".join(native_paths)
        message = (
            f"Logo file not found. Searched the following locations:\n  - {paths_str}\n"
            f"Please place a logo file (PNG or JPG) in one of these locations."
        )
        super().__init__(message)


class LogoLoadError(SignatureGeneratorError):
    """
    Raised when a logo file is found but cannot be loaded or processed.

    This exception indicates issues like corrupted files, unsupported formats,
    or other problems that prevent the logo from being loaded.

    Attributes:
        logo_path: Path to the logo file that failed to load
        reason: Specific reason for the failure
    """

    def __init__(self, logo_path: str, reason: str):
        from ..infrastructure.platform_utils import PathManager
        
        self.logo_path = logo_path
        self.reason = reason
        # Use native path separators
        native_path = str(PathManager.normalize(logo_path))
        message = (
            f"Failed to load logo from '{native_path}': {reason}\n"
            f"Please ensure the file is a valid PNG or JPG image."
        )
        super().__init__(message)


class ImageRenderError(SignatureGeneratorError):
    """
    Raised when image rendering or creation fails.

    This exception covers errors during the signature image generation process,
    such as font loading failures, text rendering issues, or image composition problems.

    Attributes:
        operation: The rendering operation that failed
        reason: Specific reason for the failure
    """

    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        message = (
            f"Image rendering failed during '{operation}': {reason}\n"
            f"Please check your configuration and try again."
        )
        super().__init__(message)


class FileSystemError(SignatureGeneratorError):
    """
    Raised when file system operations fail.

    This exception covers errors like inability to write output files,
    permission issues, or disk space problems.

    Attributes:
        operation: The file operation that failed (e.g., 'save', 'read')
        file_path: Path to the file involved in the operation
        reason: Specific reason for the failure
    """

    def __init__(self, operation: str, file_path: str, reason: str | Exception):
        from ..infrastructure.platform_utils import PathManager, ErrorMessageFormatter
        
        self.operation = operation
        self.file_path = file_path
        self.reason = reason
        
        # Use native path separators
        path_obj = PathManager.normalize(file_path)
        
        # If reason is an Exception, use ErrorMessageFormatter
        if isinstance(reason, Exception):
            formatted_error = ErrorMessageFormatter.format_path_error(path_obj, reason)
            message = f"File system operation '{operation}' failed:\n{formatted_error}"
        else:
            native_path = str(path_obj)
            message = (
                f"File system operation '{operation}' failed for '{native_path}': {reason}\n"
                f"Please check file permissions and available disk space."
            )
        super().__init__(message)
