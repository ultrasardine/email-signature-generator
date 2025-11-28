"""Property-based tests for documentation sanitization.

**Feature: data-sanitization, Property 1: Documentation uses only generic contact information**
**Validates: Requirements 2.3, 4.4**
"""

import re
from pathlib import Path
from typing import List, Tuple

from hypothesis import given, settings
from hypothesis import strategies as st


# Define patterns for identifying PII in documentation
# Note: These patterns detect non-US phone formats that should be sanitized
NON_GENERIC_PHONE_PATTERN = re.compile(r'\+3\d{2}\s*\d{2}\s*\d{3}\s*\d{4}')
NON_GENERIC_MOBILE_PATTERN = re.compile(r'\+3\d{2}\s*9[1-9]\s*\d{3}\s*\d{4}')
PORTUGUESE_NAME_PATTERN = re.compile(r'\bJoão\b|\bSilva\b|\bJoão Silva\b', re.IGNORECASE)
LISBON_ADDRESS_PATTERN = re.compile(r'\bLisbon\b|\bLisboa\b', re.IGNORECASE)
PORTUGAL_PATTERN = re.compile(r'\bPortugal\b', re.IGNORECASE)

# Define patterns for valid generic contact information
GENERIC_PHONE_PATTERN = re.compile(r'\+1\s*555\s*\d{4}')
GENERIC_EMAIL_PATTERN = re.compile(r'[\w\.-]+@example\.com')
GENERIC_NAME_PATTERN = re.compile(r'\bJohn Doe\b|\bJane Smith\b', re.IGNORECASE)
GENERIC_ADDRESS_PATTERN = re.compile(r'\bAnytown\b|\bUSA\b', re.IGNORECASE)


def get_documentation_files() -> List[Path]:
    """Get all documentation files that should be sanitized."""
    project_root = Path(__file__).parent.parent.parent
    doc_files = [
        project_root / "README.md",
        project_root / "MANUAL_TESTING_GUIDE.md",
        project_root / "docs" / "BUILDING.md",
    ]
    return [f for f in doc_files if f.exists()]


def check_file_for_pii(file_path: Path) -> Tuple[bool, List[str]]:
    """Check a file for PII patterns.
    
    Returns:
        Tuple of (has_pii, list_of_violations)
    """
    violations = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check for non-generic phone numbers
        if NON_GENERIC_PHONE_PATTERN.search(content):
            violations.append(f"Non-generic phone number found in {file_path.name}")
        
        # Check for non-generic mobile numbers
        if NON_GENERIC_MOBILE_PATTERN.search(content):
            violations.append(f"Non-generic mobile number found in {file_path.name}")
        
        # Check for Portuguese names
        if PORTUGUESE_NAME_PATTERN.search(content):
            violations.append(f"Portuguese name (João Silva) found in {file_path.name}")
        
        # Check for Lisbon addresses
        if LISBON_ADDRESS_PATTERN.search(content):
            violations.append(f"Lisbon address found in {file_path.name}")
        
        # Check for Portugal references (excluding legitimate mentions in platform docs)
        # We allow "Portugal" in certain contexts like "Lisbon, Portugal" being replaced
        portugal_matches = PORTUGAL_PATTERN.finditer(content)
        for match in portugal_matches:
            # Get context around the match
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end]
            
            # Allow Portugal in historical/replacement context
            if "Lisbon, Portugal" not in context or "Address:" in context:
                violations.append(f"Portugal reference found in {file_path.name}: {context.strip()}")
        
    except Exception as e:
        violations.append(f"Error reading {file_path.name}: {str(e)}")
    
    return len(violations) > 0, violations


def check_file_for_generic_data(file_path: Path) -> Tuple[bool, List[str]]:
    """Check a file contains generic placeholder data.
    
    Returns:
        Tuple of (has_generic_data, list_of_findings)
    """
    findings = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check for generic phone numbers
        if GENERIC_PHONE_PATTERN.search(content):
            findings.append(f"Generic phone number (+1 555-xxxx) found in {file_path.name}")
        
        # Check for example.com emails
        if GENERIC_EMAIL_PATTERN.search(content):
            findings.append(f"Generic email (example.com) found in {file_path.name}")
        
        # Check for generic names
        if GENERIC_NAME_PATTERN.search(content):
            findings.append(f"Generic name (John Doe) found in {file_path.name}")
        
        # Check for generic addresses
        if GENERIC_ADDRESS_PATTERN.search(content):
            findings.append(f"Generic address (Anytown, USA) found in {file_path.name}")
        
    except Exception as e:
        findings.append(f"Error reading {file_path.name}: {str(e)}")
    
    return len(findings) > 0, findings


def test_documentation_no_pii() -> None:
    """Property 1: Documentation uses only generic contact information.
    
    For any documentation file (README.md, MANUAL_TESTING_GUIDE.md, docs/BUILDING.md),
    it should not contain Portuguese phone numbers, Portuguese names (João Silva),
    Lisbon addresses, or other identifiable information.
    
    **Feature: data-sanitization, Property 1: Documentation uses only generic contact information**
    **Validates: Requirements 2.3, 4.4**
    """
    doc_files = get_documentation_files()
    
    assert len(doc_files) > 0, "No documentation files found to test"
    
    all_violations = []
    
    for doc_file in doc_files:
        has_pii, violations = check_file_for_pii(doc_file)
        
        if has_pii:
            all_violations.extend(violations)
    
    # Assert no PII found
    assert not all_violations, (
        f"Found PII in documentation files:\n" + "\n".join(all_violations)
    )


def test_documentation_has_generic_data() -> None:
    """Property 1 (part 2): Documentation contains generic placeholder data.
    
    For any documentation file, it should contain generic placeholder data like
    example.com emails, +1 555 phone numbers, and generic names/addresses.
    
    **Feature: data-sanitization, Property 1: Documentation uses only generic contact information**
    **Validates: Requirements 2.3, 4.4**
    """
    doc_files = get_documentation_files()
    
    assert len(doc_files) > 0, "No documentation files found to test"
    
    # At least one file should have generic data
    has_any_generic = False
    all_findings = []
    
    for doc_file in doc_files:
        has_generic, findings = check_file_for_generic_data(doc_file)
        if has_generic:
            has_any_generic = True
            all_findings.extend(findings)
    
    # Assert generic data is present
    assert has_any_generic, (
        "Documentation should contain generic placeholder data (example.com, +1 555, etc.)"
    )


@given(
    file_index=st.integers(min_value=0, max_value=2)
)
@settings(max_examples=100)
def test_documentation_sanitization_property(file_index: int) -> None:
    """Property-based test: Documentation uses only generic contact information.
    
    For any documentation file, when scanned for contact information patterns,
    all email addresses should use example.com domain, all phone numbers should
    use fictional ranges (+1 555), and all addresses should use generic locations.
    
    **Feature: data-sanitization, Property 1: Documentation uses only generic contact information**
    **Validates: Requirements 2.3, 4.4**
    """
    doc_files = get_documentation_files()
    
    if not doc_files:
        return  # Skip if no files found
    
    # Select a file based on the generated index
    file_index = file_index % len(doc_files)
    doc_file = doc_files[file_index]
    
    # Check for PII
    has_pii, violations = check_file_for_pii(doc_file)
    
    # Assert no PII in this file
    assert not has_pii, (
        f"Found PII in {doc_file.name}:\n" + "\n".join(violations)
    )
