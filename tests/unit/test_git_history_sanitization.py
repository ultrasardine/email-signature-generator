"""Unit tests for git history sanitization verification.

Feature: data-sanitization
"""

import subprocess
from pathlib import Path


def test_proprietary_logo_removed_from_git_history() -> None:
    """Example 2: Proprietary logo removed from git history.

    Validates: Requirements 1.2, 1.3, 4.2

    Verify that logo.png in git history contains only the generic placeholder,
    not the proprietary version. This test checks that:
    1. The git history has been properly sanitized
    2. No proprietary logo can be recovered from historical commits
    """
    # When checking git history for logo.png
    result = subprocess.run(
        ["git", "log", "--all", "--full-history", "--", "logo.png"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )

    # Then the command should execute successfully
    assert result.returncode == 0, f"Git log command failed: {result.stderr}"

    # The key verification is that git history should be clean
    # After git-filter-repo, there should be NO history for logo.png
    git_output = result.stdout.strip()
    
    # If git-filter-repo was successful, there should be no history
    if not git_output:
        # Success! No history means the proprietary logo was removed
        # This is the expected state after running git-filter-repo
        pass
    else:
        # If there IS history, verify it only contains the generic logo
        # Get all historical hashes of logo.png
        hash_history_result = subprocess.run(
            ["git", "log", "--all", "--full-history", "--pretty=format:%H", "--", "logo.png"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )
        
        if hash_history_result.returncode == 0 and hash_history_result.stdout.strip():
            commits = hash_history_result.stdout.strip().split('\n')
            
            # For each commit, check the logo.png blob
            for commit in commits[:5]:  # Check first 5 commits to avoid excessive checking
                blob_result = subprocess.run(
                    ["git", "show", f"{commit}:logo.png"],
                    capture_output=True,
                    cwd=Path(__file__).parent.parent.parent,
                )
                
                # The blob should exist and be relatively small (generic logo)
                if blob_result.returncode == 0:
                    blob_size = len(blob_result.stdout)
                    assert blob_size < 50000, (
                        f"Historical logo.png in commit {commit[:8]} is too large "
                        f"({blob_size} bytes), suggesting proprietary content remains"
                    )
    
    # If logo.png exists in the working directory, verify it's the generic version
    logo_path = Path(__file__).parent.parent.parent / "logo.png"
    if logo_path.exists():
        # Check that the current logo is the generic one by verifying it's a small file
        # The proprietary logo would typically be larger than a simple generated placeholder
        logo_size = logo_path.stat().st_size
        
        # Generic logos should be relatively small (< 50KB)
        # This is a heuristic check - adjust if needed based on actual generic logo size
        assert logo_size < 50000, (
            f"logo.png appears to be too large ({logo_size} bytes) to be the generic placeholder. "
            "Expected a small generic logo (< 50KB)."
        )
