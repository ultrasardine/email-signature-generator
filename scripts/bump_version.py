#!/usr/bin/env python3
"""Script to bump version numbers following semantic versioning."""

import argparse
import re
import sys
from pathlib import Path


def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse a semantic version string into components.
    
    Args:
        version_str: Version string in format MAJOR.MINOR.PATCH
        
    Returns:
        Tuple of (major, minor, patch) integers
        
    Raises:
        ValueError: If version string is not valid semantic version
    """
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
    if not match:
        raise ValueError(f"Invalid semantic version format: {version_str}")
    
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(version_str: str, bump_type: str) -> str:
    """Bump version according to semantic versioning rules.
    
    Args:
        version_str: Current version string
        bump_type: Type of bump ('major', 'minor', or 'patch')
        
    Returns:
        New version string
        
    Raises:
        ValueError: If bump_type is invalid or version format is invalid
    """
    major, minor, patch = parse_version(version_str)
    
    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}. Must be 'major', 'minor', or 'patch'")


def read_version_file(version_file_path: Path) -> str:
    """Read current version from __version__.py file.
    
    Args:
        version_file_path: Path to __version__.py file
        
    Returns:
        Current version string
        
    Raises:
        FileNotFoundError: If version file doesn't exist
        ValueError: If version file format is invalid
    """
    if not version_file_path.exists():
        raise FileNotFoundError(f"Version file not found: {version_file_path}")
    
    content = version_file_path.read_text()
    
    # Extract version from __version__ = "x.y.z"
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError(f"Could not find __version__ in {version_file_path}")
    
    return match.group(1)


def write_version_file(version_file_path: Path, new_version: str) -> None:
    """Write new version to __version__.py file.
    
    Args:
        version_file_path: Path to __version__.py file
        new_version: New version string to write
    """
    content = f'''"""Version information for email-signature-generator."""

__version__ = "{new_version}"
__version_info__ = tuple(int(x) for x in __version__.split("."))
'''
    version_file_path.write_text(content)


def main() -> None:
    """Main entry point for version bump script."""
    parser = argparse.ArgumentParser(
        description='Bump version number following semantic versioning'
    )
    parser.add_argument(
        'bump_type',
        choices=['major', 'minor', 'patch'],
        help='Type of version bump to perform'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    # Find version file
    version_file = Path(__file__).parent.parent / 'src' / 'email_signature' / '__version__.py'
    
    try:
        # Read current version
        current_version = read_version_file(version_file)
        print(f"Current version: {current_version}")
        
        # Calculate new version
        new_version = bump_version(current_version, args.bump_type)
        print(f"New version: {new_version}")
        
        # Write new version (unless dry run)
        if args.dry_run:
            print("\nDry run - no changes made")
        else:
            write_version_file(version_file, new_version)
            print(f"\nVersion bumped successfully: {current_version} -> {new_version}")
            print(f"Updated: {version_file}")
            
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
