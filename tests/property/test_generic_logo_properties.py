"""Property-based tests for generic logo generation.

Feature: data-sanitization
"""

import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st
from PIL import Image

from scripts.generate_generic_logo import create_generic_logo


# Strategy for generating valid logo sizes
logo_size = st.integers(min_value=50, max_value=500)


@given(size=logo_size)
@settings(deadline=None, max_examples=100)
def test_generic_logo_meets_design_criteria(size: int) -> None:
    """Feature: data-sanitization, Property 3: Generic logo meets design criteria.

    Validates: Requirements 1.4

    For any valid size parameter, the generated logo should:
    - Be a PNG file
    - Have RGBA mode (with transparency)
    - Have the specified dimensions (square)
    - Be loadable as a valid image
    """
    # Create a temporary file for the logo
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        logo_path = tmp_file.name

    try:
        # When generating a generic logo
        create_generic_logo(logo_path, size=size)

        # Then the file should exist
        assert Path(logo_path).exists()

        # And it should be a valid PNG image
        with Image.open(logo_path) as img:
            # Should be in RGBA mode (with transparency)
            assert img.mode == "RGBA", f"Expected RGBA mode, got {img.mode}"

            # Should have the correct dimensions (square)
            assert img.width == size, f"Expected width {size}, got {img.width}"
            assert img.height == size, f"Expected height {size}, got {img.height}"

            # Should have the PNG format
            assert img.format == "PNG", f"Expected PNG format, got {img.format}"

            # Verify the image has actual content (not all transparent)
            # Check that at least some pixels are not fully transparent
            pixels = list(img.getdata())
            non_transparent_pixels = [p for p in pixels if p[3] > 0]
            assert len(non_transparent_pixels) > 0, "Logo should have visible content"

    finally:
        # Clean up temporary file
        Path(logo_path).unlink(missing_ok=True)
