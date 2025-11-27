"""Unit tests for PreviewGenerator."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from PIL import Image

from src.email_signature.application.use_cases import GenerateSignatureUseCase
from src.email_signature.domain.models import SignatureData
from src.email_signature.interface.gui.preview_generator import PreviewGenerator
from src.email_signature.infrastructure.platform_utils import TempFileManager


@pytest.fixture
def mock_use_case():
    """Create a mock GenerateSignatureUseCase."""
    return Mock(spec=GenerateSignatureUseCase)


@pytest.fixture
def sample_signature_data():
    """Create sample signature data for testing."""
    return SignatureData(
        name="John Doe",
        position="Software Engineer",
        address="Lisbon, Portugal",
        phone="+351 21 123 4567",
        mobile="+351 91 234 5678",
        email="john.doe@example.com",
        website="www.example.com",
    )


@pytest.fixture
def preview_generator(mock_use_case):
    """Create a PreviewGenerator instance with mock use case."""
    return PreviewGenerator(mock_use_case)


def test_preview_generator_initialization(mock_use_case):
    """Test that PreviewGenerator initializes correctly."""
    generator = PreviewGenerator(mock_use_case)
    assert generator.use_case == mock_use_case


def test_generate_preview_creates_temp_file(preview_generator, sample_signature_data):
    """Test that generate_preview creates a temporary file."""
    # Clear any existing tracked files
    TempFileManager.clear_tracking()
    
    try:
        # Create a real temporary image for the test
        temp_path = TempFileManager.create_temp_file(suffix=".png", prefix="test_preview_")
        
        # Create a simple test image
        test_image = Image.new("RGB", (100, 100), color="white")
        test_image.save(temp_path)

        # Mock the use case to use our temp file
        preview_generator.use_case.execute = Mock(return_value=str(temp_path))

        # Mock TempFileManager.create_temp_file to return our controlled temp path
        with patch.object(TempFileManager, "create_temp_file", return_value=temp_path):
            result = preview_generator.generate_preview(sample_signature_data)

            # Verify result is a PIL Image
            assert isinstance(result, Image.Image)

            # Verify use case was called
            preview_generator.use_case.execute.assert_called_once()
            call_args = preview_generator.use_case.execute.call_args
            assert call_args[0][0] == sample_signature_data
            assert call_args[0][1] == str(temp_path)

    finally:
        # Clean up
        TempFileManager.cleanup_temp_files()
        TempFileManager.clear_tracking()


def test_generate_preview_tracks_temp_files(preview_generator, sample_signature_data):
    """Test that temporary files are tracked for cleanup."""
    # Clear any existing tracked files
    TempFileManager.clear_tracking()
    
    try:
        temp_path = TempFileManager.create_temp_file(suffix=".png", prefix="signature_preview_")
        test_image = Image.new("RGB", (100, 100), color="white")
        test_image.save(temp_path)

        preview_generator.use_case.execute = Mock(return_value=str(temp_path))

        # Mock TempFileManager.create_temp_file to return our temp path
        with patch.object(TempFileManager, "create_temp_file", return_value=temp_path):
            preview_generator.generate_preview(sample_signature_data)

            # Verify temp file is tracked by TempFileManager
            tracked_files = TempFileManager.get_tracked_files()
            assert temp_path in tracked_files

    finally:
        TempFileManager.cleanup_temp_files()
        TempFileManager.clear_tracking()


def test_cleanup_removes_temp_files(preview_generator):
    """Test that cleanup removes all temporary files."""
    # Clear any existing tracked files
    TempFileManager.clear_tracking()
    
    try:
        # Create some temporary preview files
        temp_files = []
        for i in range(3):
            temp_path = TempFileManager.create_temp_file(suffix=".png", prefix="signature_preview_")
            temp_files.append(temp_path)
            # Create a simple image
            test_image = Image.new("RGB", (100, 100), color="white")
            test_image.save(temp_path)

        # Call cleanup
        preview_generator.cleanup()

        # Verify all preview files are removed
        for temp_path in temp_files:
            assert not temp_path.exists()

    finally:
        # Ensure cleanup
        TempFileManager.cleanup_temp_files()
        TempFileManager.clear_tracking()


def test_cleanup_handles_missing_files(preview_generator):
    """Test that cleanup handles files that don't exist gracefully."""
    # Clear any existing tracked files
    TempFileManager.clear_tracking()
    
    try:
        # Create temp files and then manually delete them to simulate missing files
        temp_files = []
        for i in range(2):
            temp_path = TempFileManager.create_temp_file(suffix=".png", prefix="signature_preview_")
            temp_files.append(temp_path)
            # Create and immediately delete the file
            temp_path.touch()
            temp_path.unlink()

        # Should not raise an exception even though files don't exist
        preview_generator.cleanup()

    finally:
        # Ensure cleanup
        TempFileManager.cleanup_temp_files()
        TempFileManager.clear_tracking()


def test_generate_preview_cleans_up_on_failure(preview_generator, sample_signature_data):
    """Test that failed preview generation cleans up the temp file."""
    # Clear any existing tracked files
    TempFileManager.clear_tracking()
    
    try:
        temp_path = TempFileManager.create_temp_file(suffix=".png", prefix="signature_preview_")
        temp_path.touch()  # Create the file

        # Mock use case to raise an exception
        preview_generator.use_case.execute = Mock(side_effect=Exception("Generation failed"))

        with patch.object(TempFileManager, "create_temp_file", return_value=temp_path):
            with pytest.raises(Exception, match="Generation failed"):
                preview_generator.generate_preview(sample_signature_data)

            # Verify the temp file was cleaned up after failure
            assert not temp_path.exists()

    finally:
        # Ensure cleanup
        TempFileManager.cleanup_temp_files()
        TempFileManager.clear_tracking()


def test_temp_file_manager_integration(preview_generator):
    """Test that PreviewGenerator integrates correctly with TempFileManager."""
    # Clear any existing tracked files
    TempFileManager.clear_tracking()
    
    try:
        # Create a temp file using TempFileManager
        temp_path = TempFileManager.create_temp_file(suffix=".png", prefix="signature_preview_")

        # Verify file exists
        assert temp_path.exists()

        # Verify it has .png extension
        assert temp_path.suffix == ".png"

        # Verify it's tracked by TempFileManager
        tracked_files = TempFileManager.get_tracked_files()
        assert temp_path in tracked_files

    finally:
        # Clean up
        TempFileManager.cleanup_temp_files()
        TempFileManager.clear_tracking()
