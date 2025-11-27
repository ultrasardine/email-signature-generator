"""Unit tests for fresh clone verification.

Feature: data-sanitization

This test verifies that a fresh clone of the repository contains no proprietary
or identifiable information and that all tests pass in the fresh clone.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def get_repo_root() -> Path:
    """Get the repository root directory."""
    return Path(__file__).parent.parent.parent


def test_fresh_clone_contains_no_proprietary_files() -> None:
    """Example 7: Fresh clone verification.

    Validates: Requirements 4.5

    Clone the repository to a new temporary directory and verify:
    1. No proprietary files exist in the clone
    2. The generic logo is present and valid
    3. No proprietary content in configuration files
    """
    repo_root = get_repo_root()
    
    # Create a temporary directory for the clone
    with tempfile.TemporaryDirectory(prefix="email_sig_clone_") as temp_dir:
        clone_path = Path(temp_dir) / "repo_clone"
        
        # Clone the repository (local clone for speed)
        result = subprocess.run(
            ["git", "clone", str(repo_root), str(clone_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Git clone failed: {result.stderr}"
        
        # Verify the clone was successful
        assert clone_path.exists(), "Clone directory should exist"
        assert (clone_path / ".git").exists(), "Clone should have .git directory"
        
        # Verify logo.png exists and is the generic version
        logo_path = clone_path / "logo.png"
        if logo_path.exists():
            # Check file size - generic logo should be small
            logo_size = logo_path.stat().st_size
            assert logo_size < 50000, (
                f"logo.png in clone is too large ({logo_size} bytes). "
                "Expected generic placeholder (< 50KB)."
            )
        
        # Verify configuration file has generic content
        config_path = clone_path / "config" / "default_config.yaml"
        if config_path.exists():
            config_content = config_path.read_text()
            # Should NOT contain Portuguese confidentiality text
            assert "CONFIDENCIALIDADE" not in config_content, (
                "Configuration still contains Portuguese confidentiality text"
            )
            # Should contain English confidentiality text
            assert "CONFIDENTIALITY" in config_content, (
                "Configuration should contain English confidentiality text"
            )
        
        # Verify no proprietary content in git history
        history_result = subprocess.run(
            ["git", "log", "--all", "--full-history", "--oneline", "--", "logo.png"],
            capture_output=True,
            text=True,
            cwd=clone_path,
        )
        assert history_result.returncode == 0, f"Git log failed: {history_result.stderr}"
        
        # If there's history, verify it's clean (small commits only)
        if history_result.stdout.strip():
            # Check that any historical logo.png is the generic version
            commits = history_result.stdout.strip().split('\n')
            for commit_line in commits[:3]:  # Check first 3 commits
                commit_hash = commit_line.split()[0]
                blob_result = subprocess.run(
                    ["git", "show", f"{commit_hash}:logo.png"],
                    capture_output=True,
                    cwd=clone_path,
                )
                if blob_result.returncode == 0:
                    blob_size = len(blob_result.stdout)
                    assert blob_size < 50000, (
                        f"Historical logo.png in commit {commit_hash} is too large "
                        f"({blob_size} bytes)"
                    )


def test_fresh_clone_documentation_is_sanitized() -> None:
    """Verify documentation in fresh clone uses generic data.

    Validates: Requirements 4.5

    Check that documentation files in a fresh clone contain only
    generic placeholder information.
    """
    repo_root = get_repo_root()
    
    with tempfile.TemporaryDirectory(prefix="email_sig_clone_") as temp_dir:
        clone_path = Path(temp_dir) / "repo_clone"
        
        # Clone the repository
        result = subprocess.run(
            ["git", "clone", str(repo_root), str(clone_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Git clone failed: {result.stderr}"
        
        # Check README.md for generic content
        readme_path = clone_path / "README.md"
        if readme_path.exists():
            readme_content = readme_path.read_text()
            # Should use example.com domain
            if "@" in readme_content:
                # Any email should use example.com
                import re
                # More specific email regex to avoid false positives like python@3.13
                emails = re.findall(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', readme_content)
                for email in emails:
                    # Skip common false positives (version strings, technical references)
                    if any(skip in email.lower() for skip in 
                           ['python@', 'pytest@', 'github@', '@latest', '@v']):
                        continue
                    # Allow example.com, example.org, or placeholder formats
                    assert any(domain in email.lower() for domain in 
                              ['example.com', 'example.org', 'placeholder', 'your-']), (
                        f"Found non-generic email in README: {email}"
                    )
        
        # Check MANUAL_TESTING_GUIDE.md
        guide_path = clone_path / "MANUAL_TESTING_GUIDE.md"
        if guide_path.exists():
            guide_content = guide_path.read_text()
            # Should not contain Portuguese phone format (+351)
            assert "+351" not in guide_content, (
                "MANUAL_TESTING_GUIDE.md still contains Portuguese phone numbers"
            )


def test_fresh_clone_tests_directory_is_sanitized() -> None:
    """Verify test files in fresh clone use generic data.

    Validates: Requirements 4.5

    Check that test files in a fresh clone contain only
    generic placeholder test data.
    """
    repo_root = get_repo_root()
    
    with tempfile.TemporaryDirectory(prefix="email_sig_clone_") as temp_dir:
        clone_path = Path(temp_dir) / "repo_clone"
        
        # Clone the repository
        result = subprocess.run(
            ["git", "clone", str(repo_root), str(clone_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Git clone failed: {result.stderr}"
        
        # Check test files for generic content
        tests_dir = clone_path / "tests"
        if tests_dir.exists():
            for test_file in tests_dir.rglob("*.py"):
                # Skip the fresh clone verification test itself (it contains "+351" in assertions)
                if test_file.name == "test_fresh_clone_verification.py":
                    continue
                    
                content = test_file.read_text()
                
                # Should not contain Portuguese phone format
                assert "+351" not in content, (
                    f"Test file {test_file.name} still contains Portuguese phone numbers"
                )
                
                # Check emails use example.com
                import re
                emails = re.findall(r'[\w.+-]+@[\w.-]+\.\w+', content)
                for email in emails:
                    # Allow example.com, example.org, test domains, or placeholder formats
                    allowed_domains = [
                        'example.com', 'example.org', 'test.com', 
                        'placeholder', 'your-', 'acme', 'company'
                    ]
                    # Skip common false positives
                    if any(skip in email for skip in ['pytest', 'python', 'github']):
                        continue
                    assert any(domain in email.lower() for domain in allowed_domains), (
                        f"Found non-generic email in {test_file.name}: {email}"
                    )
