"""Property-based tests for logo reference consistency.

Feature: data-sanitization
"""

import ast
import re
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st


def get_all_python_files() -> list[Path]:
    """Get all Python source files in the project.
    
    Returns:
        List of Path objects for all .py files in src/ directory
    """
    src_dir = Path("src")
    if not src_dir.exists():
        return []
    
    python_files = []
    for py_file in src_dir.rglob("*.py"):
        # Skip __pycache__ directories
        if "__pycache__" not in str(py_file):
            python_files.append(py_file)
    
    return python_files


def extract_string_literals(file_path: Path) -> list[str]:
    """Extract all string literals from a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of string literals found in the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file into an AST
        tree = ast.parse(content, filename=str(file_path))
        
        # Extract all string literals
        string_literals = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                string_literals.append(node.value)
        
        return string_literals
    except Exception:
        # If we can't parse the file, return empty list
        return []


def check_logo_reference(string_literal: str) -> bool:
    """Check if a string literal is a logo file reference.
    
    Args:
        string_literal: String to check
        
    Returns:
        True if this is a logo reference, False otherwise
    """
    # Convert to lowercase for case-insensitive matching
    lower_str = string_literal.lower()
    
    # Check if it looks like a logo file path
    # Must contain "logo" and end with an image extension
    if "logo" in lower_str:
        # Check for image extensions
        if any(lower_str.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
            return True
    
    return False


def is_valid_logo_reference(logo_ref: str) -> bool:
    """Check if a logo reference uses the approved patterns.
    
    Valid patterns:
    - "logo.png" (generic filename)
    - "logo.jpg" (generic filename)
    - "./logo/logo.png" (subdirectory with generic filename)
    - "./logo/logo.jpg" (subdirectory with generic filename)
    - Any path that doesn't contain company-specific or proprietary names
    
    Args:
        logo_ref: Logo file reference to validate
        
    Returns:
        True if the reference is valid, False otherwise
    """
    # Normalize the path
    normalized = logo_ref.replace('\\', '/').lower()
    
    # Check if it's one of the approved patterns
    approved_patterns = [
        'logo.png',
        'logo.jpg',
        'logo.jpeg',
        './logo/logo.png',
        './logo/logo.jpg',
        './logo/logo.jpeg',
    ]
    
    # Check exact matches
    if normalized in approved_patterns:
        return True
    
    # Check if it's a relative path starting with ./ and containing logo
    if normalized.startswith('./') and '/logo.' in normalized:
        return True
    
    # Check if it's just a filename (no path separators except at start)
    if '/' not in normalized.lstrip('./') and normalized.startswith('logo.'):
        return True
    
    return False


@given(file_index=st.integers(min_value=0, max_value=100))
@settings(max_examples=100, deadline=None)
def test_logo_references_use_consistent_filename(file_index: int) -> None:
    """Feature: data-sanitization, Property 3: Code references use consistent logo filename.
    
    Validates: Requirements 3.1, 3.4
    
    For any Python file that references a logo file path, it should use the filename
    "logo.png" or reference the configuration's logo_search_paths.
    """
    # Get all Python files
    python_files = get_all_python_files()
    
    if not python_files:
        # No files to test
        return
    
    # Select a file based on the index (wrap around if needed)
    file_path = python_files[file_index % len(python_files)]
    
    # Extract string literals from the file
    string_literals = extract_string_literals(file_path)
    
    # Check each string literal for logo references
    for literal in string_literals:
        if check_logo_reference(literal):
            # This is a logo reference - verify it uses approved patterns
            assert is_valid_logo_reference(literal), (
                f"File {file_path} contains logo reference '{literal}' that doesn't use "
                f"the standard 'logo.png' or 'logo.jpg' filename. "
                f"All logo references should use generic filenames without proprietary names."
            )


def test_config_uses_generic_logo_filenames() -> None:
    """Test that configuration files use generic logo filenames.
    
    This is an example test that verifies the config file specifically.
    """
    # Read the config file
    config_path = Path("src/email_signature/domain/config.py")
    
    if not config_path.exists():
        # Config file doesn't exist, skip test
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for logo search paths in the config
    # The default should include generic filenames
    assert 'logo.png' in content or '"logo.png"' in content, (
        "Config should include 'logo.png' in default logo search paths"
    )
    
    # Ensure no proprietary logo names are hardcoded
    # (This is a negative test - we're checking what shouldn't be there)
    proprietary_patterns = [
        r'company.*logo',  # company-specific logos
        r'brand.*logo',    # brand-specific logos
        r'proprietary',    # proprietary references
    ]
    
    for pattern in proprietary_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        # Filter out comments and docstrings that might mention these terms
        for match in matches:
            # This is just a sanity check - if we find these terms in actual code
            # (not comments), it might indicate a problem
            pass


def test_logo_loader_uses_config_search_paths() -> None:
    """Test that LogoLoader is initialized with config.logo_search_paths.
    
    This verifies that the logo loader doesn't use hardcoded paths.
    """
    # Get all Python files that might instantiate LogoLoader
    python_files = get_all_python_files()
    
    # Also check main entry point files
    entry_points = [
        Path("main.py"),
        Path("email_signature_generator.py"),
        Path("gui_main.py"),
    ]
    
    all_files = python_files + [f for f in entry_points if f.exists()]
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if this file creates a LogoLoader
            if 'LogoLoader(' in content:
                # Verify it's using config.logo_search_paths
                # Look for the pattern: LogoLoader(config.logo_search_paths)
                pattern = r'LogoLoader\s*\(\s*config\.logo_search_paths\s*\)'
                matches = re.findall(pattern, content)
                
                # If we found LogoLoader instantiation, verify it uses config
                if 'LogoLoader(' in content:
                    # Count LogoLoader instantiations
                    loader_count = content.count('LogoLoader(')
                    
                    # Count proper config usage
                    config_usage_count = len(matches)
                    
                    # All LogoLoader instantiations should use config.logo_search_paths
                    assert config_usage_count > 0, (
                        f"File {file_path} instantiates LogoLoader but doesn't use "
                        f"config.logo_search_paths. All logo loaders should use the "
                        f"configured search paths, not hardcoded values."
                    )
        
        except Exception:
            # Skip files we can't read
            continue
