"""Property-based tests for file system operations."""

import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from PIL import Image

from src.email_signature.infrastructure.file_service import (
    FileSystemError,
    FileSystemService,
)

# Strategy for generating valid image dimensions
valid_dimension = st.integers(min_value=10, max_value=500)


@given(
    width=valid_dimension,
    height=valid_dimension,
)
@settings(deadline=None)
def test_graceful_file_operation_failures(width: int, height: int) -> None:
    """Feature: email-signature-refactor, Property 17: Graceful file operation failures.

    Validates: Requirements 12.2

    For any file operation failure (logo not found, cannot write output), the application
    should provide a clear, user-friendly error message indicating what failed and
    potential solutions.
    """
    # Create a test image
    test_image = Image.new("RGBA", (width, height), color=(255, 0, 0, 128))

    # Test 1: Attempt to save to an invalid/inaccessible path
    # Use a path that is guaranteed to fail (e.g., root directory without permissions)
    invalid_path = "/root/cannot_write_here/test_signature.png"

    # When attempting to save to an invalid path
    with pytest.raises(FileSystemError) as exc_info:
        FileSystemService.save_image(test_image, invalid_path)

    # Then the error should be a FileSystemError
    error = exc_info.value

    # And the error message should be clear and informative
    assert "Failed to save file" in str(error)
    assert invalid_path in str(error)

    # And the error should contain the operation type
    assert error.operation == "save"
    assert error.path == invalid_path

    # And the error should have the original exception for debugging
    assert error.original_error is not None


@given(
    width=valid_dimension,
    height=valid_dimension,
)
@settings(deadline=None)
def test_successful_save_creates_file(width: int, height: int) -> None:
    """Test that successful save operations create accessible files.

    For any valid image and writable path, the FileSystemService should
    successfully save the image and the file should exist afterward.
    """
    # Create a test image
    test_image = Image.new("RGBA", (width, height), color=(0, 255, 0, 200))

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = str(Path(tmp_dir) / "test_signature.png")

        # When saving the image
        FileSystemService.save_image(test_image, output_path)

        # Then the file should exist
        assert FileSystemService.file_exists(output_path)

        # And the file should be readable as a valid PNG
        loaded_image = Image.open(output_path)
        assert loaded_image.mode == "RGBA"
        assert loaded_image.size == (width, height)


@given(
    width=valid_dimension,
    height=valid_dimension,
)
@settings(deadline=None)
def test_save_creates_parent_directories(width: int, height: int) -> None:
    """Test that save operation creates parent directories if they don't exist.

    For any valid image and path with non-existent parent directories,
    the FileSystemService should create the necessary directories.
    """
    # Create a test image
    test_image = Image.new("RGBA", (width, height), color=(0, 0, 255, 150))

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a path with nested non-existent directories
        output_path = str(Path(tmp_dir) / "nested" / "directories" / "test_signature.png")

        # When saving the image
        FileSystemService.save_image(test_image, output_path)

        # Then the file should exist
        assert FileSystemService.file_exists(output_path)

        # And all parent directories should have been created
        assert Path(output_path).parent.exists()
