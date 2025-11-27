"""Unit tests for logo loading functionality."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from src.email_signature.infrastructure.logo_loader import (
    LogoLoader,
    LogoLoadError,
    LogoNotFoundError,
)


def test_logo_not_found_error_includes_searched_paths() -> None:
    """Test that LogoNotFoundError includes all searched paths in error message.

    Validates: Requirements 5.4

    When logo cannot be found in any of the configured search paths,
    the error message should include all paths that were searched.
    """
    # Given a LogoLoader with multiple search paths that don't exist
    search_paths = [
        "nonexistent_logo.png",
        "./logos/missing.jpg",
        "/tmp/not_here.png",
    ]
    loader = LogoLoader(search_paths)

    # When trying to find a logo that doesn't exist
    result = loader.find_logo()

    # Then it should return None
    assert result is None

    # And when we create a LogoNotFoundError with these paths
    error = LogoNotFoundError(search_paths)
    error_message = str(error)

    # Then the error message should include all searched paths (normalized)
    from src.email_signature.infrastructure.platform_utils import PathManager
    for path in search_paths:
        # Check for normalized path in error message
        normalized_path = str(PathManager.normalize(path))
        assert normalized_path in error_message

    # And should mention that the logo was not found
    assert "not found" in error_message.lower()
    assert "searched" in error_message.lower()


def test_logo_found_returns_path() -> None:
    """Test that find_logo returns the path when logo exists."""
    # Create a temporary logo file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        logo_path = tmp_file.name
        test_image = Image.new("RGB", (100, 100), color="red")
        test_image.save(logo_path, "PNG")

    try:
        # Given a LogoLoader with the path to the existing file
        loader = LogoLoader([logo_path])

        # When finding the logo
        result = loader.find_logo()

        # Then it should return the path
        assert result == logo_path

    finally:
        # Clean up
        Path(logo_path).unlink(missing_ok=True)


def test_logo_found_returns_first_existing_path() -> None:
    """Test that find_logo returns the first existing path when multiple exist."""
    # Create two temporary logo files
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file1:
        logo_path1 = tmp_file1.name
        test_image1 = Image.new("RGB", (100, 100), color="red")
        test_image1.save(logo_path1, "PNG")

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file2:
        logo_path2 = tmp_file2.name
        test_image2 = Image.new("RGB", (100, 100), color="blue")
        test_image2.save(logo_path2, "JPEG")

    try:
        # Given a LogoLoader with multiple paths, some non-existent
        search_paths = [
            "nonexistent.png",
            logo_path1,
            logo_path2,
        ]
        loader = LogoLoader(search_paths)

        # When finding the logo
        result = loader.find_logo()

        # Then it should return the first existing path
        assert result == logo_path1

    finally:
        # Clean up
        Path(logo_path1).unlink(missing_ok=True)
        Path(logo_path2).unlink(missing_ok=True)


def test_corrupted_logo_raises_logo_load_error() -> None:
    """Test that corrupted logo files raise LogoLoadError with helpful message."""
    # Create a temporary file with invalid image data
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False, mode="w") as tmp_file:
        logo_path = tmp_file.name
        tmp_file.write("This is not a valid image file")

    try:
        # Given a LogoLoader
        loader = LogoLoader([logo_path])

        # When trying to load a corrupted logo
        with pytest.raises(LogoLoadError) as exc_info:
            loader.load_and_resize_logo(logo_path, 70)

        # Then the error should include the logo path
        error_message = str(exc_info.value)
        assert logo_path in error_message

        # And should indicate it failed to load
        assert "failed" in error_message.lower() or "load" in error_message.lower()

    finally:
        # Clean up
        Path(logo_path).unlink(missing_ok=True)
