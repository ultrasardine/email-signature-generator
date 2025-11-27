#!/usr/bin/env python3
"""Script to validate that version has been incremented for a release."""

import re
import subprocess
import sys
from pathlib import Path


def get_current_version() -> str:
    """Get the current version from __version__.py.
    
    Returns:
        Current version string
    """
    version_file = Path(__file__).parent.parent / 'src' / 'email_signature' / '__version__.py'
    content = version_file.read_text()
    
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError(f"Could not find __version__ in {version_file}")
    
    return match.group(1)


def get_latest_git_tag() -> str | None:
    """Get the latest git tag that matches version format.
    
    Returns:
        Latest version tag (without 'v' prefix) or None if no tags exist
    """
    try:
        result = subprocess.run(
            ['git', 'tag', '--list', 'v*', '--sort=-version:refname'],
            capture_output=True,
            text=True,
            check=True
        )
        
        tags = result.stdout.strip().split('\n')
        if not tags or tags[0] == '':
            return None
        
        # Return first tag without 'v' prefix
        latest_tag = tags[0]
        if latest_tag.startswith('v'):
            return latest_tag[1:]
        return latest_tag
        
    except subprocess.CalledProcessError:
        return None


def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse semantic version string.
    
    Args:
        version_str: Version string in format MAJOR.MINOR.PATCH
        
    Returns:
        Tuple of (major, minor, patch)
        
    Raises:
        ValueError: If version format is invalid
    """
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
    if not match:
        raise ValueError(f"Invalid semantic version format: {version_str}")
    
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def is_version_greater(new_version: str, old_version: str) -> bool:
    """Check if new version is greater than old version.
    
    Args:
        new_version: New version string
        old_version: Old version string
        
    Returns:
        True if new_version > old_version
    """
    new_major, new_minor, new_patch = parse_version(new_version)
    old_major, old_minor, old_patch = parse_version(old_version)
    
    if new_major > old_major:
        return True
    elif new_major < old_major:
        return False
    
    if new_minor > old_minor:
        return True
    elif new_minor < old_minor:
        return False
    
    return new_patch > old_patch


def main() -> None:
    """Main entry point for version validation."""
    try:
        current_version = get_current_version()
        print(f"Current version: {current_version}")
        
        # Validate current version format
        parse_version(current_version)
        
        # Get latest git tag
        latest_tag = get_latest_git_tag()
        
        if latest_tag is None:
            print("No previous version tags found - this appears to be the first release")
            print("✓ Version validation passed")
            return
        
        print(f"Latest git tag: v{latest_tag}")
        
        # Check if version has been incremented
        if current_version == latest_tag:
            print(f"\n✗ Error: Version has not been incremented!", file=sys.stderr)
            print(f"  Current version ({current_version}) is the same as latest tag ({latest_tag})", file=sys.stderr)
            print(f"  Please bump the version using: make version-bump-patch|minor|major", file=sys.stderr)
            sys.exit(1)
        
        if not is_version_greater(current_version, latest_tag):
            print(f"\n✗ Error: Version has not been properly incremented!", file=sys.stderr)
            print(f"  Current version ({current_version}) is not greater than latest tag ({latest_tag})", file=sys.stderr)
            print(f"  Please ensure version follows semantic versioning rules", file=sys.stderr)
            sys.exit(1)
        
        print(f"✓ Version validation passed: {latest_tag} -> {current_version}")
        
    except ValueError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
