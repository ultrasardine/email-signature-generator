#!/usr/bin/env python3
"""Script to create GitHub releases with binary assets."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


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


def get_git_tag_name(version: str) -> str:
    """Generate git tag name from version.
    
    Args:
        version: Version string (e.g., "1.2.3")
        
    Returns:
        Git tag name (e.g., "v1.2.3")
    """
    return f"v{version}"


def is_prerelease(version: str) -> bool:
    """Detect if version is a pre-release.
    
    Args:
        version: Version string
        
    Returns:
        True if version contains pre-release identifiers
    """
    prerelease_patterns = [
        r'alpha',
        r'beta',
        r'rc',
        r'dev',
        r'pre',
    ]
    
    version_lower = version.lower()
    return any(re.search(pattern, version_lower) for pattern in prerelease_patterns)


def create_git_tag(tag_name: str, message: str) -> None:
    """Create and push a git tag.
    
    Args:
        tag_name: Name of the tag (e.g., "v1.2.3")
        message: Tag message
        
    Raises:
        subprocess.CalledProcessError: If git commands fail
    """
    # Create annotated tag
    subprocess.run(
        ['git', 'tag', '-a', tag_name, '-m', message],
        check=True,
        capture_output=True,
        text=True
    )
    print(f"Created git tag: {tag_name}")
    
    # Push tag to origin
    subprocess.run(
        ['git', 'push', 'origin', tag_name],
        check=True,
        capture_output=True,
        text=True
    )
    print(f"Pushed tag to origin: {tag_name}")


def get_release_notes(version: str) -> str:
    """Extract release notes from CHANGELOG.md for the given version.
    
    Args:
        version: Version string
        
    Returns:
        Release notes text, or default message if CHANGELOG not found
    """
    changelog_path = Path(__file__).parent.parent / 'CHANGELOG.md'
    
    if not changelog_path.exists():
        return f"Release version {version}\n\nSee commit history for changes."
    
    content = changelog_path.read_text()
    
    # Try to extract section for this version
    # Look for patterns like "## [1.2.3]" or "## 1.2.3" or "# Version 1.2.3"
    version_patterns = [
        rf'##\s*\[?{re.escape(version)}\]?.*?\n(.*?)(?=\n##|\Z)',
        rf'#\s+Version\s+{re.escape(version)}.*?\n(.*?)(?=\n#|\Z)',
    ]
    
    for pattern in version_patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            notes = match.group(1).strip()
            if notes:
                return notes
    
    # If no specific section found, return default
    return f"Release version {version}\n\nSee CHANGELOG.md for details."


def find_binary_assets() -> list[Path]:
    """Find all binary assets to upload.
    
    Returns:
        List of paths to binary files
    """
    dist_dir = Path(__file__).parent.parent / 'dist'
    
    if not dist_dir.exists():
        return []
    
    # Look for common binary patterns
    patterns = [
        '*.exe',
        '*.app',
        '*.deb',
        'email-signature',
        'email-signature-gui',
    ]
    
    assets = []
    for pattern in patterns:
        assets.extend(dist_dir.glob(pattern))
    
    # Also check for zipped .app bundles
    assets.extend(dist_dir.glob('*.zip'))
    
    return list(set(assets))  # Remove duplicates


def create_github_release_api(
    tag_name: str,
    release_name: str,
    body: str,
    prerelease: bool,
    assets: list[Path]
) -> None:
    """Create GitHub release using GitHub CLI (gh).
    
    Args:
        tag_name: Git tag name
        release_name: Release title
        body: Release notes
        prerelease: Whether this is a pre-release
        assets: List of asset files to upload
        
    Raises:
        subprocess.CalledProcessError: If gh command fails
        RuntimeError: If GitHub CLI is not installed
    """
    # Check if gh is installed
    try:
        subprocess.run(
            ['gh', '--version'],
            check=True,
            capture_output=True,
            text=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError(
            "GitHub CLI (gh) is not installed. "
            "Install it from https://cli.github.com/ or use your package manager."
        )
    
    # Build gh release create command
    cmd = [
        'gh', 'release', 'create', tag_name,
        '--title', release_name,
        '--notes', body,
    ]
    
    if prerelease:
        cmd.append('--prerelease')
    
    # Add asset files
    for asset in assets:
        cmd.append(str(asset))
    
    # Create release
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    
    print(f"Created GitHub release: {release_name}")
    print(f"Release URL: {result.stdout.strip()}")


def main() -> None:
    """Main entry point for GitHub release creation."""
    try:
        # Get current version
        version = get_current_version()
        print(f"Creating release for version: {version}")
        
        # Generate tag name
        tag_name = get_git_tag_name(version)
        
        # Check if this is a pre-release
        prerelease = is_prerelease(version)
        if prerelease:
            print(f"Detected pre-release version")
        
        # Get release notes
        release_notes = get_release_notes(version)
        
        # Find binary assets
        assets = find_binary_assets()
        if assets:
            print(f"Found {len(assets)} binary asset(s):")
            for asset in assets:
                print(f"  - {asset.name}")
        else:
            print("Warning: No binary assets found in dist/ directory")
        
        # Create git tag
        tag_message = f"Release version {version}"
        try:
            create_git_tag(tag_name, tag_message)
        except subprocess.CalledProcessError as e:
            if 'already exists' in e.stderr:
                print(f"Tag {tag_name} already exists, skipping tag creation")
            else:
                raise
        
        # Create GitHub release
        release_name = f"v{version}"
        create_github_release_api(
            tag_name=tag_name,
            release_name=release_name,
            body=release_notes,
            prerelease=prerelease,
            assets=assets
        )
        
        print(f"\n✓ Release created successfully!")
        
    except ValueError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"✗ Git/GitHub error: {e}", file=sys.stderr)
        if e.stderr:
            print(f"  {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
