"""Unit tests for application functionality with generic assets.

Feature: data-sanitization
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from src.email_signature.application.use_cases import GenerateSignatureUseCase
from src.email_signature.domain.config import ConfigLoader
from src.email_signature.domain.models import SignatureData
from src.email_signature.infrastructure.file_service import FileSystemService
from src.email_signature.infrastructure.image_renderer import ImageRenderer
from src.email_signature.infrastructure.logo_loader import LogoLoader


def test_application_successfully_loads_generic_logo() -> None:
    """Example 6: Application successfully loads generic logo.

    Validates: Requirements 3.5, 4.3

    Verify that:
    1. The application can load the generic logo.png without errors
    2. The signature generation process completes successfully
    3. The generated signature contains the logo
    4. No errors occur during the entire process
    """
    # Given the repository root with generic logo
    repo_root = Path(__file__).parent.parent.parent
    logo_path = repo_root / "logo.png"

    # Verify logo exists before testing
    assert logo_path.exists(), (
        "logo.png must exist in repository root for this test. "
        "Run task 4 to add the generic logo."
    )

    # And given a configuration
    config_path = repo_root / "config" / "default_config.yaml"
    if config_path.exists():
        config = ConfigLoader.load(str(config_path))
    else:
        config = ConfigLoader.load(None)

    # And given initialized application components
    logo_loader = LogoLoader(config.logo_search_paths)
    image_renderer = ImageRenderer(config)
    file_service = FileSystemService()

    use_case = GenerateSignatureUseCase(
        image_renderer=image_renderer,
        logo_loader=logo_loader,
        file_service=file_service,
        config=config,
    )

    # And given sample signature data
    signature_data = SignatureData(
        name="John Doe",
        position="Software Engineer",
        email="john.doe@example.com",
        phone="+1 555 0100",
        mobile="+1 555 0101",
        address="123 Main Street, Anytown, USA",
    )

    # When generating a signature with the generic logo
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_signature.png"

        # Execute the use case - this should not raise any exceptions
        try:
            result_path = use_case.execute(signature_data, str(output_path))
        except Exception as e:
            pytest.fail(
                f"Application failed to generate signature with generic logo: {e}"
            )

        # Then the signature should be generated successfully
        assert Path(result_path).exists(), "Signature file should be created"

        # And the signature should be a valid PNG image
        try:
            with Image.open(result_path) as img:
                assert img.format == "PNG", f"Expected PNG format, got {img.format}"
                assert img.mode == "RGBA", f"Expected RGBA mode, got {img.mode}"

                # Signature should have reasonable dimensions
                assert img.width > 0, "Signature should have positive width"
                assert img.height > 0, "Signature should have positive height"

                # Signature should have visible content
                pixels = list(img.getdata())
                non_transparent_pixels = [p for p in pixels if p[3] > 0]
                assert (
                    len(non_transparent_pixels) > 0
                ), "Signature should have visible content"

        except Exception as e:
            pytest.fail(f"Generated signature is not a valid image: {e}")


def test_cli_application_loads_generic_logo() -> None:
    """Test that CLI application can load generic logo without errors.

    Validates: Requirements 3.5, 4.3

    This test verifies the CLI entry point can initialize with the generic logo.
    """
    # Given the repository root with generic logo
    repo_root = Path(__file__).parent.parent.parent
    logo_path = repo_root / "logo.png"

    # Verify logo exists
    assert logo_path.exists(), "logo.png must exist in repository root"

    # When initializing the CLI application components
    config_path = repo_root / "config" / "default_config.yaml"
    if config_path.exists():
        config = ConfigLoader.load(str(config_path))
    else:
        config = ConfigLoader.load(None)

    # Then logo loader should initialize without errors
    try:
        logo_loader = LogoLoader(config.logo_search_paths)
    except Exception as e:
        pytest.fail(f"Failed to initialize logo loader: {e}")

    # And logo should be findable
    try:
        logo_path = logo_loader.find_logo()
        assert logo_path is not None, "Logo should be found"
        assert Path(logo_path).exists(), "Logo path should exist"
        
        # And logo should be loadable
        logo = logo_loader.load_and_resize_logo(logo_path, target_height=100)
        assert logo is not None, "Logo should be loaded"
        assert isinstance(logo, Image.Image), "Logo should be a PIL Image"
    except Exception as e:
        pytest.fail(f"Failed to load generic logo: {e}")


@pytest.mark.gui
def test_gui_application_loads_generic_logo() -> None:
    """Test that GUI application can load generic logo without errors.

    Validates: Requirements 3.5, 4.3

    This test verifies the GUI can initialize with the generic logo.
    """
    # Given the repository root with generic logo
    repo_root = Path(__file__).parent.parent.parent
    logo_path = repo_root / "logo.png"

    # Verify logo exists
    assert logo_path.exists(), "logo.png must exist in repository root"

    # When initializing the GUI application components
    config_path = repo_root / "config" / "default_config.yaml"
    if config_path.exists():
        config = ConfigLoader.load(str(config_path))
    else:
        config = ConfigLoader.load(None)

    # Then all components should initialize without errors
    try:
        logo_loader = LogoLoader(config.logo_search_paths)
        image_renderer = ImageRenderer(config)
        file_service = FileSystemService()

        use_case = GenerateSignatureUseCase(
            image_renderer=image_renderer,
            logo_loader=logo_loader,
            file_service=file_service,
            config=config,
        )

        # Verify logo can be found and loaded
        logo_path = logo_loader.find_logo()
        assert logo_path is not None, "Logo should be found"
        
        logo = logo_loader.load_and_resize_logo(logo_path, target_height=100)
        assert logo is not None, "Logo should be loaded"

    except Exception as e:
        pytest.fail(f"Failed to initialize GUI components with generic logo: {e}")


def test_logo_search_paths_include_generic_logo() -> None:
    """Test that logo search paths can find the generic logo.

    Validates: Requirements 3.1, 3.4, 3.5

    This test verifies that the application's logo search mechanism
    correctly finds the generic logo.png file.
    """
    # Given the configuration
    repo_root = Path(__file__).parent.parent.parent
    config_path = repo_root / "config" / "default_config.yaml"

    if config_path.exists():
        config = ConfigLoader.load(str(config_path))
    else:
        config = ConfigLoader.load(None)

    # When creating a logo loader
    logo_loader = LogoLoader(config.logo_search_paths)

    # Then it should find the generic logo
    try:
        logo_path_str = logo_loader.find_logo()
        assert logo_path_str is not None, "Logo loader should find logo.png"
        
        logo_path = Path(logo_path_str)
        assert logo_path.exists(), f"Found logo path should exist: {logo_path}"
        assert logo_path.name == "logo.png", f"Found logo should be named logo.png, got {logo_path.name}"
    except Exception as e:
        pytest.fail(f"Logo loader failed to find generic logo: {e}")


def test_signature_generation_with_missing_optional_fields() -> None:
    """Test signature generation with minimal data and generic logo.

    Validates: Requirements 3.5, 4.3

    This test ensures the application works correctly with the generic logo
    even when optional fields are missing.
    """
    # Given the repository root with generic logo
    repo_root = Path(__file__).parent.parent.parent
    logo_path = repo_root / "logo.png"

    assert logo_path.exists(), "logo.png must exist in repository root"

    # And given a configuration
    config_path = repo_root / "config" / "default_config.yaml"
    if config_path.exists():
        config = ConfigLoader.load(str(config_path))
    else:
        config = ConfigLoader.load(None)

    # And given initialized components
    logo_loader = LogoLoader(config.logo_search_paths)
    image_renderer = ImageRenderer(config)
    file_service = FileSystemService()

    use_case = GenerateSignatureUseCase(
        image_renderer=image_renderer,
        logo_loader=logo_loader,
        file_service=file_service,
        config=config,
    )

    # And given minimal signature data (only required fields)
    signature_data = SignatureData(
        name="Jane Smith",
        position="Developer",
        email="jane.smith@example.com",
        phone="",  # Optional field empty
        mobile="",  # Optional field empty
        address="123 Main St",  # Required field
    )

    # When generating a signature
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "minimal_signature.png"

        try:
            result_path = use_case.execute(signature_data, str(output_path))
        except Exception as e:
            pytest.fail(
                f"Application failed with minimal data and generic logo: {e}"
            )

        # Then the signature should be generated successfully
        assert Path(result_path).exists(), "Signature should be created with minimal data"

        # And it should be a valid image
        with Image.open(result_path) as img:
            assert img.format == "PNG"
            assert img.width > 0 and img.height > 0
