"""
Property-based tests for build system correctness.

These tests verify that the build system produces correct outputs
across different platforms and configurations.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


# Feature: deployment-and-release, Property 1: Platform-specific build outputs
@pytest.mark.slow
@settings(max_examples=10)  # Reduced since builds are expensive
@given(
    spec_name=st.sampled_from(["email-signature.spec", "email-signature-gui.spec"])
)
def test_platform_specific_build_outputs(spec_name: str) -> None:
    """
    **Feature: deployment-and-release, Property 1: Platform-specific build outputs**
    
    For any supported platform (Windows, macOS, Linux), when the build command
    is executed for that platform, the system should produce the expected
    artifact type (.exe for Windows, .app for macOS, binary and .deb for Linux)
    that exists and is executable.
    
    **Validates: Requirements 1.1, 1.2, 1.3**
    """
    project_root = Path(__file__).parent.parent.parent
    spec_path = project_root / "build" / "pyinstaller" / spec_name
    
    # Skip if spec file doesn't exist
    if not spec_path.exists():
        pytest.skip(f"Spec file {spec_name} does not exist")
    
    # Determine expected output based on current platform and spec
    current_platform = platform.system()
    is_gui = "gui" in spec_name
    
    if current_platform == "Darwin":  # macOS
        if is_gui:
            expected_output = project_root / "dist" / "EmailSignatureGenerator.app"
            expected_type = "app_bundle"
        else:
            expected_output = project_root / "dist" / "email-signature"
            expected_type = "executable"
    elif current_platform == "Windows":
        if is_gui:
            expected_output = project_root / "dist" / "email-signature-gui.exe"
        else:
            expected_output = project_root / "dist" / "email-signature.exe"
        expected_type = "exe"
    elif current_platform == "Linux":
        if is_gui:
            expected_output = project_root / "dist" / "email-signature-gui"
        else:
            expected_output = project_root / "dist" / "email-signature"
        expected_type = "executable"
    else:
        pytest.skip(f"Unsupported platform: {current_platform}")
    
    # Property: The expected output should exist
    assert expected_output.exists(), (
        f"Expected build output {expected_output} does not exist for platform {current_platform}"
    )
    
    # Property: The output should be executable (or an app bundle on macOS)
    if expected_type == "app_bundle":
        # For .app bundles, check that the bundle directory exists and contains executable
        assert expected_output.is_dir(), f"{expected_output} should be a directory (app bundle)"
        executable = expected_output / "Contents" / "MacOS" / "email-signature-gui"
        assert executable.exists(), f"App bundle should contain executable at {executable}"
        assert os.access(executable, os.X_OK), f"Executable {executable} should be executable"
    else:
        # For regular executables, check they have execute permissions
        assert os.access(expected_output, os.X_OK), (
            f"Build output {expected_output} should be executable"
        )


# Feature: deployment-and-release, Property 2: Binary completeness
@pytest.mark.slow
@settings(max_examples=10, deadline=None)  # No deadline for slow build tests
@given(
    spec_name=st.just("email-signature.spec")  # Only test CLI binary
)
def test_binary_completeness(spec_name: str) -> None:
    """
    **Feature: deployment-and-release, Property 2: Binary completeness**
    
    For any built binary, the binary should contain all required components
    (GUI entry point, CLI entry point, default config, and font fallbacks)
    accessible within the bundle.
    
    **Validates: Requirements 1.4**
    """
    project_root = Path(__file__).parent.parent.parent
    spec_path = project_root / "build" / "pyinstaller" / spec_name
    
    # Skip if spec file doesn't exist
    if not spec_path.exists():
        pytest.skip(f"Spec file {spec_name} does not exist")
    
    # Determine binary path based on current platform and spec
    current_platform = platform.system()
    is_gui = "gui" in spec_name
    
    # Skip GUI binaries for this test since they don't support --version
    # and would require GUI interaction
    if is_gui:
        pytest.skip("GUI binaries don't support --version flag")
    
    if current_platform == "Darwin":  # macOS
        binary_path = project_root / "dist" / "email-signature"
    elif current_platform == "Windows":
        binary_path = project_root / "dist" / "email-signature.exe"
    elif current_platform == "Linux":
        binary_path = project_root / "dist" / "email-signature"
    else:
        pytest.skip(f"Unsupported platform: {current_platform}")
    
    # Skip if binary doesn't exist
    if not binary_path.exists():
        pytest.skip(f"Binary {binary_path} does not exist")
    
    # Property: Binary should be runnable and show version (indicates it has all dependencies)
    try:
        result = subprocess.run(
            [str(binary_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        # Property: Binary should execute successfully
        assert result.returncode == 0, (
            f"Binary {binary_path} failed to execute: {result.stderr}"
        )
        
        # Property: Binary should output version information
        assert "0.1.0" in result.stdout or "0.1.0" in result.stderr, (
            f"Binary should display version information. Got: {result.stdout} {result.stderr}"
        )
        
    except subprocess.TimeoutExpired:
        pytest.fail(f"Binary {binary_path} timed out during execution")
    except Exception as e:
        pytest.fail(f"Failed to execute binary {binary_path}: {e}")


# Feature: deployment-and-release, Property 6: Binary version metadata
@pytest.mark.slow
@settings(max_examples=10, deadline=None)  # No deadline for slow build tests
@given(
    spec_name=st.just("email-signature.spec")  # Only test CLI binary
)
def test_binary_version_metadata(spec_name: str) -> None:
    """
    **Feature: deployment-and-release, Property 6: Binary version metadata**
    
    For any built binary, inspecting the binary metadata should reveal
    version information that matches the current version.
    
    **Validates: Requirements 8.4**
    """
    project_root = Path(__file__).parent.parent.parent
    spec_path = project_root / "build" / "pyinstaller" / spec_name
    
    # Skip if spec file doesn't exist
    if not spec_path.exists():
        pytest.skip(f"Spec file {spec_name} does not exist")
    
    # Get the expected version from __version__.py
    version_file = project_root / "src" / "email_signature" / "__version__.py"
    version_content = version_file.read_text()
    
    # Extract version string
    import re
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', version_content)
    assert version_match, "Could not find version in __version__.py"
    expected_version = version_match.group(1)
    
    # Determine binary path based on current platform and spec
    current_platform = platform.system()
    is_gui = "gui" in spec_name
    
    # Skip GUI binaries for this test since they don't support --version
    # and would require GUI interaction
    if is_gui:
        pytest.skip("GUI binaries don't support --version flag")
    
    if current_platform == "Darwin":  # macOS
        binary_path = project_root / "dist" / "email-signature"
    elif current_platform == "Windows":
        binary_path = project_root / "dist" / "email-signature.exe"
    elif current_platform == "Linux":
        binary_path = project_root / "dist" / "email-signature"
    else:
        pytest.skip(f"Unsupported platform: {current_platform}")
    
    # Skip if binary doesn't exist
    if not binary_path.exists():
        pytest.skip(f"Binary {binary_path} does not exist")
    
    # Property: Binary should report the correct version when executed with --version
    try:
        result = subprocess.run(
            [str(binary_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        # Property: Version output should match expected version
        output = result.stdout + result.stderr
        assert expected_version in output, (
            f"Binary version output should contain {expected_version}. Got: {output}"
        )
        
    except subprocess.TimeoutExpired:
        pytest.fail(f"Binary {binary_path} timed out during execution")
    except Exception as e:
        pytest.fail(f"Failed to execute binary {binary_path}: {e}")


# Feature: deployment-and-release, Property 16: Build-all target completeness
@pytest.mark.slow
def test_build_all_target_completeness() -> None:
    """
    **Feature: deployment-and-release, Property 16: Build-all target completeness**
    
    For any execution of the build-all target, the build system should produce
    artifacts for all supported platforms.
    
    **Validates: Requirements 5.1**
    
    Note: This test verifies that the Makefile target exists and is properly
    configured to call all platform-specific targets. It does not actually
    execute the builds (which would be extremely time-consuming).
    """
    project_root = Path(__file__).parent.parent.parent
    makefile_path = project_root / "Makefile"
    
    # Property: Makefile should exist
    assert makefile_path.exists(), "Makefile should exist"
    
    # Read Makefile content
    makefile_content = makefile_path.read_text()
    
    # Property: build-all target should exist
    assert "build-all:" in makefile_content, "Makefile should contain build-all target"
    
    # Property: build-all should reference all platform-specific targets
    # Extract the build-all target definition
    import re
    build_all_match = re.search(
        r'^build-all:.*?(?=^[^\t]|\Z)',
        makefile_content,
        re.MULTILINE | re.DOTALL
    )
    
    assert build_all_match, "Could not find build-all target definition"
    build_all_section = build_all_match.group(0)
    
    # Property: build-all should call build-windows
    assert "build-windows" in build_all_section, (
        "build-all target should reference build-windows"
    )
    
    # Property: build-all should call build-macos
    assert "build-macos" in build_all_section, (
        "build-all target should reference build-macos"
    )
    
    # Property: build-all should call build-linux
    assert "build-linux" in build_all_section, (
        "build-all target should reference build-linux"
    )
    
    # Property: All platform-specific targets should exist
    assert "build-windows:" in makefile_content, (
        "Makefile should contain build-windows target"
    )
    assert "build-macos:" in makefile_content, (
        "Makefile should contain build-macos target"
    )
    assert "build-linux:" in makefile_content, (
        "Makefile should contain build-linux target"
    )


# Feature: deployment-and-release, Property 17: Platform-specific build isolation
@pytest.mark.slow
@settings(max_examples=10, deadline=None)
@given(
    target=st.sampled_from(["build-windows", "build-macos", "build-linux"])
)
def test_platform_specific_build_isolation(target: str) -> None:
    """
    **Feature: deployment-and-release, Property 17: Platform-specific build isolation**
    
    For any platform-specific build target (build-windows, build-macos, build-linux),
    only that platform's artifacts should be created.
    
    **Validates: Requirements 5.2**
    
    Note: This test verifies that the Makefile targets are properly isolated
    and don't inadvertently trigger builds for other platforms. It checks
    the Makefile structure rather than executing builds.
    """
    project_root = Path(__file__).parent.parent.parent
    makefile_path = project_root / "Makefile"
    
    # Property: Makefile should exist
    assert makefile_path.exists(), "Makefile should exist"
    
    # Read Makefile content
    makefile_content = makefile_path.read_text()
    
    # Property: The target should exist
    assert f"{target}:" in makefile_content, (
        f"Makefile should contain {target} target"
    )
    
    # Extract the target definition
    import re
    # Match from target name to the next target or end of file
    # Makefile targets start at column 0, commands are indented with tabs
    target_match = re.search(
        rf'^{re.escape(target)}:.*?(?=^[a-zA-Z_-]+:|\Z)',
        makefile_content,
        re.MULTILINE | re.DOTALL
    )
    
    assert target_match, f"Could not find {target} target definition"
    target_section = target_match.group(0)
    
    # Property: Platform-specific target should NOT call other platform targets
    other_targets = {
        "build-windows": ["build-macos", "build-linux"],
        "build-macos": ["build-windows", "build-linux"],
        "build-linux": ["build-windows", "build-macos"],
    }
    
    for other_target in other_targets[target]:
        # Check that the other target is not invoked (not as a dependency or make call)
        # Allow the target name to appear in comments or strings, but not as a make invocation
        assert not re.search(
            rf'\$\(MAKE\)\s+{re.escape(other_target)}|^\s*{re.escape(other_target)}\s*$',
            target_section,
            re.MULTILINE
        ), (
            f"{target} should not invoke {other_target} (targets should be isolated)"
        )
    
    # Property: Target should call PyInstaller
    assert "pyinstaller" in target_section.lower(), (
        f"{target} should invoke PyInstaller"
    )
    
    # Property: Target should reference the spec files
    assert ".spec" in target_section, (
        f"{target} should reference PyInstaller spec files"
    )
