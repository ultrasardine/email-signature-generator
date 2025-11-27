"""Property-based tests for version management system.

Feature: deployment-and-release
"""

import re
import subprocess
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from src.email_signature.__version__ import __version__


# Property 3: Semantic version format
# Feature: deployment-and-release, Property 3: Semantic version format
@settings(max_examples=100)
@given(st.just(__version__))
def test_version_follows_semantic_versioning_format(version_str: str) -> None:
    """Test that version string follows semantic versioning format MAJOR.MINOR.PATCH.
    
    **Validates: Requirements 2.1**
    
    For any version string in the system, it should match the semantic versioning 
    format MAJOR.MINOR.PATCH where each component is a non-negative integer.
    """
    # Semantic version pattern: MAJOR.MINOR.PATCH where each is a non-negative integer
    semver_pattern = r'^\d+\.\d+\.\d+$'
    
    assert re.match(semver_pattern, version_str), (
        f"Version '{version_str}' does not follow semantic versioning format MAJOR.MINOR.PATCH"
    )
    
    # Additionally verify each component is a valid non-negative integer
    parts = version_str.split('.')
    assert len(parts) == 3, f"Version must have exactly 3 parts, got {len(parts)}"
    
    for i, part in enumerate(parts):
        component_name = ['MAJOR', 'MINOR', 'PATCH'][i]
        assert part.isdigit(), f"{component_name} component '{part}' is not a valid integer"
        assert int(part) >= 0, f"{component_name} component must be non-negative"



# Property 4: Version consistency (single source of truth)
# Feature: deployment-and-release, Property 4: Version consistency (single source of truth)
@settings(max_examples=100, deadline=None)
@given(st.just(__version__))
def test_version_consistency_across_all_sources(version_str: str) -> None:
    """Test that version is consistent across all methods of querying.
    
    **Validates: Requirements 2.5, 8.1, 8.5**
    
    For any method of querying the version (CLI --version, GUI display, module import, 
    pyproject.toml), all methods should return the same version string.
    """
    # Method 1: Direct import from __version__.py
    from src.email_signature.__version__ import __version__ as imported_version
    assert imported_version == version_str, (
        f"Imported version '{imported_version}' does not match expected '{version_str}'"
    )
    
    # Method 2: CLI --version flag
    result = subprocess.run(
        ['uv', 'run', 'python', 'main.py', '--version'],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )
    cli_output = result.stdout.strip()
    # CLI output format is "main.py X.Y.Z"
    assert version_str in cli_output, (
        f"CLI version output '{cli_output}' does not contain version '{version_str}'"
    )
    
    # Method 3: Check __version__.py file content directly
    version_file = Path(__file__).parent.parent.parent / 'src' / 'email_signature' / '__version__.py'
    version_file_content = version_file.read_text()
    assert f'__version__ = "{version_str}"' in version_file_content, (
        f"Version file does not contain __version__ = \"{version_str}\""
    )
    
    # Method 4: Verify __version_info__ matches
    from src.email_signature.__version__ import __version_info__
    expected_info = tuple(int(x) for x in version_str.split('.'))
    assert __version_info__ == expected_info, (
        f"__version_info__ {__version_info__} does not match expected {expected_info}"
    )



# Property 5: Version display in interfaces
# Feature: deployment-and-release, Property 5: Version display in interfaces
@settings(max_examples=100)
@given(st.just(__version__))
def test_version_display_in_interfaces(version_str: str) -> None:
    """Test that version is displayed in user interfaces.
    
    **Validates: Requirements 8.2, 8.3**
    
    For any user interface (CLI with --version flag, GUI window title), 
    the interface should display the current version number from the centralized version file.
    """
    # Test CLI --version flag
    result = subprocess.run(
        ['uv', 'run', 'python', 'main.py', '--version'],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )
    assert result.returncode == 0, f"CLI --version command failed with code {result.returncode}"
    cli_output = result.stdout.strip()
    assert version_str in cli_output, (
        f"CLI --version output '{cli_output}' does not display version '{version_str}'"
    )
    
    # Test GUI window title contains version
    # We'll check the code that sets the title rather than launching the GUI
    gui_main_window_file = Path(__file__).parent.parent.parent / 'src' / 'email_signature' / 'interface' / 'gui' / 'main_window.py'
    gui_content = gui_main_window_file.read_text()
    
    # Verify the GUI imports __version__
    assert 'from ...__version__ import __version__' in gui_content, (
        "GUI main_window.py does not import __version__"
    )
    
    # Verify the GUI uses version in title
    assert 'f"Email Signature Generator v{__version__}"' in gui_content, (
        "GUI main_window.py does not include version in window title"
    )



# Property 19: Version bump operations
# Feature: deployment-and-release, Property 19: Version bump operations
@settings(max_examples=100)
@given(
    major=st.integers(min_value=0, max_value=99),
    minor=st.integers(min_value=0, max_value=99),
    patch=st.integers(min_value=0, max_value=99),
    bump_type=st.sampled_from(['major', 'minor', 'patch'])
)
def test_version_bump_operations(major: int, minor: int, patch: int, bump_type: str) -> None:
    """Test that version bump operations follow semantic versioning rules.
    
    **Validates: Requirements 5.5**
    
    For any version bump operation (patch, minor, major), the version file should be 
    updated according to semantic versioning rules and the new version should be valid.
    """
    import sys
    import importlib
    
    # Import the bump_version module
    scripts_path = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(scripts_path))
    
    try:
        import bump_version
        
        # Create a test version string
        current_version = f"{major}.{minor}.{patch}"
        
        # Calculate expected new version based on bump type
        if bump_type == 'major':
            expected_version = f"{major + 1}.0.0"
        elif bump_type == 'minor':
            expected_version = f"{major}.{minor + 1}.0"
        else:  # patch
            expected_version = f"{major}.{minor}.{patch + 1}"
        
        # Test the bump_version function
        new_version = bump_version.bump_version(current_version, bump_type)
        
        # Verify the new version matches expected
        assert new_version == expected_version, (
            f"Bumping {current_version} with {bump_type} should produce {expected_version}, "
            f"but got {new_version}"
        )
        
        # Verify the new version is valid semantic version
        semver_pattern = r'^\d+\.\d+\.\d+$'
        assert re.match(semver_pattern, new_version), (
            f"Bumped version '{new_version}' is not a valid semantic version"
        )
        
        # Verify version components are non-negative integers
        new_parts = new_version.split('.')
        assert len(new_parts) == 3, f"Bumped version must have 3 parts"
        for part in new_parts:
            assert part.isdigit(), f"Version component '{part}' is not a valid integer"
            assert int(part) >= 0, f"Version component must be non-negative"
        
        # Verify parse_version works correctly
        parsed_major, parsed_minor, parsed_patch = bump_version.parse_version(new_version)
        expected_parts = [int(x) for x in new_version.split('.')]
        assert [parsed_major, parsed_minor, parsed_patch] == expected_parts, (
            f"parse_version returned incorrect values"
        )
        
    finally:
        # Clean up sys.path
        sys.path.remove(str(scripts_path))
        # Remove the imported module
        if 'bump_version' in sys.modules:
            del sys.modules['bump_version']
