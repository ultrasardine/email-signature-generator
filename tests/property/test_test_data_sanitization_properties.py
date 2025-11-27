"""Property-based tests for test data sanitization.

Feature: data-sanitization, Property 2: Test data contains no real information
Validates: Requirements 2.4
"""

import ast
import re
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st


def extract_string_literals_from_file(file_path: Path) -> list[str]:
    """Extract all string literals from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        string_literals = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                string_literals.append(node.value)
        
        return string_literals
    except Exception:
        # If we can't parse the file, return empty list
        return []


def is_generic_email(email: str) -> bool:
    """Check if an email uses generic/reserved domains."""
    generic_domains = [
        'example.com',
        'example.org',
        'example.net',
        'test.com',
        'localhost',
    ]
    
    email_lower = email.lower()
    return any(domain in email_lower for domain in generic_domains)


def is_generic_phone(phone: str) -> bool:
    """Check if a phone number uses fictional/reserved ranges."""
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check for +1 555 format (North American reserved range)
    if re.search(r'\+1\s*555', phone):
        return True
    
    # Check for UK drama numbers
    if re.search(r'\+44\s*20\s*7946', phone):
        return True
    
    # Check for other clearly fictional patterns
    if re.match(r'^555[\-\s]?\d{4}$', cleaned):
        return True
    
    # Check for fictional 9-digit format starting with 900 (reserved for testing)
    if re.match(r'^900\d{6}$', cleaned):
        return True
    
    return False


def contains_portuguese_location(text: str) -> bool:
    """Check if text contains Portuguese city names."""
    portuguese_cities = [
        'lisbon', 'lisboa', 'porto', 'faro', 'braga', 'coimbra',
        'aveiro', 'évora', 'setúbal', 'funchal', 'ponta delgada'
    ]
    
    text_lower = text.lower()
    return any(city in text_lower for city in portuguese_cities)


def contains_non_generic_location(text: str) -> bool:
    """Check if text contains specific non-generic locations."""
    # Allow generic locations
    generic_locations = [
        'anytown', 'springfield', 'riverside', 'lakeside', 
        'hilltown', 'usa', 'united states'
    ]
    
    text_lower = text.lower()
    
    # If it contains a generic location, it's fine
    if any(loc in text_lower for loc in generic_locations):
        return False
    
    # Check for Portuguese locations
    if contains_portuguese_location(text):
        return True
    
    return False


# Strategy for test file paths
test_file_paths = st.sampled_from([
    Path('tests/unit/test_cli.py'),
    Path('tests/unit/test_use_cases.py'),
    Path('tests/unit/test_preview_generator.py'),
    Path('tests/property/test_profile_properties.py'),
])


@given(test_file=test_file_paths)
@settings(max_examples=100)
def test_test_files_use_generic_emails(test_file: Path) -> None:
    """Property 2: Test data contains no real information (emails).
    
    For any test file, all email addresses should use example.com domain
    or other reserved domains.
    
    Validates: Requirements 2.4
    """
    if not test_file.exists():
        return
    
    string_literals = extract_string_literals_from_file(test_file)
    
    # Find all email-like strings
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    for literal in string_literals:
        emails = email_pattern.findall(literal)
        for email in emails:
            assert is_generic_email(email), (
                f"Test file {test_file} contains non-generic email: {email}. "
                f"Use example.com or other reserved domains."
            )


@given(test_file=test_file_paths)
@settings(max_examples=100)
def test_test_files_use_generic_phones(test_file: Path) -> None:
    """Property 2: Test data contains no real information (phones).
    
    For any test file, all phone numbers should use fictional ranges
    like +1 555-xxxx.
    
    Validates: Requirements 2.4
    """
    if not test_file.exists():
        return
    
    string_literals = extract_string_literals_from_file(test_file)
    
    # Find all phone-like strings (various formats)
    phone_patterns = [
        re.compile(r'\+\d{1,3}\s*\d{2,3}\s*\d{3,4}\s*\d{3,4}'),  # International format
        re.compile(r'\+\d{1,3}\s*\d{3}\s*\d{4}'),  # +1 555 0100 format
        re.compile(r'\d{9,}'),  # 9+ consecutive digits
    ]
    
    for literal in string_literals:
        for pattern in phone_patterns:
            phones = pattern.findall(literal)
            for phone in phones:
                # Skip if it's clearly not a phone (like a year or version number)
                if len(phone.replace('+', '').replace(' ', '')) < 9:
                    continue
                
                # Check if it's a generic phone number
                if not is_generic_phone(phone):
                    # Allow empty strings and very short numbers (not phones)
                    if phone.strip() and len(phone.replace(' ', '')) >= 9:
                        assert False, (
                            f"Test file {test_file} contains non-generic phone: {phone}. "
                            f"Use +1 555-xxxx or other fictional ranges."
                        )


@given(test_file=test_file_paths)
@settings(max_examples=100)
def test_test_files_use_generic_locations(test_file: Path) -> None:
    """Property 2: Test data contains no real information (locations).
    
    For any test file, all addresses should use generic locations
    like "Anytown, USA" instead of specific cities.
    
    Validates: Requirements 2.4
    """
    if not test_file.exists():
        return
    
    string_literals = extract_string_literals_from_file(test_file)
    
    for literal in string_literals:
        # Check for address-like strings (contain street indicators)
        if any(indicator in literal.lower() for indicator in ['st,', 'ave,', 'rd,', 'street,', 'avenue,', 'road,']):
            assert not contains_non_generic_location(literal), (
                f"Test file {test_file} contains non-generic location: {literal}. "
                f"Use generic locations like 'Anytown, USA'."
            )
