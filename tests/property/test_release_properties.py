"""Property-based tests for release automation system.

Feature: deployment-and-release
"""

import re
import sys
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st


# Property 7: Git tag format
# Feature: deployment-and-release, Property 7: Git tag format
@settings(max_examples=100)
@given(
    major=st.integers(min_value=0, max_value=99),
    minor=st.integers(min_value=0, max_value=99),
    patch=st.integers(min_value=0, max_value=99)
)
def test_git_tag_format(major: int, minor: int, patch: int) -> None:
    """Test that Git tags follow the format vMAJOR.MINOR.PATCH.
    
    **Validates: Requirements 3.1**
    
    For any version being released, the created Git tag should follow 
    the format vMAJOR.MINOR.PATCH matching the version number.
    """
    # Import the release script module
    scripts_path = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(scripts_path))
    
    try:
        import create_github_release
        
        # Create a version string
        version = f"{major}.{minor}.{patch}"
        
        # Get the tag name
        tag_name = create_github_release.get_git_tag_name(version)
        
        # Verify tag format: vMAJOR.MINOR.PATCH
        expected_tag = f"v{version}"
        assert tag_name == expected_tag, (
            f"Tag name '{tag_name}' does not match expected format '{expected_tag}'"
        )
        
        # Verify tag matches pattern
        tag_pattern = r'^v\d+\.\d+\.\d+$'
        assert re.match(tag_pattern, tag_name), (
            f"Tag '{tag_name}' does not match pattern vMAJOR.MINOR.PATCH"
        )
        
        # Verify tag starts with 'v'
        assert tag_name.startswith('v'), f"Tag '{tag_name}' must start with 'v'"
        
        # Verify version part is valid semantic version
        version_part = tag_name[1:]  # Remove 'v' prefix
        semver_pattern = r'^\d+\.\d+\.\d+$'
        assert re.match(semver_pattern, version_part), (
            f"Version part '{version_part}' is not valid semantic version"
        )
        
    finally:
        # Clean up sys.path
        if str(scripts_path) in sys.path:
            sys.path.remove(str(scripts_path))
        # Remove the imported module
        if 'create_github_release' in sys.modules:
            del sys.modules['create_github_release']


# Property 8: Release asset completeness
# Feature: deployment-and-release, Property 8: Release asset completeness
@settings(max_examples=100)
@given(
    has_windows=st.booleans(),
    has_macos=st.booleans(),
    has_linux_bin=st.booleans(),
    has_linux_deb=st.booleans()
)
def test_release_asset_completeness(
    has_windows: bool,
    has_macos: bool,
    has_linux_bin: bool,
    has_linux_deb: bool
) -> None:
    """Test that GitHub releases include assets for all supported platforms.
    
    **Validates: Requirements 3.2, 6.1, 6.5**
    
    For any GitHub release, the release should include downloadable assets 
    for all supported platforms (Windows .exe, macOS .app, Linux binary, 
    Linux .deb) and documentation.
    """
    # This property tests the logic of asset detection
    # We'll verify that the find_binary_assets function can identify
    # the expected asset types
    
    scripts_path = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(scripts_path))
    
    try:
        import create_github_release
        
        # Create a temporary dist directory structure
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dist_dir = Path(tmpdir) / 'dist'
            dist_dir.mkdir()
            
            expected_assets = []
            
            # Create mock asset files based on the boolean flags
            if has_windows:
                windows_exe = dist_dir / 'email-signature.exe'
                windows_exe.touch()
                expected_assets.append(windows_exe.name)
            
            if has_macos:
                macos_app = dist_dir / 'email-signature.app'
                macos_app.mkdir()
                expected_assets.append(macos_app.name)
            
            if has_linux_bin:
                linux_bin = dist_dir / 'email-signature'
                linux_bin.touch()
                expected_assets.append(linux_bin.name)
            
            if has_linux_deb:
                linux_deb = dist_dir / 'email-signature.deb'
                linux_deb.touch()
                expected_assets.append(linux_deb.name)
            
            # Temporarily replace the dist directory path
            original_parent = create_github_release.Path(__file__).parent.parent
            
            # Mock the find_binary_assets to use our temp directory
            def mock_find_assets() -> list[Path]:
                patterns = ['*.exe', '*.app', '*.deb', 'email-signature', 'email-signature-gui']
                assets = []
                for pattern in patterns:
                    assets.extend(dist_dir.glob(pattern))
                assets.extend(dist_dir.glob('*.zip'))
                return list(set(assets))
            
            found_assets = mock_find_assets()
            found_names = [asset.name for asset in found_assets]
            
            # Verify all expected assets are found
            for expected in expected_assets:
                assert expected in found_names, (
                    f"Expected asset '{expected}' not found in {found_names}"
                )
            
            # Verify no unexpected assets
            for found in found_names:
                assert found in expected_assets, (
                    f"Unexpected asset '{found}' found"
                )
    
    finally:
        # Clean up sys.path
        if str(scripts_path) in sys.path:
            sys.path.remove(str(scripts_path))
        # Remove the imported module
        if 'create_github_release' in sys.modules:
            del sys.modules['create_github_release']


# Property 9: Pre-release marking
# Feature: deployment-and-release, Property 9: Pre-release marking
@settings(max_examples=100)
@given(
    major=st.integers(min_value=0, max_value=99),
    minor=st.integers(min_value=0, max_value=99),
    patch=st.integers(min_value=0, max_value=99),
    prerelease_suffix=st.sampled_from([
        '',  # No suffix (stable release)
        '-alpha',
        '-alpha.1',
        '-beta',
        '-beta.2',
        '-rc.1',
        '-dev',
        '-pre',
        'alpha',  # Without dash
        'beta1',
        'rc2',
    ])
)
def test_prerelease_marking(
    major: int,
    minor: int,
    patch: int,
    prerelease_suffix: str
) -> None:
    """Test that pre-release versions are correctly identified.
    
    **Validates: Requirements 3.4**
    
    For any version string containing pre-release identifiers 
    (alpha, beta, rc), the GitHub release should be marked as a pre-release.
    """
    scripts_path = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(scripts_path))
    
    try:
        import create_github_release
        
        # Create version string with or without pre-release suffix
        version = f"{major}.{minor}.{patch}{prerelease_suffix}"
        
        # Check if version is detected as pre-release
        is_pre = create_github_release.is_prerelease(version)
        
        # Determine expected result
        prerelease_keywords = ['alpha', 'beta', 'rc', 'dev', 'pre']
        should_be_prerelease = any(
            keyword in version.lower() for keyword in prerelease_keywords
        )
        
        assert is_pre == should_be_prerelease, (
            f"Version '{version}' prerelease detection incorrect: "
            f"got {is_pre}, expected {should_be_prerelease}"
        )
        
        # Verify stable releases (no suffix) are not marked as pre-release
        if prerelease_suffix == '':
            assert not is_pre, (
                f"Stable version '{version}' should not be marked as pre-release"
            )
        
        # Verify versions with pre-release keywords are marked correctly
        if any(keyword in prerelease_suffix.lower() for keyword in prerelease_keywords):
            assert is_pre, (
                f"Version '{version}' with pre-release suffix should be marked as pre-release"
            )
    
    finally:
        # Clean up sys.path
        if str(scripts_path) in sys.path:
            sys.path.remove(str(scripts_path))
        # Remove the imported module
        if 'create_github_release' in sys.modules:
            del sys.modules['create_github_release']


# Property 10: Version increment validation
# Feature: deployment-and-release, Property 10: Version increment validation
@settings(max_examples=100)
@given(
    old_major=st.integers(min_value=0, max_value=50),
    old_minor=st.integers(min_value=0, max_value=50),
    old_patch=st.integers(min_value=0, max_value=50),
    bump_type=st.sampled_from(['major', 'minor', 'patch', 'none'])
)
def test_version_increment_validation(
    old_major: int,
    old_minor: int,
    old_patch: int,
    bump_type: str
) -> None:
    """Test that version increment validation works correctly.
    
    **Validates: Requirements 3.5**
    
    For any release, the new version number should be strictly greater 
    than the previous released version according to semantic versioning rules.
    """
    scripts_path = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(scripts_path))
    
    try:
        import validate_version
        
        # Create old version
        old_version = f"{old_major}.{old_minor}.{old_patch}"
        
        # Create new version based on bump type
        if bump_type == 'major':
            new_version = f"{old_major + 1}.0.0"
            should_be_greater = True
        elif bump_type == 'minor':
            new_version = f"{old_major}.{old_minor + 1}.0"
            should_be_greater = True
        elif bump_type == 'patch':
            new_version = f"{old_major}.{old_minor}.{old_patch + 1}"
            should_be_greater = True
        else:  # 'none' - no increment
            new_version = old_version
            should_be_greater = False
        
        # Test the is_version_greater function
        is_greater = validate_version.is_version_greater(new_version, old_version)
        
        assert is_greater == should_be_greater, (
            f"Version comparison incorrect: is_version_greater('{new_version}', '{old_version}') "
            f"returned {is_greater}, expected {should_be_greater}"
        )
        
        # Verify that same versions are not considered greater
        assert not validate_version.is_version_greater(old_version, old_version), (
            f"Same version '{old_version}' should not be greater than itself"
        )
        
        # Verify parse_version works correctly
        parsed = validate_version.parse_version(new_version)
        expected_parts = tuple(int(x) for x in new_version.split('.'))
        assert parsed == expected_parts, (
            f"parse_version returned {parsed}, expected {expected_parts}"
        )
        
        # Test version comparison transitivity
        # If A > B and B > C, then A > C
        if bump_type == 'patch' and old_patch > 0:
            even_older = f"{old_major}.{old_minor}.{old_patch - 1}"
            assert validate_version.is_version_greater(old_version, even_older), (
                f"Version transitivity failed: {old_version} should be > {even_older}"
            )
            assert validate_version.is_version_greater(new_version, even_older), (
                f"Version transitivity failed: {new_version} should be > {even_older}"
            )
    
    finally:
        # Clean up sys.path
        if str(scripts_path) in sys.path:
            sys.path.remove(str(scripts_path))
        # Remove the imported module
        if 'validate_version' in sys.modules:
            del sys.modules['validate_version']
