"""Unit tests for GUI folder opening functionality.

This test verifies that the GUI correctly uses SystemCommandExecutor
for opening folders in the native file manager.
"""

import unittest
from pathlib import Path
from unittest.mock import patch, call
import pytest
from src.email_signature.infrastructure.platform_utils import SystemCommandExecutor


@pytest.mark.gui
class TestGUIFolderOpenIntegration(unittest.TestCase):
    """Test that GUI integration with SystemCommandExecutor works correctly."""
    
    def test_system_command_executor_imported_in_signature_tab(self):
        """Test that SystemCommandExecutor is imported in signature_tab module."""
        # This verifies the import is present
        from src.email_signature.interface.gui import signature_tab
        
        # Check that the module can access SystemCommandExecutor
        # by reading the source code
        import inspect
        source = inspect.getsource(signature_tab)
        
        # Verify SystemCommandExecutor is imported
        self.assertIn('SystemCommandExecutor', source)
        self.assertIn('from ...infrastructure.platform_utils import SystemCommandExecutor', source)
    
    def test_on_generation_success_uses_system_command_executor(self):
        """Test that _on_generation_success method uses SystemCommandExecutor."""
        from src.email_signature.interface.gui import signature_tab
        import inspect
        
        # Get the source code of _on_generation_success method
        source = inspect.getsource(signature_tab.SignatureTab._on_generation_success)
        
        # Verify it uses SystemCommandExecutor.open_folder
        self.assertIn('SystemCommandExecutor.open_folder', source)
        
        # Verify it uses ErrorMessageFormatter for error handling
        self.assertIn('ErrorMessageFormatter', source)
        
        # Verify it doesn't use the old platform.system() approach
        self.assertNotIn('platform.system() == "Darwin"', source)
        self.assertNotIn('platform.system() == "Windows"', source)
        self.assertNotIn('subprocess.run(["open"', source)
        self.assertNotIn('subprocess.run(["explorer"', source)
        self.assertNotIn('subprocess.run(["xdg-open"', source)
    
    def test_error_message_formatter_imported_in_signature_tab(self):
        """Test that ErrorMessageFormatter is imported in signature_tab module."""
        from src.email_signature.interface.gui import signature_tab
        import inspect
        
        source = inspect.getsource(signature_tab)
        
        # Verify ErrorMessageFormatter is imported
        self.assertIn('ErrorMessageFormatter', source)
        self.assertIn('from ...infrastructure.platform_utils import', source)
    
    def test_system_command_executor_open_folder_works(self):
        """Test that SystemCommandExecutor.open_folder can be called."""
        import tempfile
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # This should not raise an exception
            # The result may be True or False depending on the system
            result = SystemCommandExecutor.open_folder(temp_path)
            
            # Result should be a boolean
            self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main()
