"""Platform detection and utility functions for cross-platform compatibility."""

import os
import platform
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_platform() -> str:
    """
    Returns the current platform name.
    
    Returns:
        str: 'windows', 'darwin', or 'linux'
    """
    return platform.system().lower()


def is_windows() -> bool:
    """
    Check if running on Windows.
    
    Returns:
        bool: True if running on Windows, False otherwise
    """
    return get_platform() == 'windows'


def is_macos() -> bool:
    """
    Check if running on macOS.
    
    Returns:
        bool: True if running on macOS, False otherwise
    """
    return get_platform() == 'darwin'


def is_linux() -> bool:
    """
    Check if running on Linux.
    
    Returns:
        bool: True if running on Linux, False otherwise
    """
    return get_platform() == 'linux'


def is_virtual_env() -> bool:
    """
    Check if running in a virtual environment.
    
    This detects both virtualenv and venv-based virtual environments.
    
    Returns:
        bool: True if running in a virtual environment, False otherwise
    """
    # Check for virtualenv (has real_prefix attribute)
    if hasattr(sys, 'real_prefix'):
        return True
    
    # Check for venv (base_prefix differs from prefix)
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        return True
    
    return False


def get_python_executable_name() -> str:
    """
    Get the platform-appropriate Python executable name.
    
    This returns the name of the Python executable that should be used
    on the current platform, taking into account whether we're in a
    virtual environment.
    
    Returns:
        str: Python executable name (e.g., 'python', 'python3', 'python.exe')
    """
    # If in a virtual environment, use 'python' (works on all platforms)
    if is_virtual_env():
        return 'python'
    
    # Platform-specific executable names
    if is_windows():
        # Windows uses python.exe or python3.exe
        return 'python.exe'
    else:
        # Unix-like systems typically use python3
        return 'python3'


def get_python_executable_path() -> Path:
    """
    Get the full path to the current Python executable.
    
    This returns the path to the Python interpreter that is currently
    running this code.
    
    Returns:
        Path: Full path to Python executable
    """
    return Path(sys.executable)


@dataclass
class PlatformInfo:
    """Information about the current platform."""
    
    system: str  # 'windows', 'darwin', or 'linux'
    version: str  # OS version
    python_version: str  # Python version
    is_virtual_env: bool  # Running in virtual environment
    temp_dir: Path  # Temporary directory
    font_dirs: List[Path]  # Font directories


class PathManager:
    """Handle all file path operations in a platform-independent manner."""
    
    @staticmethod
    def join(*components: str) -> Path:
        """
        Join path components using platform-native separators.
        
        Args:
            *components: Path components to join
            
        Returns:
            Path: Joined path with platform-native separators
        """
        if not components:
            return Path()
        
        # Start with the first component
        result = Path(components[0])
        
        # Join remaining components
        for component in components[1:]:
            result = result / component
        
        return result
    
    @staticmethod
    def normalize(path: str | Path) -> Path:
        """
        Normalize path to platform-native format.
        
        Args:
            path: Path to normalize (string or Path object)
            
        Returns:
            Path: Normalized path
        """
        return Path(path)
    
    @staticmethod
    def ensure_parent_dirs(file_path: Path) -> None:
        """
        Create parent directories if they don't exist.
        
        Args:
            file_path: File path whose parent directories should be created
        """
        parent = file_path.parent
        if parent != file_path:  # Avoid infinite loop for root paths
            parent.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def exists(path: Path) -> bool:
        """
        Check if path exists (handles both absolute and relative paths).
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path exists, False otherwise
        """
        return path.exists()
    
    @staticmethod
    def resolve_relative(path: Path, base: Path) -> Path:
        """
        Resolve relative path against base directory.
        
        Args:
            path: Path to resolve (can be absolute or relative)
            base: Base directory to resolve against
            
        Returns:
            Path: Resolved absolute path
        """
        if path.is_absolute():
            return path
        else:
            return (base / path).resolve()


class SystemCommandExecutor:
    """Execute platform-specific system commands."""
    
    @staticmethod
    def get_open_folder_command(folder_path: Path) -> List[str]:
        """
        Get platform-specific command to open folder in native file manager.
        
        Args:
            folder_path: Path to folder to open
            
        Returns:
            List[str]: Command and arguments to execute
        """
        path_str = str(folder_path)
        
        if is_windows():
            return ['explorer', path_str]
        elif is_macos():
            return ['open', path_str]
        elif is_linux():
            # Try xdg-open first, with fallbacks
            return ['xdg-open', path_str]
        else:
            # Unknown platform, try xdg-open as default
            return ['xdg-open', path_str]
    
    @staticmethod
    def get_linux_fallback_commands(folder_path: Path) -> List[List[str]]:
        """
        Get fallback commands for Linux file managers.
        
        Args:
            folder_path: Path to folder to open
            
        Returns:
            List[List[str]]: List of fallback commands to try
        """
        path_str = str(folder_path)
        return [
            ['gnome-open', path_str],
            ['kde-open', path_str],
        ]
    
    @staticmethod
    def execute_command(command: List[str]) -> Tuple[bool, str]:
        """
        Execute a system command and return success status.
        
        Args:
            command: Command and arguments to execute
            
        Returns:
            Tuple[bool, str]: (success, error_message)
                success: True if command executed successfully, False otherwise
                error_message: Error message if command failed, empty string otherwise
        """
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=10  # Prevent hanging
            )
            return True, ""
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with exit code {e.returncode}"
            if e.stderr:
                error_msg += f": {e.stderr.strip()}"
            return False, error_msg
        except FileNotFoundError:
            return False, f"Command not found: {command[0]}"
        except subprocess.TimeoutExpired:
            return False, f"Command timed out: {' '.join(command)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def open_folder(folder_path: Path) -> bool:
        """
        Open folder in native file manager with error handling and folder creation.
        
        This method:
        1. Creates the folder if it doesn't exist
        2. Attempts to open it with the platform-specific command
        3. On Linux, tries fallback commands if the primary command fails
        
        Args:
            folder_path: Path to folder to open
            
        Returns:
            bool: True if folder was opened successfully, False otherwise
        """
        # Create folder if it doesn't exist
        if not folder_path.exists():
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                # Failed to create folder, but continue to try opening
                # (in case it's a permission issue or race condition)
                pass
        
        # Get primary command
        command = SystemCommandExecutor.get_open_folder_command(folder_path)
        success, error = SystemCommandExecutor.execute_command(command)
        
        if success:
            return True
        
        # On Linux, try fallback commands
        if is_linux():
            fallback_commands = SystemCommandExecutor.get_linux_fallback_commands(folder_path)
            for fallback_command in fallback_commands:
                success, error = SystemCommandExecutor.execute_command(fallback_command)
                if success:
                    return True
        
        # All commands failed
        return False


class LineEndingHandler:
    """Handle different line ending conventions across platforms."""
    
    @staticmethod
    def normalize_line_endings(content: str) -> str:
        """
        Normalize line endings to Unix-style (\\n).
        
        This converts all line endings (\\r\\n, \\r, \\n) to Unix-style \\n.
        
        Args:
            content: Text content with any line ending style
            
        Returns:
            str: Content with normalized Unix-style line endings
        """
        # Replace Windows-style line endings (\\r\\n) first
        content = content.replace('\r\n', '\n')
        # Then replace old Mac-style line endings (\\r)
        content = content.replace('\r', '\n')
        return content
    
    @staticmethod
    def platform_line_endings(content: str) -> str:
        """
        Convert line endings to platform-native style.
        
        This converts Unix-style line endings to the platform's native format:
        - Windows: \\r\\n
        - Unix/Linux/macOS: \\n
        
        Args:
            content: Text content with Unix-style line endings
            
        Returns:
            str: Content with platform-native line endings
        """
        # First normalize to Unix-style
        content = LineEndingHandler.normalize_line_endings(content)
        
        # Convert to platform-native if needed
        if os.linesep != '\n':
            content = content.replace('\n', os.linesep)
        
        return content
    
    @staticmethod
    def read_text_universal(file_path: Path) -> str:
        """
        Read text file handling any line ending style.
        
        This uses Python's universal newline mode to handle any line ending
        style (\\n, \\r\\n, \\r) and converts them all to \\n.
        
        Args:
            file_path: Path to text file to read
            
        Returns:
            str: File content with normalized line endings
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        # Use newline=None (default) for universal newline mode
        # This automatically converts all line endings to \n
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def write_text_platform(file_path: Path, content: str) -> None:
        """
        Write text file with platform-native line endings.
        
        This writes the content with the platform's native line ending style:
        - Windows: \\r\\n
        - Unix/Linux/macOS: \\n
        
        Args:
            file_path: Path to text file to write
            content: Text content to write
            
        Raises:
            IOError: If file cannot be written
        """
        # Convert to platform-native line endings
        platform_content = LineEndingHandler.platform_line_endings(content)
        
        # Write with binary mode to preserve exact line endings
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(platform_content)


class FontLocator:
    """Locate fonts in platform-specific directories."""
    
    @staticmethod
    def get_font_directories() -> List[Path]:
        """
        Get platform-specific font directories.
        
        Returns:
            List[Path]: List of directories where fonts are typically located
        """
        directories = []
        
        if is_windows():
            # Windows font directories
            windows_fonts = Path(os.environ.get('WINDIR', 'C:\\Windows')) / 'Fonts'
            directories.append(windows_fonts)
            
            # User-specific fonts
            localappdata = os.environ.get('LOCALAPPDATA')
            if localappdata:
                user_fonts = Path(localappdata) / 'Microsoft' / 'Windows' / 'Fonts'
                directories.append(user_fonts)
        
        elif is_macos():
            # macOS font directories
            directories.extend([
                Path('/Library/Fonts'),
                Path('/System/Library/Fonts'),
                Path.home() / 'Library' / 'Fonts',
            ])
        
        elif is_linux():
            # Linux font directories
            directories.extend([
                Path('/usr/share/fonts'),
                Path('/usr/local/share/fonts'),
                Path.home() / '.fonts',
                Path.home() / '.local' / 'share' / 'fonts',
            ])
        
        # Filter to only existing directories
        return [d for d in directories if d.exists()]
    
    @staticmethod
    def find_font(font_name: str) -> Optional[Path]:
        """
        Search for font in platform-specific directories.
        
        This method searches for font files with common extensions (.ttf, .otf, .ttc)
        in platform-specific font directories.
        
        Args:
            font_name: Name of the font to find (with or without extension)
            
        Returns:
            Optional[Path]: Path to font file if found, None otherwise
        """
        # Common font file extensions
        extensions = ['.ttf', '.otf', '.ttc', '.TTF', '.OTF', '.TTC']
        
        # If font_name already has an extension, search for exact match
        if any(font_name.endswith(ext) for ext in extensions):
            search_names = [font_name]
        else:
            # Try all extensions
            search_names = [font_name + ext for ext in extensions]
        
        # Search in all font directories
        for directory in FontLocator.get_font_directories():
            for search_name in search_names:
                font_path = directory / search_name
                if font_path.exists():
                    return font_path
                
                # Also try case-insensitive search by listing directory
                try:
                    for file in directory.iterdir():
                        if file.name.lower() == search_name.lower():
                            return file
                except (PermissionError, OSError):
                    # Skip directories we can't read
                    continue
        
        return None
    
    @staticmethod
    def get_default_fonts() -> Dict[str, str]:
        """
        Get platform-appropriate default fonts.
        
        Returns:
            Dict[str, str]: Dictionary mapping font types to font names
                Keys: 'sans-serif', 'serif', 'monospace'
        """
        if is_windows():
            return {
                'sans-serif': 'Arial',
                'serif': 'Times New Roman',
                'monospace': 'Courier New',
            }
        elif is_macos():
            return {
                'sans-serif': 'Helvetica',
                'serif': 'Times',
                'monospace': 'Courier',
            }
        elif is_linux():
            return {
                'sans-serif': 'DejaVu Sans',
                'serif': 'DejaVu Serif',
                'monospace': 'DejaVu Sans Mono',
            }
        else:
            # Unknown platform, use common Linux fonts as fallback
            return {
                'sans-serif': 'DejaVu Sans',
                'serif': 'DejaVu Serif',
                'monospace': 'DejaVu Sans Mono',
            }
    
    @staticmethod
    def validate_font_path(font_path: Path) -> bool:
        """
        Validate font path according to platform conventions.
        
        This checks:
        1. Path exists
        2. Path points to a file (not a directory)
        3. File has a valid font extension
        
        Args:
            font_path: Path to font file to validate
            
        Returns:
            bool: True if font path is valid, False otherwise
        """
        # Check if path exists
        if not font_path.exists():
            return False
        
        # Check if it's a file
        if not font_path.is_file():
            return False
        
        # Check if it has a valid font extension
        valid_extensions = ['.ttf', '.otf', '.ttc', '.TTF', '.OTF', '.TTC']
        if not any(str(font_path).endswith(ext) for ext in valid_extensions):
            return False
        
        return True



class TempFileManager:
    """Manage temporary files using platform-appropriate directories."""
    
    # Class-level tracking of created temp files
    _tracked_files: List[Path] = []
    
    @staticmethod
    def get_temp_dir() -> Path:
        """
        Get platform-specific temporary directory.
        
        This uses the system's temporary directory as determined by Python's
        tempfile module, which respects platform conventions and environment
        variables (TMPDIR, TEMP, TMP).
        
        Returns:
            Path: Path to platform-specific temporary directory
        """
        return Path(tempfile.gettempdir())
    
    @staticmethod
    def create_temp_file(suffix: str = '', prefix: str = '') -> Path:
        """
        Create temporary file in platform temp directory.
        
        This creates a temporary file that is tracked for later cleanup.
        The file is created but not opened, and the caller is responsible
        for writing to it.
        
        Args:
            suffix: Optional suffix for the temp file (e.g., '.png')
            prefix: Optional prefix for the temp file (e.g., 'signature_')
            
        Returns:
            Path: Path to created temporary file
            
        Note:
            The created file is automatically tracked and can be cleaned up
            using cleanup_temp_files().
        """
        # Create a temporary file using NamedTemporaryFile
        # delete=False ensures the file persists after closing
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            prefix=prefix,
            delete=False,
            dir=TempFileManager.get_temp_dir()
        ) as temp_file:
            temp_path = Path(temp_file.name)
        
        # Track the file for cleanup
        TempFileManager._tracked_files.append(temp_path)
        
        return temp_path
    
    @staticmethod
    def cleanup_temp_files(pattern: str = '*') -> None:
        """
        Clean up temporary files matching pattern.
        
        This removes all tracked temporary files that match the given pattern.
        After cleanup, the files are removed from the tracking list.
        
        Args:
            pattern: Glob pattern to match files (default: '*' matches all)
                    Examples: '*.png', 'signature_*', 'temp_*.html'
        
        Note:
            This only cleans up files that were created by create_temp_file()
            and are still tracked. Files that were manually removed or never
            tracked will not be affected.
        """
        import fnmatch
        
        files_to_remove = []
        remaining_files = []
        
        for temp_file in TempFileManager._tracked_files:
            # Check if file matches pattern
            if fnmatch.fnmatch(temp_file.name, pattern):
                # Try to remove the file
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                    # Mark for removal from tracking list
                    files_to_remove.append(temp_file)
                except (PermissionError, OSError):
                    # If we can't remove it, keep tracking it
                    remaining_files.append(temp_file)
            else:
                # Doesn't match pattern, keep tracking it
                remaining_files.append(temp_file)
        
        # Update tracked files list
        TempFileManager._tracked_files = remaining_files
    
    @staticmethod
    def get_tracked_files() -> List[Path]:
        """
        Get list of currently tracked temporary files.
        
        Returns:
            List[Path]: List of paths to tracked temporary files
        """
        return TempFileManager._tracked_files.copy()
    
    @staticmethod
    def clear_tracking() -> None:
        """
        Clear the tracking list without deleting files.
        
        This is useful for testing or when you want to stop tracking files
        without actually deleting them.
        """
        TempFileManager._tracked_files = []


class ErrorMessageFormatter:
    """Format error messages with platform-specific information."""
    
    @staticmethod
    def format_path_error(path: Path, error: Exception) -> str:
        """
        Format path error with native path separators.
        
        This method formats error messages related to file paths, ensuring
        that the path is displayed using the platform's native separators
        and providing platform-appropriate context.
        
        Args:
            path: Path that caused the error
            error: Exception that was raised
            
        Returns:
            str: Formatted error message with platform-native path separators
        """
        # Convert path to string with native separators
        native_path = str(path)
        platform_name = get_platform()
        
        # Format platform name for display
        platform_display = {
            'windows': 'Windows',
            'darwin': 'macOS',
            'linux': 'Linux'
        }.get(platform_name, platform_name)
        
        # Format error message based on exception type
        if isinstance(error, PermissionError):
            return (f"Permission denied accessing '{native_path}'. "
                   f"On {platform_display}, check file permissions and ensure "
                   f"you have the necessary access rights.")
        elif isinstance(error, FileNotFoundError):
            return (f"File not found: '{native_path}'. "
                   f"Verify the path exists on your {platform_display} system.")
        elif isinstance(error, IsADirectoryError):
            return (f"Expected a file but found a directory: '{native_path}'. "
                   f"Please specify a file path.")
        elif isinstance(error, NotADirectoryError):
            return (f"Expected a directory but found a file: '{native_path}'. "
                   f"Please specify a directory path.")
        elif isinstance(error, OSError):
            return (f"Error accessing '{native_path}': {str(error)}. "
                   f"This may be a {platform_display}-specific issue.")
        else:
            return f"Error accessing '{native_path}': {str(error)}"
    
    @staticmethod
    def get_dependency_install_command(dependency: str) -> str:
        """
        Get platform-specific installation command for a dependency.
        
        This returns the appropriate command to install a Python package
        or system dependency based on the current platform.
        
        Args:
            dependency: Name of the dependency to install
            
        Returns:
            str: Platform-specific installation command
        """
        if is_windows():
            # Windows typically uses pip or python -m pip
            return f"pip install {dependency}"
        elif is_macos():
            # macOS can use pip3 or brew for system packages
            # Check if it looks like a Python package or system package
            if dependency.startswith('python3-') or dependency in ['tkinter', 'pillow']:
                return f"brew install {dependency}"
            else:
                return f"pip3 install {dependency}"
        elif is_linux():
            # Linux can use pip3 or apt/yum for system packages
            # Check if it looks like a system package
            if dependency.startswith('python3-'):
                return f"sudo apt install {dependency}"
            else:
                return f"pip3 install {dependency}"
        else:
            # Unknown platform, use generic pip command
            return f"pip install {dependency}"
    
    @staticmethod
    def get_font_location_hint() -> str:
        """
        Get platform-specific hint about font locations.
        
        This returns a helpful message indicating where fonts are typically
        located on the current platform.
        
        Returns:
            str: Platform-specific font location hint
        """
        if is_windows():
            return ("Fonts are typically located in:\n"
                   "  - C:\\Windows\\Fonts (system fonts)\n"
                   "  - %LOCALAPPDATA%\\Microsoft\\Windows\\Fonts (user fonts)\n"
                   "You can install fonts by right-clicking the font file and selecting 'Install'.")
        elif is_macos():
            return ("Fonts are typically located in:\n"
                   "  - /Library/Fonts (system fonts)\n"
                   "  - /System/Library/Fonts (macOS system fonts)\n"
                   "  - ~/Library/Fonts (user fonts)\n"
                   "You can install fonts using Font Book or by copying them to ~/Library/Fonts.")
        elif is_linux():
            return ("Fonts are typically located in:\n"
                   "  - /usr/share/fonts (system fonts)\n"
                   "  - /usr/local/share/fonts (locally installed fonts)\n"
                   "  - ~/.fonts or ~/.local/share/fonts (user fonts)\n"
                   "You can install fonts by copying them to ~/.local/share/fonts and running 'fc-cache -f'.")
        else:
            return ("Font locations vary by platform. "
                   "Please consult your operating system's documentation.")
    
    @staticmethod
    def format_command_error(command: List[str], error: str) -> str:
        """
        Format system command error with platform context.
        
        This formats error messages for failed system commands, providing
        platform-specific context and suggestions.
        
        Args:
            command: Command that failed (as list of strings)
            error: Error message from command execution
            
        Returns:
            str: Formatted error message with platform context
        """
        command_str = ' '.join(command)
        platform_name = get_platform()
        
        # Format platform name for display
        platform_display = {
            'windows': 'Windows',
            'darwin': 'macOS',
            'linux': 'Linux'
        }.get(platform_name, platform_name)
        
        # Provide platform-specific context
        base_message = f"Failed to execute command: {command_str}\n{error}"
        
        # Add platform-specific suggestions
        if is_windows():
            if 'explorer' in command:
                return (f"{base_message}\n\n"
                       f"On Windows, ensure Windows Explorer is available. "
                       f"This is a standard Windows component.")
        elif is_macos():
            if 'open' in command:
                return (f"{base_message}\n\n"
                       f"On macOS, the 'open' command should be available by default. "
                       f"Verify your macOS installation is not corrupted.")
        elif is_linux():
            if any(cmd in command for cmd in ['xdg-open', 'gnome-open', 'kde-open']):
                return (f"{base_message}\n\n"
                       f"On Linux, install a file manager or xdg-utils package:\n"
                       f"  - Ubuntu/Debian: sudo apt install xdg-utils\n"
                       f"  - Fedora: sudo dnf install xdg-utils\n"
                       f"  - Arch: sudo pacman -S xdg-utils")
        
        return f"{base_message}\n\nPlatform: {platform_display}"


class DependencyChecker:
    """Check for required dependencies with platform-specific error messages."""
    
    @staticmethod
    def check_pillow() -> Tuple[bool, str]:
        """
        Check if Pillow (PIL) is available.
        
        Returns:
            Tuple[bool, str]: (is_available, error_message)
                is_available: True if Pillow is available, False otherwise
                error_message: Empty string if available, installation instructions otherwise
        """
        try:
            import PIL
            return True, ""
        except ImportError:
            install_cmd = ErrorMessageFormatter.get_dependency_install_command('pillow')
            return False, (
                f"Pillow (PIL) is required but not installed.\n"
                f"Install it with: {install_cmd}"
            )
    
    @staticmethod
    def check_yaml() -> Tuple[bool, str]:
        """
        Check if PyYAML is available.
        
        Returns:
            Tuple[bool, str]: (is_available, error_message)
                is_available: True if PyYAML is available, False otherwise
                error_message: Empty string if available, installation instructions otherwise
        """
        try:
            import yaml
            return True, ""
        except ImportError:
            install_cmd = ErrorMessageFormatter.get_dependency_install_command('pyyaml')
            return False, (
                f"PyYAML is required but not installed.\n"
                f"Install it with: {install_cmd}"
            )
    
    @staticmethod
    def check_tkinter() -> Tuple[bool, str]:
        """
        Check if Tkinter is available.
        
        Returns:
            Tuple[bool, str]: (is_available, error_message)
                is_available: True if Tkinter is available, False otherwise
                error_message: Empty string if available, installation instructions otherwise
        """
        try:
            import tkinter as tk
            # Try to create a test instance to verify it works
            root = tk.Tk()
            root.withdraw()
            root.destroy()
            return True, ""
        except ImportError:
            if is_windows():
                return False, (
                    "Tkinter is not available. On Windows, Tkinter should be included\n"
                    "with Python. Try reinstalling Python and ensure 'tcl/tk and IDLE'\n"
                    "is selected during installation."
                )
            elif is_macos():
                return False, (
                    "Tkinter is not available. On macOS, you can install it with:\n"
                    "  brew install python-tk\n"
                    "Or reinstall Python with Tkinter support:\n"
                    "  brew reinstall python@3.x --with-tcl-tk"
                )
            else:  # Linux
                return False, (
                    "Tkinter is not available. On Linux, install it with:\n"
                    "  Ubuntu/Debian: sudo apt-get install python3-tk\n"
                    "  Fedora: sudo dnf install python3-tkinter\n"
                    "  Arch: sudo pacman -S tk"
                )
        except Exception:
            # Tkinter might be importable but not functional (e.g., no display)
            return False, "Tkinter is installed but not functional (no display available)."
    
    @staticmethod
    def check_all_dependencies() -> Tuple[bool, List[str]]:
        """
        Check all required dependencies.
        
        Returns:
            Tuple[bool, List[str]]: (all_available, error_messages)
                all_available: True if all dependencies are available, False otherwise
                error_messages: List of error messages for missing dependencies
        """
        errors = []
        
        # Check Pillow
        pillow_ok, pillow_error = DependencyChecker.check_pillow()
        if not pillow_ok:
            errors.append(pillow_error)
        
        # Check PyYAML
        yaml_ok, yaml_error = DependencyChecker.check_yaml()
        if not yaml_ok:
            errors.append(yaml_error)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def check_gui_dependencies() -> Tuple[bool, List[str]]:
        """
        Check dependencies required for GUI mode.
        
        Returns:
            Tuple[bool, List[str]]: (all_available, error_messages)
                all_available: True if all GUI dependencies are available, False otherwise
                error_messages: List of error messages for missing dependencies
        """
        # Check base dependencies first
        all_ok, errors = DependencyChecker.check_all_dependencies()
        
        # Check Tkinter
        tkinter_ok, tkinter_error = DependencyChecker.check_tkinter()
        if not tkinter_ok:
            errors.append(tkinter_error)
            all_ok = False
        
        return all_ok, errors
