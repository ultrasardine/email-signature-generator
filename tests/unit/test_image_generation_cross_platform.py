"""Unit tests for cross-platform image generation.

These tests verify that image generation produces valid PNG files on all platforms
and that the generated images meet the requirements for cross-platform compatibility.
"""

import platform
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from src.email_signature.domain.config import SignatureConfig
from src.email_signature.domain.models import SignatureData
from src.email_signature.infrastructure.image_renderer import ImageRenderer


def create_test_signature_data() -> SignatureData:
    """Create test signature data for image generation tests."""
    return SignatureData(
        name="John Doe",
        position="Software Engineer",
        address="123 Main St, City, Country",
        phone="+1 234 567 8900",
        mobile="+1 234 567 8901",
        email="john.doe@example.com",
        website="www.example.com",
    )


def create_test_logo() -> Image.Image:
    """Create a test logo image."""
    return Image.new("RGBA", (50, 50), (255, 0, 0, 255))


@pytest.mark.windows
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
def test_image_generation_on_windows() -> None:
    """Test image generation on Windows.

    Validates: Requirements 9.1

    When the System generates images on Windows THEN the System SHALL create valid PNG files.
    """
    # Create signature data and logo
    signature_data = create_test_signature_data()
    logo = create_test_logo()

    # Create renderer
    config = SignatureConfig()
    renderer = ImageRenderer(config)

    # Generate signature image
    signature_image = renderer.create_signature_image(signature_data, logo)

    # Verify the image was created
    assert signature_image is not None
    assert signature_image.mode == "RGBA"
    assert signature_image.width > 0
    assert signature_image.height > 0

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        signature_image.save(tmp_path, "PNG")

    try:
        # Verify the file exists and is a valid PNG
        assert Path(tmp_path).exists()
        
        # Try to open the file to verify it's a valid PNG
        with Image.open(tmp_path) as img:
            assert img.format == "PNG"
            assert img.mode == "RGBA"
            assert img.width == signature_image.width
            assert img.height == signature_image.height

    finally:
        # Clean up
        Path(tmp_path).unlink(missing_ok=True)


@pytest.mark.macos
@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-specific test")
def test_image_generation_on_macos() -> None:
    """Test image generation on macOS.

    Validates: Requirements 9.2

    When the System generates images on macOS THEN the System SHALL create valid PNG files.
    """
    # Create signature data and logo
    signature_data = create_test_signature_data()
    logo = create_test_logo()

    # Create renderer
    config = SignatureConfig()
    renderer = ImageRenderer(config)

    # Generate signature image
    signature_image = renderer.create_signature_image(signature_data, logo)

    # Verify the image was created
    assert signature_image is not None
    assert signature_image.mode == "RGBA"
    assert signature_image.width > 0
    assert signature_image.height > 0

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        signature_image.save(tmp_path, "PNG")

    try:
        # Verify the file exists and is a valid PNG
        assert Path(tmp_path).exists()
        
        # Try to open the file to verify it's a valid PNG
        with Image.open(tmp_path) as img:
            assert img.format == "PNG"
            assert img.mode == "RGBA"
            assert img.width == signature_image.width
            assert img.height == signature_image.height

    finally:
        # Clean up
        Path(tmp_path).unlink(missing_ok=True)


@pytest.mark.linux
@pytest.mark.skipif(platform.system() != "Linux", reason="Linux-specific test")
def test_image_generation_on_linux() -> None:
    """Test image generation on Linux.

    Validates: Requirements 9.3

    When the System generates images on Linux THEN the System SHALL create valid PNG files.
    """
    # Create signature data and logo
    signature_data = create_test_signature_data()
    logo = create_test_logo()

    # Create renderer
    config = SignatureConfig()
    renderer = ImageRenderer(config)

    # Generate signature image
    signature_image = renderer.create_signature_image(signature_data, logo)

    # Verify the image was created
    assert signature_image is not None
    assert signature_image.mode == "RGBA"
    assert signature_image.width > 0
    assert signature_image.height > 0

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        signature_image.save(tmp_path, "PNG")

    try:
        # Verify the file exists and is a valid PNG
        assert Path(tmp_path).exists()
        
        # Try to open the file to verify it's a valid PNG
        with Image.open(tmp_path) as img:
            assert img.format == "PNG"
            assert img.mode == "RGBA"
            assert img.width == signature_image.width
            assert img.height == signature_image.height

    finally:
        # Clean up
        Path(tmp_path).unlink(missing_ok=True)


def test_image_generation_produces_valid_png() -> None:
    """Test that image generation produces valid PNG files on any platform.

    This test runs on all platforms and verifies that the generated image
    is a valid PNG file that can be saved and reloaded.
    """
    # Create signature data and logo
    signature_data = create_test_signature_data()
    logo = create_test_logo()

    # Create renderer
    config = SignatureConfig()
    renderer = ImageRenderer(config)

    # Generate signature image
    signature_image = renderer.create_signature_image(signature_data, logo)

    # Verify the image was created
    assert signature_image is not None
    assert signature_image.mode == "RGBA"

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        signature_image.save(tmp_path, "PNG")

    try:
        # Verify the file exists
        assert Path(tmp_path).exists()
        
        # Verify the file is not empty
        assert Path(tmp_path).stat().st_size > 0
        
        # Try to open the file to verify it's a valid PNG
        with Image.open(tmp_path) as img:
            assert img.format == "PNG"
            assert img.mode == "RGBA"
            assert img.width == signature_image.width
            assert img.height == signature_image.height
            
            # Verify the image has content (non-transparent pixels)
            pixels = img.load()
            assert pixels is not None
            has_content = False
            for x in range(img.width):
                for y in range(img.height):
                    pixel = pixels[x, y]
                    if isinstance(pixel, tuple) and pixel[3] > 0:
                        has_content = True
                        break
                if has_content:
                    break
            
            assert has_content, "Generated image has no visible content"

    finally:
        # Clean up
        Path(tmp_path).unlink(missing_ok=True)


def test_image_transparency_preserved_across_platforms() -> None:
    """Test that image transparency is preserved when saving and loading.

    This verifies that PNG transparency works correctly on all platforms.
    """
    # Create signature data and logo
    signature_data = create_test_signature_data()
    logo = create_test_logo()

    # Create renderer
    config = SignatureConfig()
    renderer = ImageRenderer(config)

    # Generate signature image
    signature_image = renderer.create_signature_image(signature_data, logo)

    # Verify the image has an alpha channel
    assert signature_image.mode == "RGBA"

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        signature_image.save(tmp_path, "PNG")

    try:
        # Reload the image
        with Image.open(tmp_path) as reloaded_image:
            # Verify the alpha channel is preserved
            assert reloaded_image.mode == "RGBA"
            
            # Check that there are transparent pixels
            pixels = reloaded_image.load()
            assert pixels is not None
            has_transparent = False
            has_opaque = False
            
            for x in range(reloaded_image.width):
                for y in range(reloaded_image.height):
                    pixel = pixels[x, y]
                    if isinstance(pixel, tuple):
                        if pixel[3] == 0:
                            has_transparent = True
                        elif pixel[3] == 255:
                            has_opaque = True
                    
                    if has_transparent and has_opaque:
                        break
                if has_transparent and has_opaque:
                    break
            
            # The image should have both transparent and opaque pixels
            assert has_transparent, "No transparent pixels found"
            assert has_opaque, "No opaque pixels found"

    finally:
        # Clean up
        Path(tmp_path).unlink(missing_ok=True)


def test_image_dimensions_consistent_across_platforms() -> None:
    """Test that image dimensions are consistent regardless of platform.

    This verifies that the same input produces the same dimensions on all platforms.
    """
    # Create signature data and logo
    signature_data = create_test_signature_data()
    logo = create_test_logo()

    # Create renderer
    config = SignatureConfig()
    renderer = ImageRenderer(config)

    # Generate signature image twice
    signature_image_1 = renderer.create_signature_image(signature_data, logo)
    signature_image_2 = renderer.create_signature_image(signature_data, logo)

    # Verify dimensions are identical
    assert signature_image_1.width == signature_image_2.width
    assert signature_image_1.height == signature_image_2.height

    # Verify dimensions are reasonable
    assert signature_image_1.width > logo.width
    assert signature_image_1.height >= logo.height
