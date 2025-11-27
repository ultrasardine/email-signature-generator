"""Unit tests for platform-specific command generation."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.email_signature.infrastructure.platform_utils import (
    FontLocator,
    SystemCommandExecutor,
    is_linux,
    is_macos,
    is_windows,
)


def test_windows_explorer_command_generation() -> None:
    """Test Windows explorer command generation.
    
    Validates: Requirements 2.1
    
    When opening a folder on Windows, the system should execute explorer <path>.
    """
    # Given a folder path
    folder_path = Path("C:/test/folder")
    
    # When getting the open folder command on Windows
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=True):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=False):
                command = SystemCommandExecutor.get_open_folder_command(folder_path)
    
    # Then it should return the explorer command
    assert command[0] == 'explorer', f"Expected 'explorer', got '{command[0]}'"
    assert str(folder_path) in command, f"Expected path '{folder_path}' in command {command}"
    assert len(command) == 2, f"Expected 2 elements in command, got {len(command)}"


def test_macos_open_command_generation() -> None:
    """Test macOS open command generation.
    
    Validates: Requirements 2.2
    
    When opening a folder on macOS, the system should execute open <path>.
    """
    # Given a folder path
    folder_path = Path("/test/folder")
    
    # When getting the open folder command on macOS
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=True):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=False):
                command = SystemCommandExecutor.get_open_folder_command(folder_path)
    
    # Then it should return the open command
    assert command[0] == 'open', f"Expected 'open', got '{command[0]}'"
    assert str(folder_path) in command, f"Expected path '{folder_path}' in command {command}"
    assert len(command) == 2, f"Expected 2 elements in command, got {len(command)}"


def test_linux_xdg_open_command_generation() -> None:
    """Test Linux xdg-open command generation with fallbacks.
    
    Validates: Requirements 2.3
    
    When opening a folder on Linux, the system should execute xdg-open <path>
    or an appropriate fallback.
    """
    # Given a folder path
    folder_path = Path("/test/folder")
    
    # When getting the open folder command on Linux
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=True):
                command = SystemCommandExecutor.get_open_folder_command(folder_path)
    
    # Then it should return the xdg-open command
    assert command[0] == 'xdg-open', f"Expected 'xdg-open', got '{command[0]}'"
    assert str(folder_path) in command, f"Expected path '{folder_path}' in command {command}"
    assert len(command) == 2, f"Expected 2 elements in command, got {len(command)}"


def test_linux_fallback_commands() -> None:
    """Test Linux fallback commands are available.
    
    Validates: Requirements 2.3
    
    When xdg-open fails on Linux, the system should have fallback commands
    like gnome-open and kde-open.
    """
    # Given a folder path
    folder_path = Path("/test/folder")
    
    # When getting fallback commands
    fallback_commands = SystemCommandExecutor.get_linux_fallback_commands(folder_path)
    
    # Then it should return a list of fallback commands
    assert isinstance(fallback_commands, list), "Expected list of fallback commands"
    assert len(fallback_commands) >= 2, "Expected at least 2 fallback commands"
    
    # And the fallback commands should include gnome-open and kde-open
    command_names = [cmd[0] for cmd in fallback_commands]
    assert 'gnome-open' in command_names, "Expected 'gnome-open' in fallback commands"
    assert 'kde-open' in command_names, "Expected 'kde-open' in fallback commands"
    
    # And each fallback command should include the folder path
    for cmd in fallback_commands:
        assert str(folder_path) in cmd, f"Expected path '{folder_path}' in command {cmd}"


def test_execute_command_with_nonexistent_command() -> None:
    """Test execute_command handles nonexistent commands gracefully.
    
    Validates: Requirements 2.4
    
    When a command doesn't exist, execute_command should return False
    with an appropriate error message.
    """
    # Given a nonexistent command
    command = ['nonexistent_command_xyz123', '/some/path']
    
    # When executing the command
    success, error_message = SystemCommandExecutor.execute_command(command)
    
    # Then it should return False
    assert success is False, "Expected execute_command to return False for nonexistent command"
    
    # And it should provide an error message
    assert error_message, "Expected non-empty error message"
    assert isinstance(error_message, str), f"Expected string error message, got {type(error_message)}"
    assert 'not found' in error_message.lower() or 'nonexistent' in error_message.lower(), \
        f"Expected error message to mention command not found, got: {error_message}"


def test_current_platform_command_generation() -> None:
    """Test command generation for the current platform.
    
    This test verifies that the command generation works correctly
    for whichever platform the test is running on.
    """
    # Given a folder path
    folder_path = Path("/test/folder")
    
    # When getting the open folder command
    command = SystemCommandExecutor.get_open_folder_command(folder_path)
    
    # Then it should return a valid command
    assert isinstance(command, list), "Expected command to be a list"
    assert len(command) >= 2, "Expected command to have at least 2 elements"
    assert str(folder_path) in command, f"Expected path '{folder_path}' in command {command}"
    
    # And the command should match the current platform
    if is_windows():
        assert command[0] == 'explorer', "Expected 'explorer' on Windows"
    elif is_macos():
        assert command[0] == 'open', "Expected 'open' on macOS"
    elif is_linux():
        assert command[0] == 'xdg-open', "Expected 'xdg-open' on Linux"


# FontLocator Unit Tests


def test_windows_font_directories() -> None:
    """Test Windows font directory detection.
    
    Validates: Requirements 3.1, 3.3
    
    When loading fonts on Windows, the system should search C:\\Windows\\Fonts
    and user font directories.
    """
    # When getting font directories on Windows
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=True):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=False):
                # Mock the Path.exists() to return True for our test directories
                with patch('pathlib.Path.exists', return_value=True):
                    directories = FontLocator.get_font_directories()
    
    # Then it should return Windows font directories
    assert isinstance(directories, list), "Expected list of directories"
    
    # The directories should be Path objects
    for directory in directories:
        assert isinstance(directory, Path), f"Expected Path object, got {type(directory)}"
    
    # Should include Windows Fonts directory (when it exists)
    # Note: We can't check exact paths since they depend on environment variables
    # but we can verify the structure is correct
    assert len(directories) > 0, "Expected at least one font directory on Windows"


def test_macos_font_directories() -> None:
    """Test macOS font directory detection.
    
    Validates: Requirements 3.1, 3.4
    
    When loading fonts on macOS, the system should search /Library/Fonts,
    /System/Library/Fonts, and ~/Library/Fonts.
    """
    # When getting font directories on macOS
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=True):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=False):
                # Mock the Path.exists() to return True for our test directories
                with patch('pathlib.Path.exists', return_value=True):
                    directories = FontLocator.get_font_directories()
    
    # Then it should return macOS font directories
    assert isinstance(directories, list), "Expected list of directories"
    assert len(directories) > 0, "Expected at least one font directory on macOS"
    
    # The directories should be Path objects
    for directory in directories:
        assert isinstance(directory, Path), f"Expected Path object, got {type(directory)}"
    
    # Should include standard macOS font directories (when they exist)
    directory_strs = [str(d) for d in directories]
    # At least one should contain "Library/Fonts"
    assert any('Library/Fonts' in d for d in directory_strs), \
        "Expected macOS font directories to include Library/Fonts paths"


def test_linux_font_directories() -> None:
    """Test Linux font directory detection.
    
    Validates: Requirements 3.1, 3.5
    
    When loading fonts on Linux, the system should search /usr/share/fonts,
    ~/.fonts, and ~/.local/share/fonts.
    """
    # When getting font directories on Linux
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=True):
                # Mock the Path.exists() to return True for our test directories
                with patch('pathlib.Path.exists', return_value=True):
                    directories = FontLocator.get_font_directories()
    
    # Then it should return Linux font directories
    assert isinstance(directories, list), "Expected list of directories"
    assert len(directories) > 0, "Expected at least one font directory on Linux"
    
    # The directories should be Path objects
    for directory in directories:
        assert isinstance(directory, Path), f"Expected Path object, got {type(directory)}"
    
    # Should include standard Linux font directories (when they exist)
    directory_strs = [str(d) for d in directories]
    # At least one should contain "fonts"
    assert any('fonts' in d.lower() for d in directory_strs), \
        "Expected Linux font directories to include font paths"


def test_get_default_fonts_returns_platform_appropriate_fonts() -> None:
    """Test that get_default_fonts returns appropriate fonts for each platform.
    
    Validates: Requirements 3.2
    
    The system should return platform-appropriate default fonts.
    """
    # When getting default fonts
    default_fonts = FontLocator.get_default_fonts()
    
    # Then it should return a dictionary
    assert isinstance(default_fonts, dict), "Expected dictionary of default fonts"
    
    # And it should have the expected keys
    expected_keys = {'sans-serif', 'serif', 'monospace'}
    assert set(default_fonts.keys()) == expected_keys, \
        f"Expected keys {expected_keys}, got {set(default_fonts.keys())}"
    
    # And all values should be non-empty strings
    for font_type, font_name in default_fonts.items():
        assert isinstance(font_name, str), \
            f"Expected string for {font_type}, got {type(font_name)}"
        assert font_name.strip(), f"Expected non-empty font name for {font_type}"
    
    # And the fonts should be platform-appropriate
    if is_windows():
        # Windows should have fonts like Arial, Times New Roman, Courier New
        assert any(font in ['Arial', 'Calibri', 'Times New Roman', 'Courier New'] 
                   for font in default_fonts.values()), \
            f"Expected Windows fonts, got {default_fonts}"
    elif is_macos():
        # macOS should have fonts like Helvetica, Times, Courier
        assert any(font in ['Helvetica', 'SF Pro', 'Times', 'Courier'] 
                   for font in default_fonts.values()), \
            f"Expected macOS fonts, got {default_fonts}"
    elif is_linux():
        # Linux should have DejaVu fonts
        assert any('DejaVu' in font for font in default_fonts.values()), \
            f"Expected Linux DejaVu fonts, got {default_fonts}"


def test_validate_font_path_with_valid_font() -> None:
    """Test font path validation with a valid font file.
    
    Validates: Requirements 8.4
    
    The system should validate font paths according to platform conventions.
    """
    # Given a valid font path (mocked)
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    
    # When validating the font path
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.is_file', return_value=True):
            result = FontLocator.validate_font_path(font_path)
    
    # Then it should return True
    assert result is True, "Expected validate_font_path to return True for valid font"


def test_validate_font_path_with_nonexistent_file() -> None:
    """Test font path validation with a nonexistent file.
    
    Validates: Requirements 8.4
    
    The system should reject nonexistent font paths.
    """
    # Given a nonexistent font path
    font_path = Path("/nonexistent/font.ttf")
    
    # When validating the font path
    with patch('pathlib.Path.exists', return_value=False):
        result = FontLocator.validate_font_path(font_path)
    
    # Then it should return False
    assert result is False, "Expected validate_font_path to return False for nonexistent file"


def test_validate_font_path_with_directory() -> None:
    """Test font path validation with a directory instead of a file.
    
    Validates: Requirements 8.4
    
    The system should reject directories as font paths.
    """
    # Given a directory path
    font_path = Path("/usr/share/fonts")
    
    # When validating the font path
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.is_file', return_value=False):
            result = FontLocator.validate_font_path(font_path)
    
    # Then it should return False
    assert result is False, "Expected validate_font_path to return False for directory"


def test_validate_font_path_with_invalid_extension() -> None:
    """Test font path validation with an invalid file extension.
    
    Validates: Requirements 8.4
    
    The system should reject files without valid font extensions.
    """
    # Given a file with invalid extension
    font_path = Path("/usr/share/fonts/notafont.txt")
    
    # When validating the font path
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.is_file', return_value=True):
            result = FontLocator.validate_font_path(font_path)
    
    # Then it should return False
    assert result is False, "Expected validate_font_path to return False for invalid extension"


def test_find_font_returns_none_for_nonexistent_font() -> None:
    """Test that find_font returns None when font is not found.
    
    Validates: Requirements 3.2
    
    When a font is not found, the system should return None to allow
    fallback to default fonts.
    """
    # Given a nonexistent font name
    font_name = "NonExistentFont_XYZ123"
    
    # When searching for the font
    result = FontLocator.find_font(font_name)
    
    # Then it should return None
    assert result is None, f"Expected None for nonexistent font, got {result}"



# ErrorMessageFormatter Unit Tests


def test_dependency_install_command_windows() -> None:
    """Test dependency installation commands for Windows.
    
    Validates: Requirements 10.3
    
    When a dependency is missing on Windows, the system should provide
    Windows-specific installation commands.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Given a dependency name
    dependency = "pillow"
    
    # When getting the install command on Windows
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=True):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=False):
                command = ErrorMessageFormatter.get_dependency_install_command(dependency)
    
    # Then it should return a Windows-appropriate command
    assert isinstance(command, str), f"Expected string command, got {type(command)}"
    assert 'pip' in command.lower(), "Expected command to use pip"
    assert dependency in command, f"Expected dependency '{dependency}' in command"
    # Windows typically uses 'pip install' without sudo
    assert 'sudo' not in command.lower(), "Windows command should not use sudo"


def test_dependency_install_command_macos() -> None:
    """Test dependency installation commands for macOS.
    
    Validates: Requirements 10.3
    
    When a dependency is missing on macOS, the system should provide
    macOS-specific installation commands.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Given a Python package dependency
    dependency = "pillow"
    
    # When getting the install command on macOS
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=True):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=False):
                command = ErrorMessageFormatter.get_dependency_install_command(dependency)
    
    # Then it should return a macOS-appropriate command
    assert isinstance(command, str), f"Expected string command, got {type(command)}"
    assert 'pip3' in command or 'brew' in command, \
        "Expected command to use pip3 or brew"
    assert dependency in command, f"Expected dependency '{dependency}' in command"


def test_dependency_install_command_macos_system_package() -> None:
    """Test dependency installation commands for macOS system packages.
    
    Validates: Requirements 10.3
    
    When a system dependency is missing on macOS, the system should suggest
    using brew.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Given a system package dependency
    dependency = "tkinter"
    
    # When getting the install command on macOS
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=True):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=False):
                command = ErrorMessageFormatter.get_dependency_install_command(dependency)
    
    # Then it should suggest using brew
    assert isinstance(command, str), f"Expected string command, got {type(command)}"
    assert 'brew' in command, "Expected command to use brew for system packages"
    assert dependency in command, f"Expected dependency '{dependency}' in command"


def test_dependency_install_command_linux() -> None:
    """Test dependency installation commands for Linux.
    
    Validates: Requirements 10.3
    
    When a dependency is missing on Linux, the system should provide
    Linux-specific installation commands.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Given a Python package dependency
    dependency = "pillow"
    
    # When getting the install command on Linux
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=True):
                command = ErrorMessageFormatter.get_dependency_install_command(dependency)
    
    # Then it should return a Linux-appropriate command
    assert isinstance(command, str), f"Expected string command, got {type(command)}"
    assert 'pip3' in command or 'apt' in command, \
        "Expected command to use pip3 or apt"
    assert dependency in command, f"Expected dependency '{dependency}' in command"


def test_dependency_install_command_linux_system_package() -> None:
    """Test dependency installation commands for Linux system packages.
    
    Validates: Requirements 10.3
    
    When a system dependency is missing on Linux, the system should suggest
    using apt.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Given a system package dependency (with python3- prefix)
    dependency = "python3-tk"
    
    # When getting the install command on Linux
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=True):
                command = ErrorMessageFormatter.get_dependency_install_command(dependency)
    
    # Then it should suggest using apt
    assert isinstance(command, str), f"Expected string command, got {type(command)}"
    assert 'apt' in command, "Expected command to use apt for system packages"
    assert dependency in command, f"Expected dependency '{dependency}' in command"


def test_font_location_hint_windows() -> None:
    """Test font location hints for Windows.
    
    Validates: Requirements 10.4
    
    When a font is not found on Windows, the system should suggest
    Windows-appropriate font locations.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # When getting font location hint on Windows
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=True):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=False):
                hint = ErrorMessageFormatter.get_font_location_hint()
    
    # Then it should return Windows-specific hints
    assert isinstance(hint, str), f"Expected string hint, got {type(hint)}"
    assert 'Windows' in hint or 'Fonts' in hint, \
        "Expected hint to mention Windows or Fonts"
    assert 'C:\\Windows\\Fonts' in hint or 'LOCALAPPDATA' in hint, \
        "Expected hint to mention Windows font directories"


def test_font_location_hint_macos() -> None:
    """Test font location hints for macOS.
    
    Validates: Requirements 10.4
    
    When a font is not found on macOS, the system should suggest
    macOS-appropriate font locations.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # When getting font location hint on macOS
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=True):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=False):
                hint = ErrorMessageFormatter.get_font_location_hint()
    
    # Then it should return macOS-specific hints
    assert isinstance(hint, str), f"Expected string hint, got {type(hint)}"
    assert 'Library/Fonts' in hint, \
        "Expected hint to mention Library/Fonts"
    assert 'Font Book' in hint or 'macOS' in hint, \
        "Expected hint to mention Font Book or macOS"


def test_font_location_hint_linux() -> None:
    """Test font location hints for Linux.
    
    Validates: Requirements 10.4
    
    When a font is not found on Linux, the system should suggest
    Linux-appropriate font locations.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # When getting font location hint on Linux
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=True):
                hint = ErrorMessageFormatter.get_font_location_hint()
    
    # Then it should return Linux-specific hints
    assert isinstance(hint, str), f"Expected string hint, got {type(hint)}"
    assert '/usr/share/fonts' in hint or '.fonts' in hint, \
        "Expected hint to mention Linux font directories"
    assert 'fc-cache' in hint, \
        "Expected hint to mention fc-cache command"


def test_format_command_error_windows() -> None:
    """Test command error formatting for Windows.
    
    Validates: Requirements 10.5
    
    When a system command fails on Windows, the error message should
    provide Windows-specific context.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Given a failed Windows command
    command = ['explorer', 'C:\\test\\folder']
    error = "Command failed with exit code 1"
    
    # When formatting the error on Windows
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=True):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=False):
                formatted = ErrorMessageFormatter.format_command_error(command, error)
    
    # Then it should return a formatted error message
    assert isinstance(formatted, str), f"Expected string message, got {type(formatted)}"
    assert 'explorer' in formatted, "Expected message to mention explorer"
    assert error in formatted, "Expected message to include original error"
    assert 'Windows' in formatted, "Expected message to mention Windows"


def test_format_command_error_macos() -> None:
    """Test command error formatting for macOS.
    
    Validates: Requirements 10.5
    
    When a system command fails on macOS, the error message should
    provide macOS-specific context.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Given a failed macOS command
    command = ['open', '/test/folder']
    error = "Command failed with exit code 1"
    
    # When formatting the error on macOS
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=True):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=False):
                formatted = ErrorMessageFormatter.format_command_error(command, error)
    
    # Then it should return a formatted error message
    assert isinstance(formatted, str), f"Expected string message, got {type(formatted)}"
    assert 'open' in formatted, "Expected message to mention open"
    assert error in formatted, "Expected message to include original error"
    assert 'macOS' in formatted, "Expected message to mention macOS"


def test_format_command_error_linux() -> None:
    """Test command error formatting for Linux.
    
    Validates: Requirements 10.5
    
    When a system command fails on Linux, the error message should
    provide Linux-specific context and installation suggestions.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Given a failed Linux command
    command = ['xdg-open', '/test/folder']
    error = "Command not found"
    
    # When formatting the error on Linux
    with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=False):
        with patch('src.email_signature.infrastructure.platform_utils.is_macos', return_value=False):
            with patch('src.email_signature.infrastructure.platform_utils.is_linux', return_value=True):
                formatted = ErrorMessageFormatter.format_command_error(command, error)
    
    # Then it should return a formatted error message with installation hints
    assert isinstance(formatted, str), f"Expected string message, got {type(formatted)}"
    assert 'xdg-open' in formatted, "Expected message to mention xdg-open"
    assert error in formatted, "Expected message to include original error"
    assert 'Linux' in formatted or 'apt' in formatted or 'xdg-utils' in formatted, \
        "Expected message to mention Linux or provide installation hints"


def test_format_path_error_with_permission_error() -> None:
    """Test path error formatting with PermissionError.
    
    Validates: Requirements 10.1, 10.2
    
    When a permission error occurs, the error message should be formatted
    appropriately with platform context.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Given a path and permission error
    test_path = Path("/test/restricted/file.txt")
    error = PermissionError("Permission denied")
    
    # When formatting the error
    formatted = ErrorMessageFormatter.format_path_error(test_path, error)
    
    # Then it should return a helpful message
    assert isinstance(formatted, str), f"Expected string message, got {type(formatted)}"
    assert str(test_path) in formatted, "Expected message to contain the path"
    assert 'permission' in formatted.lower(), \
        "Expected message to mention permission"
    
    # And it should mention the platform
    if is_windows():
        assert 'Windows' in formatted
    elif is_macos():
        assert 'macOS' in formatted
    elif is_linux():
        assert 'Linux' in formatted


def test_format_path_error_with_file_not_found() -> None:
    """Test path error formatting with FileNotFoundError.
    
    Validates: Requirements 10.1, 10.2
    
    When a file is not found, the error message should be formatted
    appropriately with platform context.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Given a path and file not found error
    test_path = Path("/test/nonexistent/file.txt")
    error = FileNotFoundError("File not found")
    
    # When formatting the error
    formatted = ErrorMessageFormatter.format_path_error(test_path, error)
    
    # Then it should return a helpful message
    assert isinstance(formatted, str), f"Expected string message, got {type(formatted)}"
    assert str(test_path) in formatted, "Expected message to contain the path"
    assert 'not found' in formatted.lower(), \
        "Expected message to mention 'not found'"
    
    # And it should mention the platform
    if is_windows():
        assert 'Windows' in formatted
    elif is_macos():
        assert 'macOS' in formatted
    elif is_linux():
        assert 'Linux' in formatted
