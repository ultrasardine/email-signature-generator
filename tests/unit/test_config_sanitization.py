"""
Unit tests for configuration sanitization.

**Feature: data-sanitization, Example 4: Confidentiality text is generic English**
**Validates: Requirements 2.2, 2.5**
"""

import yaml
from pathlib import Path


def test_confidentiality_text_is_generic_english():
    """
    Verify that config/default_config.yaml contains the English confidentiality text,
    not the Portuguese version.
    
    This ensures the configuration has been properly sanitized for open-source distribution.
    """
    config_path = Path("config/default_config.yaml")
    
    # Load the configuration file
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    
    # Extract the confidentiality text
    confidentiality_text = config_data.get("signature", {}).get("text", {}).get("confidentiality", "")
    
    # Expected generic English text
    expected_text = "CONFIDENTIALITY: This message is intended solely for the use of the addressee and may contain confidential information."
    
    # Verify it matches the expected generic English version
    assert confidentiality_text == expected_text, (
        f"Configuration should contain generic English confidentiality text.\n"
        f"Expected: {expected_text}\n"
        f"Got: {confidentiality_text}"
    )
    
    # Verify it does NOT contain Portuguese keywords
    portuguese_keywords = ["CONFIDENCIALIDADE", "mensagem", "ficheiro", "destinatário"]
    for keyword in portuguese_keywords:
        assert keyword not in confidentiality_text, (
            f"Configuration should not contain Portuguese text. Found keyword: {keyword}"
        )


def test_configuration_loads_correctly():
    """
    Verify that the configuration file can be loaded without errors.
    
    This ensures the sanitization didn't break the YAML structure.
    """
    config_path = Path("config/default_config.yaml")
    
    # Load the configuration file
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    
    # Verify basic structure exists
    assert "signature" in config_data, "Configuration should have 'signature' section"
    assert "text" in config_data["signature"], "Configuration should have 'text' section"
    assert "confidentiality" in config_data["signature"]["text"], "Configuration should have 'confidentiality' field"
    
    # Verify the text is a non-empty string
    confidentiality_text = config_data["signature"]["text"]["confidentiality"]
    assert isinstance(confidentiality_text, str), "Confidentiality text should be a string"
    assert len(confidentiality_text) > 0, "Confidentiality text should not be empty"
