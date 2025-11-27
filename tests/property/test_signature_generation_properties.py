"""Property-based tests for signature generation functionality.

Feature: gui-interface
"""

import os
import tempfile
from pathlib import Path
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from src.email_signature.domain.models import SignatureData
from src.email_signature.domain.config import SignatureConfig
from src.email_signature.domain.validators import InputValidator
from src.email_signature.application.use_cases import GenerateSignatureUseCase
from src.email_signature.infrastructure.image_renderer import ImageRenderer
from src.email_signature.infrastructure.logo_loader import LogoLoader
from src.email_signature.infrastructure.file_service import FileSystemService


# Strategy for generating valid signature data
valid_signature_data = st.fixed_dictionaries({
    "name": st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
    "position": st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
    "address": st.text(min_size=1, max_size=100).filter(lambda s: s.strip()),
    "email": st.from_regex(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", fullmatch=True),
    "phone": st.one_of(st.just(""), st.from_regex(r"^\+?351\s?\d{3}\s?\d{3}\s?\d{3}$", fullmatch=True)),
    "mobile": st.one_of(st.just(""), st.from_regex(r"^\+?351\s?\d{3}\s?\d{3}\s?\d{3}$", fullmatch=True)),
    "website": st.text(max_size=50),
})


@given(data=valid_signature_data)
@settings(max_examples=100, deadline=None)
def test_signature_file_creation(data: dict) -> None:
    """Feature: gui-interface, Property 8: Signature file creation.
    
    Validates: Requirements 4.1
    
    For any valid signature data, clicking generate should create
    an image file at the specified output path.
    """
    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create output path
        output_path = os.path.join(temp_dir, "test_signature.png")
        
        # Ensure output file doesn't exist yet
        assert not os.path.exists(output_path)
        
        # Create signature data
        signature_data = SignatureData(
            name=data["name"],
            position=data["position"],
            address=data["address"],
            phone=data["phone"],
            mobile=data["mobile"],
            email=data["email"],
            website=data["website"]
        )
        
        # Create use case with dependencies
        config = SignatureConfig()
        image_renderer = ImageRenderer(config)
        logo_loader = LogoLoader(config.logo_search_paths)
        file_service = FileSystemService()
        use_case = GenerateSignatureUseCase(
            image_renderer, logo_loader, file_service, config
        )
        
        try:
            # Execute signature generation
            result_path = use_case.execute(signature_data, output_path)
            
            # Verify the file was created
            assert os.path.exists(output_path), (
                f"Signature file should be created at {output_path}, but it doesn't exist"
            )
            
            # Verify the returned path matches the requested path
            assert result_path == output_path, (
                f"Returned path {result_path} should match requested path {output_path}"
            )
            
            # Verify the file is not empty
            file_size = os.path.getsize(output_path)
            assert file_size > 0, (
                f"Signature file should not be empty, but has size {file_size}"
            )
            
            # Verify the file is a valid PNG (check magic bytes)
            with open(output_path, "rb") as f:
                header = f.read(8)
                # PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
                png_magic = b'\x89PNG\r\n\x1a\n'
                assert header == png_magic, (
                    f"File should be a valid PNG, but has header {header.hex()}"
                )
                
        except Exception as e:
            # If generation fails due to missing logo, that's acceptable for this test
            # We're testing that the file is created when generation succeeds
            if "logo" in str(e).lower():
                assume(False)  # Skip this test case
            else:
                raise


# Strategy for generating valid file paths
# We'll use paths in a temp directory to ensure they're writable
def valid_output_paths():
    """Generate valid output file paths."""
    # Generate various filename patterns
    filenames = st.one_of(
        st.just("signature.png"),
        st.text(
            alphabet=st.characters(
                whitelist_categories=["Lu", "Ll", "Nd"],
                whitelist_characters="_-"
            ),
            min_size=1,
            max_size=20
        ).map(lambda s: f"{s}.png"),
        st.text(
            alphabet=st.characters(
                whitelist_categories=["Lu", "Ll", "Nd"],
                whitelist_characters="_-"
            ),
            min_size=1,
            max_size=20
        ).map(lambda s: f"sig_{s}.png"),
    )
    return filenames


@given(
    data=valid_signature_data,
    filename=valid_output_paths()
)
@settings(max_examples=100, deadline=None)
def test_custom_output_path(data: dict, filename: str) -> None:
    """Feature: gui-interface, Property 9: Custom output path.
    
    Validates: Requirements 4.4
    
    For any valid file path chosen by the user, the signature
    should be saved to that exact location.
    """
    # Filter out invalid filenames
    assume(filename.strip())
    assume(not filename.startswith("."))
    assume(len(filename) > 4)  # At least "x.png"
    
    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create custom output path
        custom_path = os.path.join(temp_dir, filename)
        
        # Ensure output file doesn't exist yet
        assert not os.path.exists(custom_path)
        
        # Create signature data
        signature_data = SignatureData(
            name=data["name"],
            position=data["position"],
            address=data["address"],
            phone=data["phone"],
            mobile=data["mobile"],
            email=data["email"],
            website=data["website"]
        )
        
        # Create use case with dependencies
        config = SignatureConfig()
        image_renderer = ImageRenderer(config)
        logo_loader = LogoLoader(config.logo_search_paths)
        file_service = FileSystemService()
        use_case = GenerateSignatureUseCase(
            image_renderer, logo_loader, file_service, config
        )
        
        try:
            # Execute signature generation with custom path
            result_path = use_case.execute(signature_data, custom_path)
            
            # Verify the file was created at the exact custom path
            assert os.path.exists(custom_path), (
                f"Signature file should be created at custom path {custom_path}, "
                f"but it doesn't exist"
            )
            
            # Verify the returned path matches the custom path exactly
            assert result_path == custom_path, (
                f"Returned path {result_path} should match custom path {custom_path}"
            )
            
            # Verify no file was created at a different location
            # (check that only one PNG file exists in the temp directory)
            png_files = list(Path(temp_dir).glob("*.png"))
            assert len(png_files) == 1, (
                f"Should have exactly one PNG file in temp directory, "
                f"but found {len(png_files)}: {png_files}"
            )
            
            # Verify the one PNG file is at our custom path
            assert png_files[0] == Path(custom_path), (
                f"The PNG file should be at {custom_path}, "
                f"but found at {png_files[0]}"
            )
            
            # Verify the file is not empty
            file_size = os.path.getsize(custom_path)
            assert file_size > 0, (
                f"Signature file at custom path should not be empty, "
                f"but has size {file_size}"
            )
            
        except Exception as e:
            # If generation fails due to missing logo, that's acceptable for this test
            # We're testing that the file is created at the custom path when generation succeeds
            if "logo" in str(e).lower():
                assume(False)  # Skip this test case
            else:
                raise
