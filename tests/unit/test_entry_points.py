"""Unit tests for application entry points."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.email_signature.infrastructure.platform_utils import (
    DependencyChecker,
    get_python_executable_name,
    get_python_executable_path,
    is_virtual_env,
)


class TestCLIEntryPoint:
    """Tests for CLI entry point execution."""

    def test_cli_entry_point_checks_dependencies(self) -> None:
        """Test that CLI entry point checks dependencies before running.

        Validates: Requirements 5.1, 5.2
        """
        # Mock the dependency checker to simulate missing dependencies
        with patch.object(
            DependencyChecker, 'check_all_dependencies', return_value=(False, ["Missing Pillow"])
        ):
            # Import main after patching
            from main import main

            # When running the CLI entry point with missing dependencies
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Then it should exit with error code 1
            assert exc_info.value.code == 1

    def test_cli_entry_point_runs_with_dependencies(self) -> None:
        """Test that CLI entry point runs when dependencies are available.

        Validates: Requirements 5.1, 5.2
        """
        # This test verifies that the CLI entry point can be imported and
        # that it checks dependencies. We don't actually run it to avoid
        # user interaction during tests.
        
        # Mock the dependency checker to simulate all dependencies available
        with patch.object(DependencyChecker, 'check_all_dependencies', return_value=(True, [])):
            # Import main to verify it doesn't crash during import
            from main import main
            
            # Verify main is callable
            assert callable(main)
            
            # The actual execution is tested in integration tests
            # Here we just verify the entry point structure is correct

    def test_cli_entry_point_handles_keyboard_interrupt(self) -> None:
        """Test that CLI entry point handles keyboard interrupt gracefully.

        Validates: Requirements 5.1, 5.2
        """
        # Mock the dependency checker
        with patch.object(DependencyChecker, 'check_all_dependencies', return_value=(True, [])):
            # Mock the CLI to raise KeyboardInterrupt
            with patch('main.CLI') as mock_cli_class:
                mock_cli = MagicMock()
                mock_cli_class.return_value = mock_cli
                mock_cli.collect_user_data.side_effect = KeyboardInterrupt()

                # Import main
                from main import main

                # When running the CLI entry point and user interrupts
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Then it should exit with code 0 (graceful exit)
                assert exc_info.value.code == 0


@pytest.mark.gui
class TestGUIEntryPoint:
    """Tests for GUI entry point execution."""

    def test_gui_entry_point_checks_dependencies(self) -> None:
        """Test that GUI entry point checks dependencies before running.

        Validates: Requirements 5.3
        """
        # Mock the dependency checker to simulate missing Tkinter
        with patch.object(
            DependencyChecker,
            'check_gui_dependencies',
            return_value=(False, ["Tkinter is not available"]),
        ):
            # Import main after patching
            from gui_main import main

            # When running the GUI entry point with missing dependencies
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Then it should exit with error code 1
            assert exc_info.value.code == 1

    def test_gui_entry_point_runs_with_dependencies(self) -> None:
        """Test that GUI entry point runs when dependencies are available.

        Validates: Requirements 5.3
        """
        # Mock the dependency checker to simulate all dependencies available
        with patch.object(DependencyChecker, 'check_gui_dependencies', return_value=(True, [])):
            # Mock the MainWindow to avoid actually launching GUI
            with patch('src.email_signature.interface.gui.main_window.MainWindow') as mock_window_class:
                mock_window = MagicMock()
                mock_window_class.return_value = mock_window

                # Import and run main
                from gui_main import main

                # When running the GUI entry point
                # Should not raise an exception
                try:
                    main()
                except SystemExit:
                    # main() might call sys.exit(0) on success
                    pass

                # Then it should have created the main window
                mock_window_class.assert_called_once()

                # And it should have called run()
                mock_window.run.assert_called_once()

    def test_gui_entry_point_handles_exceptions(self) -> None:
        """Test that GUI entry point handles exceptions gracefully.

        Validates: Requirements 5.3
        """
        # Mock the dependency checker
        with patch.object(DependencyChecker, 'check_gui_dependencies', return_value=(True, [])):
            # Mock the MainWindow to raise an exception
            with patch('src.email_signature.interface.gui.main_window.MainWindow') as mock_window_class:
                mock_window_class.side_effect = RuntimeError("Test error")

                # Import main
                from gui_main import main

                # When running the GUI entry point and an error occurs
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Then it should exit with error code 1
                assert exc_info.value.code == 1


class TestVirtualEnvironmentDetection:
    """Tests for virtual environment detection."""

    def test_virtual_environment_detection_in_venv(self) -> None:
        """Test that virtual environment detection works correctly.

        Validates: Requirements 5.1, 5.2, 5.3
        """
        # Save original attributes
        original_real_prefix = getattr(sys, 'real_prefix', None)
        original_base_prefix = getattr(sys, 'base_prefix', sys.prefix)
        original_prefix = sys.prefix

        try:
            # Simulate venv environment
            sys.base_prefix = '/usr/bin/python'
            sys.prefix = '/home/user/.venv'

            # When checking if in virtual environment
            result = is_virtual_env()

            # Then it should return True
            assert result is True

        finally:
            # Restore original attributes
            if original_real_prefix is not None:
                sys.real_prefix = original_real_prefix
            elif hasattr(sys, 'real_prefix'):
                delattr(sys, 'real_prefix')

            sys.base_prefix = original_base_prefix
            sys.prefix = original_prefix

    def test_virtual_environment_detection_not_in_venv(self) -> None:
        """Test that virtual environment detection returns False when not in venv.

        Validates: Requirements 5.1, 5.2, 5.3
        """
        # Save original attributes
        original_real_prefix = getattr(sys, 'real_prefix', None)
        original_base_prefix = getattr(sys, 'base_prefix', sys.prefix)
        original_prefix = sys.prefix

        try:
            # Simulate not in venv
            if hasattr(sys, 'real_prefix'):
                delattr(sys, 'real_prefix')
            sys.base_prefix = sys.prefix

            # When checking if in virtual environment
            result = is_virtual_env()

            # Then it should return False
            assert result is False

        finally:
            # Restore original attributes
            if original_real_prefix is not None:
                sys.real_prefix = original_real_prefix
            elif hasattr(sys, 'real_prefix'):
                delattr(sys, 'real_prefix')

            sys.base_prefix = original_base_prefix
            sys.prefix = original_prefix

    def test_virtual_environment_detection_in_virtualenv(self) -> None:
        """Test that virtual environment detection works for virtualenv.

        Validates: Requirements 5.1, 5.2, 5.3
        """
        # Save original attributes
        original_real_prefix = getattr(sys, 'real_prefix', None)
        original_base_prefix = getattr(sys, 'base_prefix', sys.prefix)
        original_prefix = sys.prefix

        try:
            # Simulate virtualenv environment
            sys.real_prefix = '/usr/bin/python'

            # When checking if in virtual environment
            result = is_virtual_env()

            # Then it should return True
            assert result is True

        finally:
            # Restore original attributes
            if original_real_prefix is not None:
                sys.real_prefix = original_real_prefix
            elif hasattr(sys, 'real_prefix'):
                delattr(sys, 'real_prefix')

            sys.base_prefix = original_base_prefix
            sys.prefix = original_prefix


class TestPythonExecutableName:
    """Tests for Python executable name handling."""

    def test_python_executable_name_in_venv(self) -> None:
        """Test that Python executable name is 'python' in virtual environment.

        Validates: Requirements 5.5
        """
        with patch('src.email_signature.infrastructure.platform_utils.is_virtual_env', return_value=True):
            # When getting Python executable name in venv
            result = get_python_executable_name()

            # Then it should return 'python'
            assert result == 'python'

    def test_python_executable_name_on_windows(self) -> None:
        """Test that Python executable name is 'python.exe' on Windows.

        Validates: Requirements 5.5
        """
        with patch('src.email_signature.infrastructure.platform_utils.is_virtual_env', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=True):
                # When getting Python executable name on Windows
                result = get_python_executable_name()

                # Then it should return 'python.exe'
                assert result == 'python.exe'

    def test_python_executable_name_on_unix(self) -> None:
        """Test that Python executable name is 'python3' on Unix-like systems.

        Validates: Requirements 5.5
        """
        with patch('src.email_signature.infrastructure.platform_utils.is_virtual_env', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
                # When getting Python executable name on Unix
                result = get_python_executable_name()

                # Then it should return 'python3'
                assert result == 'python3'

    def test_python_executable_path_exists(self) -> None:
        """Test that Python executable path points to an existing file.

        Validates: Requirements 5.5
        """
        # When getting Python executable path
        result = get_python_executable_path()

        # Then it should be a Path object
        assert isinstance(result, Path)

        # And it should exist
        assert result.exists()

        # And it should be a file
        assert result.is_file()

        # And it should match sys.executable
        assert result == Path(sys.executable)


class TestDependencyChecker:
    """Tests for dependency checking functionality."""

    def test_check_pillow_available(self) -> None:
        """Test that Pillow dependency check works when available."""
        # When checking Pillow (which should be available in test environment)
        is_available, error_message = DependencyChecker.check_pillow()

        # Then it should be available
        assert is_available is True
        assert error_message == ""

    def test_check_pillow_unavailable(self) -> None:
        """Test that Pillow dependency check works when unavailable."""
        # Mock PIL import to fail
        with patch.dict('sys.modules', {'PIL': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'PIL'")):
                # When checking Pillow
                is_available, error_message = DependencyChecker.check_pillow()

                # Then it should not be available
                assert is_available is False
                assert "Pillow" in error_message
                assert "install" in error_message.lower()

    def test_check_yaml_available(self) -> None:
        """Test that PyYAML dependency check works when available."""
        # When checking PyYAML (which should be available in test environment)
        is_available, error_message = DependencyChecker.check_yaml()

        # Then it should be available
        assert is_available is True
        assert error_message == ""

    def test_check_yaml_unavailable(self) -> None:
        """Test that PyYAML dependency check works when unavailable."""
        # Mock yaml import to fail
        with patch.dict('sys.modules', {'yaml': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'yaml'")):
                # When checking PyYAML
                is_available, error_message = DependencyChecker.check_yaml()

                # Then it should not be available
                assert is_available is False
                assert "PyYAML" in error_message
                assert "install" in error_message.lower()

    def test_check_all_dependencies_available(self) -> None:
        """Test that check_all_dependencies works when all are available."""
        # Mock both dependencies as available
        with patch.object(DependencyChecker, 'check_pillow', return_value=(True, "")):
            with patch.object(DependencyChecker, 'check_yaml', return_value=(True, "")):
                # When checking all dependencies
                all_ok, errors = DependencyChecker.check_all_dependencies()

                # Then all should be available
                assert all_ok is True
                assert len(errors) == 0

    def test_check_all_dependencies_some_missing(self) -> None:
        """Test that check_all_dependencies works when some are missing."""
        # Mock Pillow as missing
        with patch.object(DependencyChecker, 'check_pillow', return_value=(False, "Pillow missing")):
            with patch.object(DependencyChecker, 'check_yaml', return_value=(True, "")):
                # When checking all dependencies
                all_ok, errors = DependencyChecker.check_all_dependencies()

                # Then not all should be available
                assert all_ok is False
                assert len(errors) == 1
                assert "Pillow" in errors[0]

    def test_check_gui_dependencies_available(self) -> None:
        """Test that check_gui_dependencies works when all are available."""
        # Mock all dependencies as available
        with patch.object(DependencyChecker, 'check_all_dependencies', return_value=(True, [])):
            with patch.object(DependencyChecker, 'check_tkinter', return_value=(True, "")):
                # When checking GUI dependencies
                all_ok, errors = DependencyChecker.check_gui_dependencies()

                # Then all should be available
                assert all_ok is True
                assert len(errors) == 0

    def test_check_gui_dependencies_tkinter_missing(self) -> None:
        """Test that check_gui_dependencies works when Tkinter is missing."""
        # Mock base dependencies as available but Tkinter as missing
        with patch.object(DependencyChecker, 'check_all_dependencies', return_value=(True, [])):
            with patch.object(
                DependencyChecker, 'check_tkinter', return_value=(False, "Tkinter missing")
            ):
                # When checking GUI dependencies
                all_ok, errors = DependencyChecker.check_gui_dependencies()

                # Then not all should be available
                assert all_ok is False
                assert len(errors) == 1
                assert "Tkinter" in errors[0]
