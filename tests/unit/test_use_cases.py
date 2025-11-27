"""Unit tests for use case orchestration."""

from unittest.mock import Mock

import pytest
from PIL import Image

from src.email_signature.application.use_cases import GenerateSignatureUseCase
from src.email_signature.domain.config import SignatureConfig
from src.email_signature.domain.exceptions import (
    FileSystemError,
    ImageRenderError,
    LogoLoadError,
    LogoNotFoundError,
)
from src.email_signature.domain.models import SignatureData
from src.email_signature.infrastructure.file_service import FileSystemService
from src.email_signature.infrastructure.image_renderer import ImageRenderer
from src.email_signature.infrastructure.logo_loader import LogoLoader


def test_successful_signature_generation_flow() -> None:
    """Test complete flow with valid inputs.

    Validates: Requirements 1.1-1.7

    When all components work correctly, the use case should:
    1. Find the logo using LogoLoader
    2. Load and resize the logo
    3. Create the signature image using ImageRenderer
    4. Save the image using FileSystemService
    5. Return the output path
    """
    # Given valid signature data
    signature_data = SignatureData(
        name="John Smith",
        position="Software Engineer",
        address="Anytown, USA",
        phone="900000006",
        mobile="900000007",
        email="john.smith@example.com",
        website="www.example.com",
    )

    output_path = "test_signature.png"

    # Create mock dependencies
    config = SignatureConfig()

    # Mock LogoLoader
    logo_loader = Mock(spec=LogoLoader)
    logo_loader.find_logo.return_value = "logo.png"
    test_logo = Image.new("RGBA", (100, 70), (0, 0, 0, 0))
    logo_loader.load_and_resize_logo.return_value = test_logo

    # Mock ImageRenderer
    image_renderer = Mock(spec=ImageRenderer)
    test_signature = Image.new("RGBA", (400, 200), (0, 0, 0, 0))
    image_renderer.create_signature_image.return_value = test_signature

    # Mock FileSystemService
    file_service = Mock(spec=FileSystemService)

    # Create use case
    use_case = GenerateSignatureUseCase(
        image_renderer=image_renderer,
        logo_loader=logo_loader,
        file_service=file_service,
        config=config,
    )

    # When executing the use case
    result = use_case.execute(signature_data, output_path)

    # Then it should return the output path
    assert result == output_path

    # And it should call find_logo
    logo_loader.find_logo.assert_called_once()

    # And it should load and resize the logo with correct height
    logo_loader.load_and_resize_logo.assert_called_once_with(
        "logo.png",
        config.logo_height,
    )

    # And it should create the signature image with correct data
    image_renderer.create_signature_image.assert_called_once_with(
        signature_data,
        test_logo,
    )

    # And it should save the image to the correct path
    file_service.save_image.assert_called_once_with(
        test_signature,
        output_path,
    )


def test_logo_not_found_propagates_error() -> None:
    """Test that LogoNotFoundError is properly propagated."""
    # Given signature data
    signature_data = SignatureData(
        name="Test User",
        position="Tester",
        address="Test Address",
        phone="",
        mobile="",
        email="test@example.com",
    )

    # Create mock dependencies
    config = SignatureConfig()
    image_renderer = Mock(spec=ImageRenderer)
    logo_loader = Mock(spec=LogoLoader)
    file_service = Mock(spec=FileSystemService)

    # Configure logo_loader to return None (logo not found)
    logo_loader.find_logo.return_value = None
    logo_loader.search_paths = ["path1", "path2"]

    # Create use case
    use_case = GenerateSignatureUseCase(
        image_renderer=image_renderer,
        logo_loader=logo_loader,
        file_service=file_service,
        config=config,
    )

    # When executing the use case
    with pytest.raises(LogoNotFoundError) as exc_info:
        use_case.execute(signature_data, "output.png")

    # Then the error should contain the search paths
    assert exc_info.value.searched_paths == ["path1", "path2"]

    # And subsequent steps should not be called
    logo_loader.load_and_resize_logo.assert_not_called()
    image_renderer.create_signature_image.assert_not_called()
    file_service.save_image.assert_not_called()


def test_logo_load_error_propagates() -> None:
    """Test that LogoLoadError is properly propagated."""
    # Given signature data
    signature_data = SignatureData(
        name="Test User",
        position="Tester",
        address="Test Address",
        phone="",
        mobile="",
        email="test@example.com",
    )

    # Create mock dependencies
    config = SignatureConfig()
    image_renderer = Mock(spec=ImageRenderer)
    logo_loader = Mock(spec=LogoLoader)
    file_service = Mock(spec=FileSystemService)

    # Configure logo_loader to raise LogoLoadError
    logo_loader.find_logo.return_value = "logo.png"
    logo_loader.load_and_resize_logo.side_effect = LogoLoadError("logo.png", "Corrupted file")

    # Create use case
    use_case = GenerateSignatureUseCase(
        image_renderer=image_renderer,
        logo_loader=logo_loader,
        file_service=file_service,
        config=config,
    )

    # When executing the use case
    with pytest.raises(LogoLoadError):
        use_case.execute(signature_data, "output.png")

    # And subsequent steps should not be called
    image_renderer.create_signature_image.assert_not_called()
    file_service.save_image.assert_not_called()


def test_image_render_error_propagates() -> None:
    """Test that ImageRenderError is properly propagated."""
    # Given signature data
    signature_data = SignatureData(
        name="Test User",
        position="Tester",
        address="Test Address",
        phone="",
        mobile="",
        email="test@example.com",
    )

    # Create mock dependencies
    config = SignatureConfig()
    image_renderer = Mock(spec=ImageRenderer)
    logo_loader = Mock(spec=LogoLoader)
    file_service = Mock(spec=FileSystemService)

    # Configure mocks
    logo_loader.find_logo.return_value = "logo.png"
    test_logo = Image.new("RGBA", (100, 70), (0, 0, 0, 0))
    logo_loader.load_and_resize_logo.return_value = test_logo

    # Configure image_renderer to raise ImageRenderError
    image_renderer.create_signature_image.side_effect = ImageRenderError("rendering", "Font error")

    # Create use case
    use_case = GenerateSignatureUseCase(
        image_renderer=image_renderer,
        logo_loader=logo_loader,
        file_service=file_service,
        config=config,
    )

    # When executing the use case
    with pytest.raises(ImageRenderError):
        use_case.execute(signature_data, "output.png")

    # And file save should not be called
    file_service.save_image.assert_not_called()


def test_file_system_error_propagates() -> None:
    """Test that FileSystemError is properly propagated."""
    # Given signature data
    signature_data = SignatureData(
        name="Test User",
        position="Tester",
        address="Test Address",
        phone="",
        mobile="",
        email="test@example.com",
    )

    # Create mock dependencies
    config = SignatureConfig()
    image_renderer = Mock(spec=ImageRenderer)
    logo_loader = Mock(spec=LogoLoader)
    file_service = Mock(spec=FileSystemService)

    # Configure mocks
    logo_loader.find_logo.return_value = "logo.png"
    test_logo = Image.new("RGBA", (100, 70), (0, 0, 0, 0))
    logo_loader.load_and_resize_logo.return_value = test_logo
    test_signature = Image.new("RGBA", (400, 200), (0, 0, 0, 0))
    image_renderer.create_signature_image.return_value = test_signature

    # Configure file_service to raise FileSystemError
    file_service.save_image.side_effect = FileSystemError("save", "output.png", "Permission denied")

    # Create use case
    use_case = GenerateSignatureUseCase(
        image_renderer=image_renderer,
        logo_loader=logo_loader,
        file_service=file_service,
        config=config,
    )

    # When executing the use case
    with pytest.raises(FileSystemError):
        use_case.execute(signature_data, "output.png")
