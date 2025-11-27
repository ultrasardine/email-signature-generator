"""Property-based tests for logo loading and processing."""

import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st
from PIL import Image

from src.email_signature.infrastructure.logo_loader import (
    LogoLoader,
)

# Strategy for generating valid image dimensions
valid_dimension = st.integers(min_value=10, max_value=1000)

# Strategy for generating target heights for resizing
target_height = st.integers(min_value=20, max_value=500)


@given(
    original_width=valid_dimension,
    original_height=valid_dimension,
    target_height=target_height,
)
@settings(deadline=None)
def test_logo_aspect_ratio_preservation(
    original_width: int, original_height: int, target_height: int
) -> None:
    """Feature: email-signature-refactor, Property 7: Logo aspect ratio preservation.

    Validates: Requirements 5.3

    For any logo image with width W and height H, after resizing to target height T,
    the resulting logo should have width (W/H) * T (within 1 pixel tolerance),
    preserving the original aspect ratio.
    """
    # Create a temporary logo image with random dimensions
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        logo_path = tmp_file.name

        # Create test image with specific dimensions
        test_image = Image.new("RGB", (original_width, original_height), color="red")
        test_image.save(logo_path, "PNG")

    try:
        # When loading and resizing the logo
        loader = LogoLoader([logo_path])
        resized_logo = loader.load_and_resize_logo(logo_path, target_height)

        # Then the height should match target
        assert resized_logo.height == target_height

        # And the width should preserve aspect ratio (within 1 pixel tolerance for rounding)
        expected_aspect_ratio = original_width / original_height
        expected_width = int(target_height * expected_aspect_ratio)
        assert abs(resized_logo.width - expected_width) <= 1

    finally:
        # Clean up temporary file
        Path(logo_path).unlink(missing_ok=True)


@given(
    width=valid_dimension,
    height=valid_dimension,
    image_format=st.sampled_from(["PNG", "JPEG"]),
    target_height=target_height,
)
@settings(deadline=None)
def test_logo_format_conversion(
    width: int, height: int, image_format: str, target_height: int
) -> None:
    """Feature: email-signature-refactor, Property 8: Logo format conversion.

    Validates: Requirements 5.2

    For any logo file in supported formats (PNG, JPG), the LogoLoader should
    successfully load and convert it to RGBA format.
    """
    # Create a temporary logo image in the specified format
    suffix = ".png" if image_format == "PNG" else ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        logo_path = tmp_file.name

        # Create test image
        mode = "RGB" if image_format == "JPEG" else "RGBA"
        test_image = Image.new(mode, (width, height), color="blue")
        test_image.save(logo_path, image_format)

    try:
        # When loading and resizing the logo
        loader = LogoLoader([logo_path])
        resized_logo = loader.load_and_resize_logo(logo_path, target_height)

        # Then the logo should be converted to RGBA format
        assert resized_logo.mode == "RGBA"

        # And should have the correct dimensions
        assert resized_logo.height == target_height

    finally:
        # Clean up temporary file
        Path(logo_path).unlink(missing_ok=True)
