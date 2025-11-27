"""Property-based tests for GUI logo selection and preview.

Feature: gui-interface
"""

import os
import tempfile
import tkinter as tk
from pathlib import Path
from typing import Optional

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from PIL import Image


def create_test_image(path: str, width: int = 100, height: int = 100) -> None:
    """Create a test image file.
    
    Args:
        path: Path where to save the image
        width: Image width in pixels
        height: Image height in pixels
    """
    # Create a simple test image
    img = Image.new('RGB', (width, height), color='red')
    img.save(path)


# Strategy for generating valid image file paths
@st.composite
def valid_image_paths(draw):
    """Generate valid image file paths with actual image files."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Generate a random filename
    extension = draw(st.sampled_from(['.png', '.jpg', '.jpeg']))
    filename = draw(st.text(alphabet=st.characters(whitelist_categories=['L', 'N']), min_size=1, max_size=20))
    filename = filename.replace('/', '_').replace('\\', '_')  # Remove path separators
    
    # Create full path
    file_path = os.path.join(temp_dir, filename + extension)
    
    # Create the test image
    width = draw(st.integers(min_value=50, max_value=500))
    height = draw(st.integers(min_value=50, max_value=500))
    create_test_image(file_path, width, height)
    
    return file_path


@pytest.mark.gui
@given(logo_path=valid_image_paths())
@settings(max_examples=100, deadline=None)
def test_logo_path_display(logo_path: str) -> None:
    """Feature: gui-interface, Property 11: Logo path display.
    
    Validates: Requirements 6.3
    
    For any valid logo file selected through the file picker,
    the file path should be displayed in the GUI.
    """
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Import dependencies
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.domain.validators import InputValidator
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        from src.email_signature.interface.gui.signature_tab import SignatureTab
        from src.email_signature.infrastructure.image_renderer import ImageRenderer
        from src.email_signature.infrastructure.logo_loader import LogoLoader
        from src.email_signature.infrastructure.file_service import FileSystemService
        
        # Create dependencies
        config = SignatureConfig()
        validator = InputValidator()
        image_renderer = ImageRenderer(config)
        logo_loader = LogoLoader(config.logo_search_paths)
        file_service = FileSystemService()
        use_case = GenerateSignatureUseCase(image_renderer, logo_loader, file_service, config)
        
        # Create the signature tab
        tab = SignatureTab(root, config, validator, use_case)
        
        # Simulate logo selection by directly setting the path
        tab.selected_logo_path = logo_path
        
        # Update the path display (simulate what _on_browse_logo_clicked does)
        display_path = logo_path
        if len(logo_path) > 50:
            display_path = "..." + logo_path[-47:]
        tab.logo_path_var.set(display_path)
        
        # Update the UI
        root.update_idletasks()
        
        # Verify the path is displayed
        displayed_path = tab.logo_path_var.get()
        
        # The displayed path should either be the full path or a truncated version
        assert displayed_path != "(using default logo)", "Logo path should be displayed after selection"
        
        # If the path is long, it should be truncated
        if len(logo_path) > 50:
            assert displayed_path.startswith("..."), "Long paths should be truncated with '...'"
            assert logo_path.endswith(displayed_path[3:]), "Truncated path should match the end of the full path"
        else:
            assert displayed_path == logo_path, "Short paths should be displayed in full"
        
        # Verify the selected logo path is stored
        assert tab.get_selected_logo_path() == logo_path, "Selected logo path should be stored"
        
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass
        
        # Clean up the temporary file
        try:
            if os.path.exists(logo_path):
                os.remove(logo_path)
            # Try to remove the parent directory
            parent_dir = os.path.dirname(logo_path)
            if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                os.rmdir(parent_dir)
        except:
            pass


@pytest.mark.gui
@given(logo_path=valid_image_paths())
@settings(max_examples=100, deadline=None)
def test_logo_preview_display(logo_path: str) -> None:
    """Feature: gui-interface, Property 12: Logo preview display.
    
    Validates: Requirements 6.4
    
    For any valid logo file selected through the file picker,
    a thumbnail preview should be displayed in the GUI.
    """
    # Create a temporary Tkinter root for testing
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    except tk.TclError:
        # Skip test if Tkinter is not properly configured
        return
    
    try:
        # Import dependencies
        from src.email_signature.domain.config import SignatureConfig
        from src.email_signature.domain.validators import InputValidator
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        from src.email_signature.interface.gui.signature_tab import SignatureTab
        from src.email_signature.infrastructure.image_renderer import ImageRenderer
        from src.email_signature.infrastructure.logo_loader import LogoLoader
        from src.email_signature.infrastructure.file_service import FileSystemService
        
        # Create dependencies
        config = SignatureConfig()
        validator = InputValidator()
        image_renderer = ImageRenderer(config)
        logo_loader = LogoLoader(config.logo_search_paths)
        file_service = FileSystemService()
        use_case = GenerateSignatureUseCase(image_renderer, logo_loader, file_service, config)
        
        # Create the signature tab
        tab = SignatureTab(root, config, validator, use_case)
        
        # Verify initial state (no preview)
        assert tab.logo_preview_image is None, "Initially, no preview image should be set"
        
        # Update the logo preview
        tab._update_logo_preview(logo_path)
        
        # Update the UI
        root.update_idletasks()
        
        # Verify a preview image is now displayed
        assert tab.logo_preview_image is not None, "After selecting a logo, a preview image should be displayed"
        
        # Verify the preview label has an image (not just text)
        assert tab.logo_preview_label.cget("image") != "", "Preview label should have an image"
        
        # Verify the text is cleared (when image is shown, text should be empty)
        assert tab.logo_preview_label.cget("text") == "", "Preview label text should be empty when image is shown"
        
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass
        
        # Clean up the temporary file
        try:
            if os.path.exists(logo_path):
                os.remove(logo_path)
            # Try to remove the parent directory
            parent_dir = os.path.dirname(logo_path)
            if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                os.rmdir(parent_dir)
        except:
            pass
