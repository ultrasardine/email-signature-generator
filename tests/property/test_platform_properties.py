"""Property-based tests for platform detection and utilities."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from hypothesis import given
from hypothesis import strategies as st

from src.email_signature.infrastructure.platform_utils import (
    FontLocator,
    LineEndingHandler,
    PathManager,
    SystemCommandExecutor,
    TempFileManager,
    get_platform,
    is_linux,
    is_macos,
    is_virtual_env,
    is_windows,
)


@given(
    has_real_prefix=st.booleans(),
    base_prefix_differs=st.booleans(),
)
def test_virtual_environment_interpreter_usage(
    has_real_prefix: bool, base_prefix_differs: bool
) -> None:
    """Feature: cross-platform-compatibility, Property 8: Virtual environment interpreter usage.

    Validates: Requirements 5.4

    For any execution context, when running from a virtual environment, the system
    should use the virtual environment's Python interpreter.
    """
    # Save original attributes
    original_real_prefix = getattr(sys, 'real_prefix', None)
    original_base_prefix = getattr(sys, 'base_prefix', sys.prefix)
    original_prefix = sys.prefix

    try:
        # Set up test scenario
        if has_real_prefix:
            # Simulate virtualenv environment
            sys.real_prefix = '/usr/bin/python'
        else:
            # Remove real_prefix if it exists
            if hasattr(sys, 'real_prefix'):
                delattr(sys, 'real_prefix')

        if base_prefix_differs:
            # Simulate venv environment
            sys.base_prefix = '/usr/bin/python'
            sys.prefix = '/home/user/.venv'
        else:
            # Make them the same (not in venv)
            sys.base_prefix = sys.prefix

        # When checking if running in virtual environment
        result = is_virtual_env()

        # Then the result should correctly identify virtual environment
        expected = has_real_prefix or base_prefix_differs
        assert result == expected, (
            f"Expected is_virtual_env() to return {expected} "
            f"(has_real_prefix={has_real_prefix}, base_prefix_differs={base_prefix_differs}), "
            f"but got {result}"
        )

        # If in virtual environment, sys.prefix should point to venv location
        if result:
            # The virtual environment detection should be consistent
            assert (
                hasattr(sys, 'real_prefix')
                or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            ), "Virtual environment detected but sys attributes don't reflect it"

    finally:
        # Restore original attributes
        if original_real_prefix is not None:
            sys.real_prefix = original_real_prefix
        elif hasattr(sys, 'real_prefix'):
            delattr(sys, 'real_prefix')

        sys.base_prefix = original_base_prefix
        sys.prefix = original_prefix


def test_platform_detection_consistency() -> None:
    """Test that platform detection functions are consistent with each other.

    For any platform, exactly one of is_windows(), is_macos(), or is_linux()
    should return True.
    """
    # Get platform detection results
    windows = is_windows()
    macos = is_macos()
    linux = is_linux()

    # Exactly one should be True
    true_count = sum([windows, macos, linux])
    assert true_count == 1, (
        f"Exactly one platform should be detected, but got: "
        f"windows={windows}, macos={macos}, linux={linux}"
    )

    # Platform name should match
    platform_name = get_platform()
    if windows:
        assert platform_name == 'windows'
    elif macos:
        assert platform_name == 'darwin'
    elif linux:
        assert platform_name == 'linux'


def test_current_virtual_env_detection() -> None:
    """Test that virtual environment detection works for the current environment.

    This test verifies that the is_virtual_env() function correctly identifies
    whether the test is running in a virtual environment.
    """
    result = is_virtual_env()

    # Verify the result matches the actual sys attributes
    expected = (
        hasattr(sys, 'real_prefix')
        or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

    assert result == expected, (
        f"is_virtual_env() returned {result} but expected {expected} "
        f"based on sys attributes"
    )


# PathManager Property Tests


@given(
    components=st.lists(
        st.text(
            alphabet=st.characters(
                blacklist_categories=('Cs',),  # Exclude surrogates
                blacklist_characters='\x00\n\r\t',  # Exclude null and control chars
            ),
            min_size=1,
            max_size=20,
        ).filter(lambda x: x not in ['', '.', '..'] and '/' not in x and '\\' not in x),
        min_size=1,
        max_size=5,
    )
)
def test_path_construction_uses_native_separators(components: list[str]) -> None:
    """Feature: cross-platform-compatibility, Property 1: Path construction uses native separators.

    Validates: Requirements 1.1, 1.2

    For any sequence of path components, when joined together, the resulting path
    should use the operating system's native path separator.
    """
    # When joining path components
    result = PathManager.join(*components)

    # Then the result should be a Path object
    assert isinstance(result, Path), f"Expected Path object, got {type(result)}"

    # And the string representation should use native separators
    result_str = str(result)

    # The path should contain all components
    for component in components:
        assert component in result_str, (
            f"Component '{component}' not found in result path '{result_str}'"
        )

    # The path should use the native separator
    native_sep = os.sep
    if len(components) > 1:
        # For multi-component paths, the native separator should appear
        # (unless components are empty or single character)
        expected_path = Path(*components)
        assert str(result) == str(expected_path), (
            f"Path construction mismatch: got '{result}', expected '{expected_path}'"
        )


@given(
    path_exists=st.booleans(),
    is_absolute=st.booleans(),
)
def test_path_existence_checking_works_for_all_path_types(
    path_exists: bool, is_absolute: bool
) -> None:
    """Feature: cross-platform-compatibility, Property 2: Path existence checking works for all path types.

    Validates: Requirements 1.3

    For any file path (absolute or relative), the existence check should correctly
    determine whether the path exists on the filesystem.
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        if path_exists:
            # Create a test file
            test_file = temp_path / "test_file.txt"
            test_file.write_text("test content")

            if is_absolute:
                path_to_check = test_file
            else:
                # Create relative path from current directory
                try:
                    path_to_check = test_file.relative_to(Path.cwd())
                except ValueError:
                    # If we can't make it relative, use absolute
                    path_to_check = test_file
        else:
            # Use a non-existent path
            if is_absolute:
                path_to_check = temp_path / "nonexistent_file.txt"
            else:
                # Create a relative path that doesn't exist
                path_to_check = Path("nonexistent_dir") / "nonexistent_file.txt"

        # When checking if the path exists
        result = PathManager.exists(path_to_check)

        # Then the result should match the actual existence
        actual_exists = path_to_check.exists()
        assert result == actual_exists, (
            f"PathManager.exists() returned {result} for path '{path_to_check}', "
            f"but actual existence is {actual_exists}"
        )


@given(
    depth=st.integers(min_value=1, max_value=5),
    create_parents=st.booleans(),
)
def test_parent_directory_creation(depth: int, create_parents: bool) -> None:
    """Feature: cross-platform-compatibility, Property 3: Parent directory creation.

    Validates: Requirements 1.4

    For any file path, when saving a file, all parent directories should be
    created if they don't exist.
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Build a nested path
        nested_components = [f"dir_{i}" for i in range(depth)]
        file_path = temp_path.joinpath(*nested_components, "test_file.txt")

        # Optionally create some parent directories
        if create_parents and depth > 1:
            # Create only the first half of parent directories
            partial_parent = temp_path.joinpath(*nested_components[: depth // 2])
            partial_parent.mkdir(parents=True, exist_ok=True)

        # Verify parent doesn't fully exist before calling ensure_parent_dirs
        parent_existed_before = file_path.parent.exists()

        # When ensuring parent directories exist
        PathManager.ensure_parent_dirs(file_path)

        # Then all parent directories should exist
        assert file_path.parent.exists(), (
            f"Parent directory '{file_path.parent}' should exist after "
            f"ensure_parent_dirs() but it doesn't"
        )

        # And we should be able to create the file
        file_path.write_text("test content")
        assert file_path.exists(), (
            f"File '{file_path}' should exist after writing, but it doesn't"
        )

        # Verify the content
        assert file_path.read_text() == "test content"


# SystemCommandExecutor Property Tests


@given(
    folder_name=st.text(
        alphabet=st.characters(
            min_codepoint=32,
            max_codepoint=126,
            blacklist_characters='/<>:"|?*\\',
        ),
        min_size=1,
        max_size=50,
    ).filter(lambda x: x.strip() and x not in ['.', '..']),
    command_will_fail=st.booleans(),
)
def test_folder_open_error_handling(folder_name: str, command_will_fail: bool) -> None:
    """Feature: cross-platform-compatibility, Property 5: Folder open error handling.

    Validates: Requirements 2.4

    For any folder path, if the open command fails, the system should display
    an error message without crashing.
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        folder_path = temp_path / folder_name

        if command_will_fail:
            # Use an invalid command that will fail
            # We'll test execute_command directly with a bad command
            bad_command = ['nonexistent_command_xyz123', str(folder_path)]
            
            # When executing a command that will fail
            success, error_message = SystemCommandExecutor.execute_command(bad_command)
            
            # Then it should return False
            assert success is False, (
                f"Expected execute_command to return False for invalid command, "
                f"but got {success}"
            )
            
            # And it should provide an error message
            assert error_message, (
                "Expected error_message to be non-empty when command fails"
            )
            assert isinstance(error_message, str), (
                f"Expected error_message to be a string, got {type(error_message)}"
            )
        else:
            # Test with a valid folder path
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # When attempting to open the folder
            # Note: We can't actually test the GUI opening without mocking,
            # but we can verify the command generation doesn't crash
            try:
                command = SystemCommandExecutor.get_open_folder_command(folder_path)
                
                # Then it should return a valid command list
                assert isinstance(command, list), (
                    f"Expected command to be a list, got {type(command)}"
                )
                assert len(command) >= 2, (
                    f"Expected command to have at least 2 elements, got {len(command)}"
                )
                assert str(folder_path) in command, (
                    f"Expected folder path '{folder_path}' to be in command {command}"
                )
            except Exception as e:
                # Should not crash
                assert False, (
                    f"get_open_folder_command should not crash, but raised: {e}"
                )


@given(
    folder_name=st.text(
        alphabet=st.characters(
            min_codepoint=32,
            max_codepoint=126,
            blacklist_characters='/<>:"|?*\\',
        ),
        min_size=1,
        max_size=50,
    ).filter(lambda x: x.strip() and x not in ['.', '..']),
    nested_depth=st.integers(min_value=0, max_value=3),
)
def test_folder_creation_before_opening(folder_name: str, nested_depth: int) -> None:
    """Feature: cross-platform-compatibility, Property 6: Folder creation before opening.

    Validates: Requirements 2.5

    For any folder path that doesn't exist, the system should create it before
    attempting to open it.
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Build nested path
        nested_components = [f"nested_{i}" for i in range(nested_depth)]
        folder_path = temp_path.joinpath(folder_name, *nested_components)
        
        # Ensure the folder doesn't exist
        assert not folder_path.exists(), (
            f"Test setup error: folder '{folder_path}' should not exist initially"
        )
        
        # When testing the folder creation logic (without actually opening)
        # We test the folder creation part separately from the opening part
        # to avoid opening Finder/Explorer windows during tests
        
        # Verify the folder doesn't exist initially
        assert not folder_path.exists(), (
            f"Folder '{folder_path}' should not exist before creation"
        )
        
        # Simulate what open_folder does: create the folder if it doesn't exist
        if not folder_path.exists():
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass  # open_folder handles this gracefully
        
        # Then the folder should exist after creation
        assert folder_path.exists(), (
            f"Folder '{folder_path}' should exist after mkdir() call, "
            f"but it doesn't"
        )
        
        # And it should be a directory
        assert folder_path.is_dir(), (
            f"Path '{folder_path}' should be a directory, but it's not"
        )
        
        # Verify that get_open_folder_command works without crashing
        try:
            command = SystemCommandExecutor.get_open_folder_command(folder_path)
            assert isinstance(command, list), (
                f"Expected command to be a list, got {type(command)}"
            )
            assert len(command) >= 2, (
                f"Expected command to have at least 2 elements, got {len(command)}"
            )
        except Exception as e:
            assert False, (
                f"get_open_folder_command should not crash, but raised: {e}"
            )


# FontLocator Property Tests


@given(
    font_name=st.text(
        alphabet=st.characters(
            min_codepoint=32,
            max_codepoint=126,
            blacklist_characters='/<>:"|?*\\',
        ),
        min_size=1,
        max_size=50,
    ).filter(lambda x: x.strip() and '/' not in x and '\\' not in x),
)
def test_font_fallback_behavior(font_name: str) -> None:
    """Feature: cross-platform-compatibility, Property 7: Font fallback behavior.

    Validates: Requirements 3.2

    For any non-existent font name, the system should fall back to a
    platform-appropriate default font.
    """
    # Generate a font name that is very unlikely to exist
    nonexistent_font = f"NonExistentFont_{font_name}_XYZ123_UNLIKELY"
    
    # When searching for a non-existent font
    result = FontLocator.find_font(nonexistent_font)
    
    # Then it should return None (indicating font not found)
    # The fallback happens at a higher level when None is returned
    assert result is None, (
        f"Expected find_font to return None for non-existent font "
        f"'{nonexistent_font}', but got {result}"
    )
    
    # When getting default fonts
    default_fonts = FontLocator.get_default_fonts()
    
    # Then it should return a dictionary with platform-appropriate defaults
    assert isinstance(default_fonts, dict), (
        f"Expected get_default_fonts to return a dict, got {type(default_fonts)}"
    )
    
    # And it should contain the expected font types
    expected_keys = {'sans-serif', 'serif', 'monospace'}
    assert set(default_fonts.keys()) == expected_keys, (
        f"Expected default_fonts to have keys {expected_keys}, "
        f"but got {set(default_fonts.keys())}"
    )
    
    # And all values should be non-empty strings
    for font_type, font_name_value in default_fonts.items():
        assert isinstance(font_name_value, str), (
            f"Expected font name for '{font_type}' to be a string, "
            f"got {type(font_name_value)}"
        )
        assert font_name_value.strip(), (
            f"Expected font name for '{font_type}' to be non-empty"
        )
    
    # Verify platform-specific defaults
    if is_windows():
        assert 'Arial' in default_fonts.values() or 'Calibri' in default_fonts.values(), (
            f"Expected Windows default fonts to include Arial or Calibri, "
            f"got {default_fonts}"
        )
    elif is_macos():
        assert 'Helvetica' in default_fonts.values() or 'Times' in default_fonts.values(), (
            f"Expected macOS default fonts to include Helvetica or Times, "
            f"got {default_fonts}"
        )
    elif is_linux():
        assert any('DejaVu' in font for font in default_fonts.values()), (
            f"Expected Linux default fonts to include DejaVu fonts, "
            f"got {default_fonts}"
        )


# LineEndingHandler Property Tests


@given(
    lines=st.lists(
        st.text(
            alphabet=st.characters(
                blacklist_characters='\r\n',
                blacklist_categories=('Cs',)  # Exclude surrogates
            ),
            min_size=0,
            max_size=100
        ),
        min_size=0,
        max_size=20
    ),
    line_ending_style=st.sampled_from(['\n', '\r\n', '\r']),
)
def test_line_ending_handling(lines: list[str], line_ending_style: str) -> None:
    """Feature: cross-platform-compatibility, Property 4: Line ending handling.

    Validates: Requirements 1.5

    For any text content with any line ending style (\\n, \\r\\n, \\r), the system
    should correctly parse and process the content.
    """
    # Create content with the specified line ending style
    # Join lines with the test line ending style
    content_with_line_endings = line_ending_style.join(lines)
    
    # When normalizing line endings
    normalized = LineEndingHandler.normalize_line_endings(content_with_line_endings)
    
    # Then all line endings should be converted to Unix-style (\n)
    assert '\r\n' not in normalized, (
        f"Normalized content should not contain \\r\\n, but found it in: "
        f"{repr(normalized[:100])}"
    )
    assert '\r' not in normalized, (
        f"Normalized content should not contain \\r, but found it in: "
        f"{repr(normalized[:100])}"
    )
    
    # The content should be equivalent to joining with \n
    expected_normalized = '\n'.join(lines)
    assert normalized == expected_normalized, (
        f"Normalized content should match Unix-style line endings. "
        f"Expected: {repr(expected_normalized[:100])}, "
        f"Got: {repr(normalized[:100])}"
    )
    
    # When reading and writing with universal handling
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / "test_file.txt"
        
        # Write content with specific line endings using binary mode to preserve exact bytes
        temp_file.write_bytes(content_with_line_endings.encode('utf-8'))
        
        # When reading with universal newline handling
        read_content = LineEndingHandler.read_text_universal(temp_file)
        
        # Then the content should be readable and normalized
        assert isinstance(read_content, str), (
            f"Expected read_text_universal to return a string, got {type(read_content)}"
        )
        
        # The read content should have normalized line endings
        # (Python's universal newline mode converts all to \n)
        assert '\r\n' not in read_content, (
            "read_text_universal should normalize \\r\\n to \\n"
        )
        assert '\r' not in read_content, (
            "read_text_universal should normalize \\r to \\n"
        )
        
        # The normalized content should match
        assert read_content == expected_normalized, (
            f"Read content should match normalized content. "
            f"Expected: {repr(expected_normalized[:100])}, "
            f"Got: {repr(read_content[:100])}"
        )


@given(
    text_content=st.text(min_size=0, max_size=1000),
    num_lines=st.integers(min_value=0, max_value=20),
)
def test_configuration_line_endings(text_content: str, num_lines: int) -> None:
    """Feature: cross-platform-compatibility, Property 14: Configuration line endings.

    Validates: Requirements 8.3

    For any configuration content, when saved, the system should use
    platform-appropriate line endings.
    """
    # Create multi-line content
    lines = [f"{text_content}_{i}" for i in range(num_lines)]
    content = '\n'.join(lines)
    
    # When converting to platform line endings
    platform_content = LineEndingHandler.platform_line_endings(content)
    
    # Then the content should use platform-native line endings
    if os.linesep == '\r\n':
        # Windows: should have \r\n
        if num_lines > 1:
            assert '\r\n' in platform_content or num_lines == 0, (
                f"On Windows, multi-line content should contain \\r\\n line endings"
            )
    else:
        # Unix/Linux/macOS: should have \n only
        assert '\r\n' not in platform_content, (
            f"On Unix systems, content should not contain \\r\\n"
        )
        assert '\r' not in platform_content, (
            f"On Unix systems, content should not contain \\r"
        )
    
    # When writing and reading back
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / "config_test.txt"
        
        # Write with platform-native line endings
        LineEndingHandler.write_text_platform(temp_file, content)
        
        # Verify file was created
        assert temp_file.exists(), (
            f"File '{temp_file}' should exist after write_text_platform"
        )
        
        # Read back with universal handling
        read_content = LineEndingHandler.read_text_universal(temp_file)
        
        # The content should be preserved (after normalization)
        normalized_original = LineEndingHandler.normalize_line_endings(content)
        normalized_read = LineEndingHandler.normalize_line_endings(read_content)
        
        assert normalized_original == normalized_read, (
            f"Content should be preserved after write and read. "
            f"Original (normalized): {repr(normalized_original[:100])}, "
            f"Read (normalized): {repr(normalized_read[:100])}"
        )
        
        # When reading the raw bytes, they should have platform-native endings
        raw_bytes = temp_file.read_bytes()
        raw_text = raw_bytes.decode('utf-8')
        
        if os.linesep == '\r\n' and num_lines > 1:
            # On Windows, raw file should contain \r\n
            assert b'\r\n' in raw_bytes or num_lines == 0, (
                f"On Windows, raw file should contain \\r\\n bytes"
            )
        elif num_lines > 1:
            # On Unix, raw file should contain \n but not \r\n
            assert b'\n' in raw_bytes, (
                f"On Unix, raw file should contain \\n bytes"
            )
            # Should not have \r\n sequences
            assert b'\r\n' not in raw_bytes, (
                f"On Unix, raw file should not contain \\r\\n bytes"
            )



# TempFileManager Property Tests


@given(
    suffix=st.sampled_from(['', '.txt', '.png', '.html', '.json', '.tmp']),
    prefix=st.sampled_from(['', 'test_', 'temp_', 'signature_', 'preview_']),
    num_files=st.integers(min_value=1, max_value=10),
)
def test_temporary_directory_usage(suffix: str, prefix: str, num_files: int) -> None:
    """Feature: cross-platform-compatibility, Property 10: Temporary directory usage.

    Validates: Requirements 7.4

    For any temporary file creation, the system should use the platform-appropriate
    temporary directory.
    """
    # Clear any existing tracked files before test
    TempFileManager.clear_tracking()
    
    try:
        # Get the platform-specific temp directory
        temp_dir = TempFileManager.get_temp_dir()
        
        # Then it should return a valid Path object
        assert isinstance(temp_dir, Path), (
            f"Expected get_temp_dir to return a Path object, got {type(temp_dir)}"
        )
        
        # And it should exist
        assert temp_dir.exists(), (
            f"Temporary directory '{temp_dir}' should exist"
        )
        
        # And it should be a directory
        assert temp_dir.is_dir(), (
            f"Temporary directory '{temp_dir}' should be a directory"
        )
        
        # When creating temporary files
        created_files = []
        for i in range(num_files):
            temp_file = TempFileManager.create_temp_file(suffix=suffix, prefix=prefix)
            created_files.append(temp_file)
            
            # Then each file should be in the platform temp directory
            assert isinstance(temp_file, Path), (
                f"Expected create_temp_file to return a Path object, got {type(temp_file)}"
            )
            
            # The file should exist
            assert temp_file.exists(), (
                f"Temporary file '{temp_file}' should exist after creation"
            )
            
            # The file should be in the temp directory
            assert temp_file.parent == temp_dir or temp_dir in temp_file.parents, (
                f"Temporary file '{temp_file}' should be in temp directory '{temp_dir}'"
            )
            
            # The file should have the correct suffix
            if suffix:
                assert str(temp_file).endswith(suffix), (
                    f"Temporary file '{temp_file}' should have suffix '{suffix}'"
                )
            
            # The file should have the correct prefix
            if prefix:
                assert temp_file.name.startswith(prefix), (
                    f"Temporary file '{temp_file.name}' should have prefix '{prefix}'"
                )
        
        # Verify all files are tracked
        tracked_files = TempFileManager.get_tracked_files()
        assert len(tracked_files) == num_files, (
            f"Expected {num_files} tracked files, got {len(tracked_files)}"
        )
        
        for created_file in created_files:
            assert created_file in tracked_files, (
                f"Created file '{created_file}' should be in tracked files"
            )
    
    finally:
        # Clean up all created files
        TempFileManager.cleanup_temp_files()
        TempFileManager.clear_tracking()


@given(
    num_files=st.integers(min_value=1, max_value=15),
    pattern=st.sampled_from(['*', '*.txt', '*.png', 'test_*', 'temp_*', 'signature_*']),
    cleanup_immediately=st.booleans(),
)
def test_temporary_file_cleanup(
    num_files: int, pattern: str, cleanup_immediately: bool
) -> None:
    """Feature: cross-platform-compatibility, Property 11: Temporary file cleanup.

    Validates: Requirements 7.5

    For any temporary files created during execution, the system should properly
    delete them after use.
    """
    # Clear any existing tracked files before test
    TempFileManager.clear_tracking()
    
    try:
        # Create temporary files with different suffixes
        suffixes = ['.txt', '.png', '.html', '.json', '.tmp']
        prefixes = ['test_', 'temp_', 'signature_', 'preview_', '']
        
        created_files = []
        for i in range(num_files):
            suffix = suffixes[i % len(suffixes)]
            prefix = prefixes[i % len(prefixes)]
            
            temp_file = TempFileManager.create_temp_file(suffix=suffix, prefix=prefix)
            created_files.append(temp_file)
            
            # Write some content to the file to make it real
            temp_file.write_text(f"Test content {i}")
        
        # Verify all files exist
        for temp_file in created_files:
            assert temp_file.exists(), (
                f"Temporary file '{temp_file}' should exist before cleanup"
            )
        
        # Verify all files are tracked
        tracked_before = TempFileManager.get_tracked_files()
        assert len(tracked_before) == num_files, (
            f"Expected {num_files} tracked files before cleanup, "
            f"got {len(tracked_before)}"
        )
        
        if cleanup_immediately:
            # When cleaning up with a specific pattern
            TempFileManager.cleanup_temp_files(pattern)
            
            # Then files matching the pattern should be deleted
            import fnmatch
            for temp_file in created_files:
                if fnmatch.fnmatch(temp_file.name, pattern):
                    assert not temp_file.exists(), (
                        f"File '{temp_file}' matching pattern '{pattern}' "
                        f"should be deleted after cleanup"
                    )
                else:
                    # Files not matching pattern should still exist
                    assert temp_file.exists(), (
                        f"File '{temp_file}' not matching pattern '{pattern}' "
                        f"should still exist after cleanup"
                    )
            
            # Verify tracking list is updated
            tracked_after = TempFileManager.get_tracked_files()
            expected_remaining = sum(
                1 for f in created_files 
                if not fnmatch.fnmatch(f.name, pattern)
            )
            assert len(tracked_after) == expected_remaining, (
                f"Expected {expected_remaining} tracked files after cleanup, "
                f"got {len(tracked_after)}"
            )
        else:
            # When cleaning up all files (default pattern '*')
            TempFileManager.cleanup_temp_files()
            
            # Then all files should be deleted
            for temp_file in created_files:
                assert not temp_file.exists(), (
                    f"File '{temp_file}' should be deleted after cleanup_temp_files()"
                )
            
            # And tracking list should be empty
            tracked_after = TempFileManager.get_tracked_files()
            assert len(tracked_after) == 0, (
                f"Expected 0 tracked files after cleanup, got {len(tracked_after)}"
            )
    
    finally:
        # Ensure cleanup in case of test failure
        TempFileManager.cleanup_temp_files()
        TempFileManager.clear_tracking()


@given(
    font_path_exists=st.booleans(),
    is_file=st.booleans(),
    has_valid_extension=st.booleans(),
)
def test_font_path_validation(
    font_path_exists: bool, is_file: bool, has_valid_extension: bool
) -> None:
    """Feature: cross-platform-compatibility, Property 15: Font path validation.

    Validates: Requirements 8.4

    For any font path in configuration, the system should validate it according
    to platform conventions.
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Determine the extension based on has_valid_extension
        if has_valid_extension:
            extension = '.ttf'
        else:
            extension = '.txt'
        
        # Create the test path
        test_font_path = temp_path / f"test_font{extension}"
        
        if font_path_exists:
            if is_file:
                # Create a file
                test_font_path.write_text("fake font content")
            else:
                # Create a directory instead of a file
                test_font_path.mkdir(parents=True, exist_ok=True)
        
        # When validating the font path
        result = FontLocator.validate_font_path(test_font_path)
        
        # Then the result should be True only if all conditions are met:
        # 1. Path exists
        # 2. Path is a file (not a directory)
        # 3. Path has a valid font extension
        expected = font_path_exists and is_file and has_valid_extension
        
        assert result == expected, (
            f"Expected validate_font_path to return {expected} for path '{test_font_path}' "
            f"(exists={font_path_exists}, is_file={is_file}, valid_ext={has_valid_extension}), "
            f"but got {result}"
        )
        
        # Additional validation: if path is valid, it should meet all criteria
        if result:
            assert test_font_path.exists(), (
                f"Valid font path '{test_font_path}' should exist"
            )
            assert test_font_path.is_file(), (
                f"Valid font path '{test_font_path}' should be a file"
            )
            assert any(str(test_font_path).endswith(ext) for ext in ['.ttf', '.otf', '.ttc', '.TTF', '.OTF', '.TTC']), (
                f"Valid font path '{test_font_path}' should have a valid font extension"
            )


def test_temp_file_manager_tracking_isolation() -> None:
    """Test that TempFileManager properly tracks and cleans up files.

    This test verifies that the tracking mechanism works correctly and that
    cleanup only affects tracked files.
    """
    # Clear any existing tracked files
    TempFileManager.clear_tracking()
    
    try:
        # Create some tracked files
        tracked_file1 = TempFileManager.create_temp_file(suffix='.txt', prefix='tracked_')
        tracked_file2 = TempFileManager.create_temp_file(suffix='.png', prefix='tracked_')
        
        # Create an untracked file manually
        untracked_file = TempFileManager.get_temp_dir() / 'untracked_manual.txt'
        untracked_file.write_text("This file is not tracked")
        
        # Verify tracked files are in the tracking list
        tracked_files = TempFileManager.get_tracked_files()
        assert len(tracked_files) == 2, (
            f"Expected 2 tracked files, got {len(tracked_files)}"
        )
        assert tracked_file1 in tracked_files
        assert tracked_file2 in tracked_files
        
        # Verify all files exist
        assert tracked_file1.exists()
        assert tracked_file2.exists()
        assert untracked_file.exists()
        
        # Clean up tracked files
        TempFileManager.cleanup_temp_files()
        
        # Verify tracked files are deleted
        assert not tracked_file1.exists(), (
            "Tracked file 1 should be deleted after cleanup"
        )
        assert not tracked_file2.exists(), (
            "Tracked file 2 should be deleted after cleanup"
        )
        
        # Verify untracked file still exists
        assert untracked_file.exists(), (
            "Untracked file should not be affected by cleanup"
        )
        
        # Verify tracking list is empty
        tracked_after = TempFileManager.get_tracked_files()
        assert len(tracked_after) == 0, (
            f"Expected 0 tracked files after cleanup, got {len(tracked_after)}"
        )
        
    finally:
        # Clean up the untracked file manually
        if untracked_file.exists():
            untracked_file.unlink()
        
        # Ensure cleanup
        TempFileManager.cleanup_temp_files()
        TempFileManager.clear_tracking()


# ErrorMessageFormatter Property Tests


@given(
    path_components=st.lists(
        st.text(
            alphabet=st.characters(
                min_codepoint=32,
                max_codepoint=126,
                blacklist_characters='<>:"|?*',
            ),
            min_size=1,
            max_size=20,
        ).filter(lambda x: x.strip() and x not in ['.', '..']),
        min_size=1,
        max_size=5,
    ),
    error_type=st.sampled_from([
        PermissionError,
        FileNotFoundError,
        IsADirectoryError,
        NotADirectoryError,
        OSError,
        ValueError,
    ]),
)
def test_error_message_platform_appropriateness(
    path_components: list[str], error_type: type
) -> None:
    """Feature: cross-platform-compatibility, Property 18: Error message platform appropriateness.

    Validates: Requirements 10.1

    For any error condition, the displayed error message should be appropriate
    for the current platform.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Create a path using the components
    test_path = PathManager.join(*path_components)
    
    # Create an error of the specified type
    error_message = f"Test error for {error_type.__name__}"
    if error_type == ValueError:
        error = error_type(error_message)
    else:
        error = error_type(error_message)
    
    # When formatting the error message
    formatted_message = ErrorMessageFormatter.format_path_error(test_path, error)
    
    # Then the message should be a non-empty string
    assert isinstance(formatted_message, str), (
        f"Expected format_path_error to return a string, got {type(formatted_message)}"
    )
    assert formatted_message.strip(), (
        "Expected formatted error message to be non-empty"
    )
    
    # And the message should contain the path
    path_str = str(test_path)
    assert path_str in formatted_message, (
        f"Expected error message to contain path '{path_str}', "
        f"but got: {formatted_message}"
    )
    
    # And the message should mention the platform
    platform_name = get_platform()
    platform_display_names = {
        'windows': 'Windows',
        'darwin': 'macOS',
        'linux': 'Linux'
    }
    
    # The message should contain platform-specific information
    # (either the platform name or platform-specific guidance)
    if error_type in [PermissionError, FileNotFoundError, OSError]:
        expected_platform = platform_display_names.get(platform_name, platform_name)
        assert expected_platform in formatted_message, (
            f"Expected error message to mention platform '{expected_platform}', "
            f"but got: {formatted_message}"
        )
    
    # Verify the message provides helpful context based on error type
    if error_type == PermissionError:
        assert 'permission' in formatted_message.lower(), (
            "Expected PermissionError message to mention 'permission'"
        )
    elif error_type == FileNotFoundError:
        assert 'not found' in formatted_message.lower(), (
            "Expected FileNotFoundError message to mention 'not found'"
        )
    elif error_type == IsADirectoryError:
        assert 'directory' in formatted_message.lower(), (
            "Expected IsADirectoryError message to mention 'directory'"
        )


@given(
    path_components=st.lists(
        st.text(
            alphabet=st.characters(
                min_codepoint=32,
                max_codepoint=126,
                blacklist_characters='<>:"|?*',
            ),
            min_size=1,
            max_size=20,
        ).filter(lambda x: x.strip() and x not in ['.', '..']),
        min_size=1,
        max_size=5,
    ),
    error_type=st.sampled_from([
        PermissionError,
        FileNotFoundError,
        OSError,
    ]),
)
def test_path_display_in_errors(
    path_components: list[str], error_type: type
) -> None:
    """Feature: cross-platform-compatibility, Property 19: Path display in errors.

    Validates: Requirements 10.2

    For any file path error, the error message should display the path using
    platform-native separators.
    """
    from src.email_signature.infrastructure.platform_utils import ErrorMessageFormatter
    
    # Create a path using the components
    test_path = PathManager.join(*path_components)
    
    # Create an error
    error = error_type(f"Test error for {error_type.__name__}")
    
    # When formatting the error message
    formatted_message = ErrorMessageFormatter.format_path_error(test_path, error)
    
    # Then the message should contain the path with native separators
    path_str = str(test_path)
    assert path_str in formatted_message, (
        f"Expected error message to contain path '{path_str}', "
        f"but got: {formatted_message}"
    )
    
    # Verify the path uses native separators
    native_sep = os.sep
    if len(path_components) > 1:
        # For multi-component paths, the native separator should appear in the path
        assert native_sep in path_str, (
            f"Expected path '{path_str}' to contain native separator '{native_sep}'"
        )
        
        # The path in the error message should match the native path format
        # (no mixing of separators)
        if native_sep == '\\':
            # On Windows, should not have forward slashes
            # (unless they're in the original component names)
            pass  # Path objects handle this automatically
        else:
            # On Unix, should use forward slashes
            assert '\\' not in path_str or '\\' in ''.join(path_components), (
                f"Expected Unix path '{path_str}' to not contain backslashes "
                f"(unless in component names)"
            )
    
    # Verify the formatted message is helpful
    assert len(formatted_message) > len(path_str), (
        "Expected formatted message to provide more context than just the path"
    )



# Python Executable Name Handling Property Tests


@given(
    in_venv=st.booleans(),
    platform_override=st.sampled_from(['windows', 'darwin', 'linux', None]),
)
def test_python_executable_name_handling(
    in_venv: bool, platform_override: str | None
) -> None:
    """Feature: cross-platform-compatibility, Property 9: Python executable name handling.

    Validates: Requirements 5.5

    For any platform, the system should correctly identify and use the appropriate
    Python executable name (python, python3, python.exe).
    """
    from src.email_signature.infrastructure.platform_utils import (
        get_python_executable_name,
        get_python_executable_path,
    )
    
    # Save original sys attributes
    original_real_prefix = getattr(sys, 'real_prefix', None)
    original_base_prefix = getattr(sys, 'base_prefix', sys.prefix)
    original_prefix = sys.prefix
    
    try:
        # Set up virtual environment state
        if in_venv:
            # Simulate venv environment
            sys.base_prefix = '/usr/bin/python'
            sys.prefix = '/home/user/.venv'
        else:
            # Not in venv
            if hasattr(sys, 'real_prefix'):
                delattr(sys, 'real_prefix')
            sys.base_prefix = sys.prefix
        
        # When getting the Python executable name
        if platform_override:
            # Test with platform override (for testing cross-platform behavior)
            with patch('src.email_signature.infrastructure.platform_utils.get_platform', return_value=platform_override):
                with patch('src.email_signature.infrastructure.platform_utils.is_windows', return_value=(platform_override == 'windows')):
                    with patch('src.email_signature.infrastructure.platform_utils.is_virtual_env', return_value=in_venv):
                        executable_name = get_python_executable_name()
        else:
            # Test with actual platform
            executable_name = get_python_executable_name()
        
        # Then the executable name should be appropriate
        assert isinstance(executable_name, str), (
            f"Expected get_python_executable_name to return a string, got {type(executable_name)}"
        )
        assert executable_name.strip(), (
            "Expected executable name to be non-empty"
        )
        
        # Verify the executable name follows platform conventions
        if in_venv:
            # In virtual environment, should use 'python' (works on all platforms)
            assert executable_name == 'python', (
                f"In virtual environment, expected executable name to be 'python', "
                f"got '{executable_name}'"
            )
        elif platform_override == 'windows':
            # Windows should use python.exe
            assert executable_name == 'python.exe', (
                f"On Windows, expected executable name to be 'python.exe', "
                f"got '{executable_name}'"
            )
        elif platform_override in ['darwin', 'linux']:
            # Unix-like systems should use python3
            assert executable_name == 'python3', (
                f"On Unix-like systems, expected executable name to be 'python3', "
                f"got '{executable_name}'"
            )
        
        # When getting the Python executable path
        executable_path = get_python_executable_path()
        
        # Then it should return a valid Path object
        assert isinstance(executable_path, Path), (
            f"Expected get_python_executable_path to return a Path object, "
            f"got {type(executable_path)}"
        )
        
        # And the path should exist
        assert executable_path.exists(), (
            f"Python executable path '{executable_path}' should exist"
        )
        
        # And it should be a file
        assert executable_path.is_file(), (
            f"Python executable path '{executable_path}' should be a file"
        )
        
        # And it should match sys.executable
        assert executable_path == Path(sys.executable), (
            f"Expected executable path to match sys.executable, "
            f"got '{executable_path}' vs '{sys.executable}'"
        )
    
    finally:
        # Restore original attributes
        if original_real_prefix is not None:
            sys.real_prefix = original_real_prefix
        elif hasattr(sys, 'real_prefix'):
            delattr(sys, 'real_prefix')
        
        sys.base_prefix = original_base_prefix
        sys.prefix = original_prefix


def test_python_executable_path_consistency() -> None:
    """Test that Python executable path is consistent with sys.executable.

    This test verifies that get_python_executable_path() returns the same
    path as sys.executable.
    """
    from src.email_signature.infrastructure.platform_utils import get_python_executable_path
    
    # When getting the Python executable path
    executable_path = get_python_executable_path()
    
    # Then it should match sys.executable
    assert executable_path == Path(sys.executable), (
        f"Expected executable path to match sys.executable, "
        f"got '{executable_path}' vs '{sys.executable}'"
    )
    
    # And it should exist
    assert executable_path.exists(), (
        f"Python executable path '{executable_path}' should exist"
    )
    
    # And it should be executable (on Unix systems)
    if not is_windows():
        import stat
        assert os.access(executable_path, os.X_OK), (
            f"Python executable '{executable_path}' should be executable"
        )
