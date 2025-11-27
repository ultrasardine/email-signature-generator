"""Property-based tests for use case orchestration."""

import logging
from unittest.mock import Mock, patch

from hypothesis import given
from hypothesis import strategies as st
from PIL import Image

from src.email_signature.application.use_cases import GenerateSignatureUseCase
from src.email_signature.domain.config import SignatureConfig
from src.email_signature.domain.exceptions import (
    FileSystemError,
    ImageRenderError,
    LogoLoadError,
    LogoNotFoundError,
    SignatureGeneratorError,
)
from src.email_signature.domain.models import SignatureData
from src.email_signature.infrastructure.file_service import FileSystemService
from src.email_signature.infrastructure.image_renderer import ImageRenderer
from src.email_signature.infrastructure.logo_loader import LogoLoader


# Strategy for generating valid signature data
def signature_data_strategy() -> st.SearchStrategy[SignatureData]:
    """Generate valid SignatureData objects."""
    return st.builds(
        SignatureData,
        name=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
        position=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
        address=st.text(min_size=1, max_size=100).filter(lambda s: s.strip()),
        phone=st.text(max_size=20),
        mobile=st.text(max_size=20),
        email=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
        website=st.text(max_size=50),
    )


@given(
    signature_data=signature_data_strategy(),
    output_path=st.text(min_size=1, max_size=100),
    error_type=st.sampled_from(
        [
            "logo_not_found",
            "logo_load_error",
            "image_render_error",
            "file_system_error",
        ]
    ),
)
def test_error_logging(signature_data: SignatureData, output_path: str, error_type: str) -> None:
    """Feature: email-signature-refactor, Property 16: Error logging.

    Validates: Requirements 12.1

    For any error condition (file not found, validation failure, rendering error),
    the application should log the error with appropriate detail level (ERROR for
    critical failures, WARNING for fallbacks) before handling or propagating the error.
    """
    # Create mock dependencies
    config = SignatureConfig()
    image_renderer = Mock(spec=ImageRenderer)
    logo_loader = Mock(spec=LogoLoader)
    file_service = Mock(spec=FileSystemService)

    # Configure mocks to raise specific errors
    if error_type == "logo_not_found":
        logo_loader.find_logo.return_value = None
        logo_loader.search_paths = ["path1", "path2"]
    elif error_type == "logo_load_error":
        logo_loader.find_logo.return_value = "logo.png"
        logo_loader.load_and_resize_logo.side_effect = LogoLoadError("logo.png", "Corrupted file")
    elif error_type == "image_render_error":
        logo_loader.find_logo.return_value = "logo.png"
        # Create a simple test image
        test_logo = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        logo_loader.load_and_resize_logo.return_value = test_logo
        image_renderer.create_signature_image.side_effect = ImageRenderError(
            "rendering", "Font error"
        )
    else:  # file_system_error
        logo_loader.find_logo.return_value = "logo.png"
        test_logo = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        logo_loader.load_and_resize_logo.return_value = test_logo
        test_image = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        image_renderer.create_signature_image.return_value = test_image
        file_service.save_image.side_effect = FileSystemError(
            "save", output_path, "Permission denied"
        )

    # Create use case
    use_case = GenerateSignatureUseCase(
        image_renderer=image_renderer,
        logo_loader=logo_loader,
        file_service=file_service,
        config=config,
    )

    # Capture log records
    logger = logging.getLogger("src.email_signature.application.use_cases")
    with patch.object(logger, "error") as mock_error_log:
        with patch.object(logger, "info"):
            # When executing the use case with error conditions
            try:
                use_case.execute(signature_data, output_path)
            except (LogoNotFoundError, LogoLoadError, ImageRenderError, FileSystemError):
                # Expected errors
                pass

            # Then error should be logged at ERROR level
            assert mock_error_log.called, f"Error log should be called for {error_type}"

            # Verify that error log contains relevant information
            error_call_args = str(mock_error_log.call_args)

            # Check that the error message is descriptive
            if error_type == "logo_not_found":
                assert "logo" in error_call_args.lower() or "not found" in error_call_args.lower()
            elif error_type == "logo_load_error":
                assert "logo" in error_call_args.lower() or "load" in error_call_args.lower()
            elif error_type == "image_render_error":
                assert "render" in error_call_args.lower() or "image" in error_call_args.lower()
            else:  # file_system_error
                assert "save" in error_call_args.lower() or "file" in error_call_args.lower()


@given(
    signature_data=signature_data_strategy(),
    output_path=st.text(min_size=1, max_size=100),
)
def test_unexpected_error_handling(signature_data: SignatureData, output_path: str) -> None:
    """Feature: email-signature-refactor, Property 18: Unexpected error handling.

    Validates: Requirements 12.4

    For any unexpected exception during signature generation, the application should
    catch the error, log it, display a user-friendly message, and exit gracefully
    without crashing.
    """
    # Create mock dependencies
    config = SignatureConfig()
    image_renderer = Mock(spec=ImageRenderer)
    logo_loader = Mock(spec=LogoLoader)
    file_service = Mock(spec=FileSystemService)

    # Configure mocks to raise an unexpected error
    logo_loader.find_logo.side_effect = RuntimeError("Unexpected system error")

    # Create use case
    use_case = GenerateSignatureUseCase(
        image_renderer=image_renderer,
        logo_loader=logo_loader,
        file_service=file_service,
        config=config,
    )

    # Capture log records
    logger = logging.getLogger("src.email_signature.application.use_cases")
    with patch.object(logger, "error") as mock_error_log:
        # When executing the use case with unexpected error
        try:
            use_case.execute(signature_data, output_path)
            # Should not reach here
            assert False, "Expected SignatureGeneratorError to be raised"
        except SignatureGeneratorError as e:
            # Then the error should be wrapped in SignatureGeneratorError
            assert "Unexpected error" in str(e)

            # And error should be logged with exc_info for traceback
            assert mock_error_log.called

            # Verify that exc_info=True was used for detailed logging
            call_kwargs = mock_error_log.call_args[1] if mock_error_log.call_args else {}
            assert (
                call_kwargs.get("exc_info") is True
            ), "Should log with exc_info=True for traceback"
        except Exception as e:
            # Should not raise other exception types
            assert False, f"Should raise SignatureGeneratorError, not {type(e).__name__}"
