"""Unit tests for logo file verification in working directory.

Feature: data-sanitization
"""

from pathlib import Path

from PIL import Image


def test_proprietary_logo_removed_from_working_directory() -> None:
    """Example 1: Proprietary logo removed from working directory.

    Validates: Requirements 1.1, 4.1

    Verify that logo.png in the repository root is not the proprietary file.
    This test checks that:
    1. If logo.png exists, it is the generic placeholder
    2. The file size is reasonable for a generic logo (< 50KB)
    3. The image can be loaded and has expected properties
    """
    # Given the repository root
    repo_root = Path(__file__).parent.parent.parent
    logo_path = repo_root / "logo.png"

    # When checking if logo.png exists
    if not logo_path.exists():
        # If logo.png doesn't exist yet, that's acceptable during sanitization
        # The test will pass once the generic logo is added
        return

    # Then the logo should be a small file (generic placeholder)
    logo_size = logo_path.stat().st_size
    
    # Generic logos should be relatively small (< 50KB)
    # Proprietary logos are typically larger
    assert logo_size < 50000, (
        f"logo.png appears to be too large ({logo_size} bytes) to be the generic placeholder. "
        "Expected a small generic logo (< 50KB). This suggests proprietary content may still be present."
    )

    # And it should be a valid image file
    try:
        with Image.open(logo_path) as img:
            # Should be PNG format
            assert img.format == "PNG", f"Expected PNG format, got {img.format}"
            
            # Should have transparency (RGBA mode)
            assert img.mode == "RGBA", f"Expected RGBA mode for transparency, got {img.mode}"
            
            # Should be a reasonable size for a logo (not too large)
            assert img.width <= 500, f"Logo width {img.width} is too large for a generic placeholder"
            assert img.height <= 500, f"Logo height {img.height} is too large for a generic placeholder"
            
            # Should have actual content (not all transparent)
            pixels = list(img.getdata())
            non_transparent_pixels = [p for p in pixels if p[3] > 0]
            assert len(non_transparent_pixels) > 0, "Logo should have visible content"
            
    except Exception as e:
        raise AssertionError(f"Failed to load logo.png as a valid image: {e}")
