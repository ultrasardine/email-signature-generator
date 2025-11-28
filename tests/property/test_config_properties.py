"""Property-based tests for configuration loading."""

import tempfile
from pathlib import Path

import yaml
from hypothesis import given
from hypothesis import strategies as st

from src.email_signature.domain.config import ConfigLoader, SignatureConfig


@given(
    logo_height=st.integers(min_value=10, max_value=200),
    margin=st.integers(min_value=5, max_value=50),
    logo_margin_right=st.integers(min_value=5, max_value=50),
    line_height=st.integers(min_value=10, max_value=50),
)
def test_configuration_loading(
    logo_height: int, margin: int, logo_margin_right: int, line_height: int
) -> None:
    """Feature: email-signature-refactor, Property 11: Configuration loading.

    Validates: Requirements 11.1, 11.2, 11.3, 11.4

    For any valid configuration file containing font paths, colors, dimensions,
    or logo search paths, the ConfigLoader should successfully parse and apply
    all specified settings.
    """
    # Create a valid configuration dictionary
    # Note: Font paths that don't exist will be filtered out and defaults will be used
    # This is correct behavior per the cross-platform compatibility design
    config_data = {
        "signature": {
            "dimensions": {
                "logo_height": logo_height,
                "margin": margin,
                "logo_margin_right": logo_margin_right,
                "line_height": line_height,
            },
            "outline": {
                "name_width": 2,
                "text_width": 1,
            },
            "colors": {
                "outline": [255, 255, 255],
                "name": [51, 51, 51],
            },
            "logo": {
                "search_paths": ["logo.png", "test/logo.jpg"],
            },
            "text": {
                "confidentiality": "Test confidentiality text",
            },
        }
    }

    # Write config to temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name

    try:
        # When loading configuration from file
        config = ConfigLoader.load(temp_path)

        # Then all settings should be loaded correctly
        assert config.logo_height == logo_height
        assert config.margin == margin
        assert config.logo_margin_right == logo_margin_right
        assert config.line_height == line_height
        assert config.outline_width_name == 2
        assert config.outline_width_text == 1
        assert config.colors["outline"] == (255, 255, 255)
        assert config.colors["name"] == (51, 51, 51)
        # Font paths: since we didn't provide valid font paths, defaults should be used
        assert len(config.font_paths["linux"]) > 0
        assert len(config.font_paths["windows"]) > 0
        assert "logo.png" in config.logo_search_paths
        assert "test/logo.jpg" in config.logo_search_paths
        assert config.confidentiality_text == "Test confidentiality text"

    finally:
        # Clean up temporary file
        Path(temp_path).unlink(missing_ok=True)


@given(
    config_scenario=st.sampled_from(
        [
            "no_file",
            "empty_file",
            "invalid_yaml",
            "missing_signature_section",
            "invalid_types",
        ]
    )
)
def test_configuration_defaults_fallback(config_scenario: str) -> None:
    """Feature: email-signature-refactor, Property 12: Configuration defaults fallback.

    Validates: Requirements 11.5

    For any missing or invalid configuration value, the application should use
    a sensible default value and continue execution without errors.
    """
    temp_path = None

    try:
        if config_scenario == "no_file":
            # Test with non-existent file path
            config = ConfigLoader.load("/nonexistent/path/config.yaml")
        elif config_scenario == "empty_file":
            # Test with empty file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                f.write("")
                temp_path = f.name
            config = ConfigLoader.load(temp_path)
        elif config_scenario == "invalid_yaml":
            # Test with invalid YAML
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                f.write("invalid: yaml: content: [[[")
                temp_path = f.name
            config = ConfigLoader.load(temp_path)
        elif config_scenario == "missing_signature_section":
            # Test with valid YAML but missing signature section
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump({"other_section": {"key": "value"}}, f)
                temp_path = f.name
            config = ConfigLoader.load(temp_path)
        else:  # invalid_types
            # Test with invalid data types
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump(
                    {
                        "signature": {
                            "dimensions": "not a dict",
                            "colors": ["not", "a", "dict"],
                        }
                    },
                    f,
                )
                temp_path = f.name
            config = ConfigLoader.load(temp_path)

        # Then default configuration should be returned
        assert isinstance(config, SignatureConfig)

        # Verify sensible defaults are present
        assert config.logo_height > 0
        assert config.margin > 0
        assert config.line_height > 0
        assert len(config.colors) > 0
        assert len(config.font_paths) > 0
        assert len(config.logo_search_paths) > 0
        assert config.confidentiality_text

    finally:
        # Clean up temporary file if created
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


@given(
    logo_height=st.integers(min_value=10, max_value=200),
    margin=st.integers(min_value=5, max_value=50),
    logo_margin_right=st.integers(min_value=5, max_value=50),
    line_height=st.integers(min_value=10, max_value=50),
    outline_width_name=st.integers(min_value=1, max_value=5),
    outline_width_text=st.integers(min_value=1, max_value=5),
)
def test_configuration_round_trip_with_format_preservation(
    logo_height: int,
    margin: int,
    logo_margin_right: int,
    line_height: int,
    outline_width_name: int,
    outline_width_text: int,
) -> None:
    """Feature: gui-interface, Property 6: Configuration round-trip with format preservation.

    Validates: Requirements 2.5, 8.4

    For any configuration changes made through the GUI, saving then loading the
    configuration should preserve both the values and the YAML file format.
    """
    temp_path = None

    try:
        # Create initial config file with comments and specific format
        initial_config = f"""# Test configuration for Email Signature Generator
signature:
  dimensions:
    logo_height: {logo_height}
    margin: {margin}
    logo_margin_right: {logo_margin_right}
    line_height: {line_height}
  
  outline:
    name_width: {outline_width_name}
    text_width: {outline_width_text}
  
  colors:
    outline: [255, 255, 255]
    name: [51, 51, 51]
    details: [100, 100, 100]
    separator: [200, 0, 40, 200]
    confidentiality: [150, 150, 150]
  
  fonts:
    linux:
      - "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
      - "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    windows:
      - "C:\\\\Windows\\\\Fonts\\\\arialbd.ttf"
      - "C:\\\\Windows\\\\Fonts\\\\arial.ttf"
    macos:
      - "/System/Library/Fonts/Helvetica.ttc"
      - "/System/Library/Fonts/HelveticaNeue.ttc"
  
  logo:
    search_paths:
      - "logo.png"
      - "logo.jpg"
  
  text:
    confidentiality: "Test confidentiality text"
"""

        # Write initial config to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(initial_config)
            temp_path = f.name

        # Load the configuration
        config_before = ConfigLoader.load(temp_path)

        # Verify initial values were loaded correctly
        assert config_before.logo_height == logo_height
        assert config_before.margin == margin
        assert config_before.logo_margin_right == logo_margin_right
        assert config_before.line_height == line_height
        assert config_before.outline_width_name == outline_width_name
        assert config_before.outline_width_text == outline_width_text

        # Simulate GUI save operation by modifying and re-saving
        # Read existing config
        with open(temp_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # Modify some values (simulating GUI changes)
        new_logo_height = logo_height + 10
        new_margin = margin + 5
        config_data["signature"]["dimensions"]["logo_height"] = new_logo_height
        config_data["signature"]["dimensions"]["margin"] = new_margin

        # Write back to file
        with open(temp_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

        # Load again to verify round-trip
        config_after = ConfigLoader.load(temp_path)

        # Verify modified values were saved and loaded correctly
        assert config_after.logo_height == new_logo_height
        assert config_after.margin == new_margin

        # Verify unchanged values were preserved
        assert config_after.logo_margin_right == logo_margin_right
        assert config_after.line_height == line_height
        assert config_after.outline_width_name == outline_width_name
        assert config_after.outline_width_text == outline_width_text

        # Verify the file still contains the signature section structure
        with open(temp_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
            # Check that key sections are present
            assert "signature:" in saved_content
            assert "dimensions:" in saved_content
            assert "colors:" in saved_content
            assert "fonts:" in saved_content

    finally:
        # Clean up temporary file
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


@given(
    line_ending=st.sampled_from(['\n', '\r\n', '\r']),
    logo_height=st.integers(min_value=10, max_value=200),
    margin=st.integers(min_value=5, max_value=50),
)
def test_yaml_parsing_consistency_across_line_endings(
    line_ending: str,
    logo_height: int,
    margin: int,
) -> None:
    """Feature: cross-platform-compatibility, Property 12: YAML parsing consistency.

    Validates: Requirements 8.1

    For any valid YAML configuration file, the system should parse it correctly
    regardless of platform or line ending style.
    """
    temp_path = None

    try:
        # Create config content with Unix-style line endings
        # Use only dimensions and colors to avoid font path validation issues
        config_content = f"""signature:
  dimensions:
    logo_height: {logo_height}
    margin: {margin}
    line_height: 22
  colors:
    outline: [255, 255, 255]
    name: [51, 51, 51]
    details: [100, 100, 100]
  logo:
    search_paths:
      - "logo.png"
      - "test/logo.jpg"
"""

        # Convert to the specified line ending style
        config_with_line_ending = config_content.replace('\n', line_ending)

        # Write config to temporary file with binary mode to preserve exact line endings
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".yaml", delete=False) as f:
            f.write(config_with_line_ending.encode('utf-8'))
            temp_path = f.name

        # When loading configuration from file with any line ending style
        config = ConfigLoader.load(temp_path)

        # Then the configuration should be parsed correctly regardless of line endings
        assert config.logo_height == logo_height
        assert config.margin == margin
        assert config.line_height == 22
        assert config.colors["outline"] == (255, 255, 255)
        assert config.colors["name"] == (51, 51, 51)
        assert config.colors["details"] == (100, 100, 100)
        assert "logo.png" in config.logo_search_paths
        assert "test/logo.jpg" in config.logo_search_paths

    finally:
        # Clean up temporary file
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)



@given(
    use_forward_slash=st.booleans(),
    use_backslash=st.booleans(),
)
def test_configuration_path_interpretation(
    use_forward_slash: bool,
    use_backslash: bool,
) -> None:
    """Feature: cross-platform-compatibility, Property 13: Configuration path interpretation.

    Validates: Requirements 8.2

    For any file path specified in configuration, the system should interpret it
    correctly for the current platform.
    """
    temp_path = None

    try:
        # Create paths with different separator styles
        # We'll use a mix of forward and backward slashes
        if use_forward_slash and not use_backslash:
            logo_path = "assets/images/logo.png"
            font_path_linux = "/usr/share/fonts/test.ttf"
            font_path_windows = "C:/Windows/Fonts/test.ttf"
        elif use_backslash and not use_forward_slash:
            logo_path = "assets\\images\\logo.png"
            font_path_linux = "/usr/share/fonts/test.ttf"
            font_path_windows = "C:\\Windows\\Fonts\\test.ttf"
        else:
            # Mix of both or neither - use platform default
            logo_path = "assets/images/logo.png"
            font_path_linux = "/usr/share/fonts/test.ttf"
            font_path_windows = "C:\\Windows\\Fonts\\test.ttf"

        config_data = {
            "signature": {
                "dimensions": {
                    "logo_height": 70,
                    "margin": 15,
                },
                "fonts": {
                    "linux": [font_path_linux],
                    "windows": [font_path_windows],
                },
                "logo": {
                    "search_paths": [logo_path],
                },
            }
        }

        # Write config to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        # When loading configuration with various path formats
        config = ConfigLoader.load(temp_path)

        # Then paths should be interpreted correctly
        # The paths should be stored as-is in the config
        assert len(config.logo_search_paths) > 0
        assert len(config.font_paths["linux"]) > 0
        assert len(config.font_paths["windows"]) > 0

        # The PathManager should be able to normalize these paths
        from src.email_signature.infrastructure.platform_utils import PathManager

        for logo_search_path in config.logo_search_paths:
            normalized = PathManager.normalize(logo_search_path)
            assert isinstance(normalized, Path)

        for font_path in config.font_paths.get("linux", []):
            normalized = PathManager.normalize(font_path)
            assert isinstance(normalized, Path)

        for font_path in config.font_paths.get("windows", []):
            normalized = PathManager.normalize(font_path)
            assert isinstance(normalized, Path)

    finally:
        # Clean up temporary file
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)



@given(
    logo_height=st.integers(min_value=10, max_value=200),
    margin=st.integers(min_value=5, max_value=50),
    line_height=st.integers(min_value=10, max_value=50),
)
def test_configuration_round_trip_preserves_data(
    logo_height: int,
    margin: int,
    line_height: int,
) -> None:
    """Feature: cross-platform-compatibility, Property 6: Configuration round-trip with format preservation.

    Validates: Requirements 8.2, 8.3

    For any configuration content, when saved and then loaded, the system should
    preserve the data values correctly across platforms.
    """
    from src.email_signature.infrastructure.platform_utils import (
        LineEndingHandler,
        PathManager,
    )

    temp_path = None

    try:
        # Create configuration data
        config_data = {
            "signature": {
                "dimensions": {
                    "logo_height": logo_height,
                    "margin": margin,
                    "line_height": line_height,
                },
                "colors": {
                    "outline": [255, 255, 255],
                    "name": [51, 51, 51],
                },
                "fonts": {
                    "linux": ["/usr/share/fonts/test.ttf"],
                    "windows": ["C:\\Windows\\Fonts\\test.ttf"],
                },
            }
        }

        # Create temporary file path
        temp_dir = Path(tempfile.gettempdir())
        temp_path = temp_dir / f"test_config_{logo_height}_{margin}.yaml"

        # Write config using platform-native line endings
        config_content = yaml.dump(config_data, default_flow_style=False, sort_keys=False)
        LineEndingHandler.write_text_platform(temp_path, config_content)

        # Read back using universal line ending handling
        read_content = LineEndingHandler.read_text_universal(temp_path)

        # Parse the read content
        parsed_data = yaml.safe_load(read_content)

        # Verify data is preserved
        assert parsed_data["signature"]["dimensions"]["logo_height"] == logo_height
        assert parsed_data["signature"]["dimensions"]["margin"] == margin
        assert parsed_data["signature"]["dimensions"]["line_height"] == line_height

        # Also verify through ConfigLoader
        config = ConfigLoader.load(str(temp_path))
        assert config.logo_height == logo_height
        assert config.margin == margin
        assert config.line_height == line_height

    finally:
        # Clean up temporary file
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)


@given(
    element_order=st.permutations([
        "logo",
        "name",
        "position",
        "address",
        "phone",
        "email",
        "separator",
        "confidentiality",
    ])
)
def test_element_order_persistence_round_trip(element_order: list[str]) -> None:
    """Feature: gui-settings-preview, Property 6: Element order persistence round-trip.

    Validates: Requirements 2.5, 2.6

    For any element order configuration, saving and then loading the configuration
    SHALL preserve the element order.
    """
    temp_path = None

    try:
        # Create a SignatureConfig with the given element order
        config = SignatureConfig()
        config.element_order = list(element_order)

        # Create temporary file path
        temp_dir = Path(tempfile.gettempdir())
        temp_path = temp_dir / f"test_element_order_{hash(tuple(element_order))}.yaml"

        # Save the configuration
        ConfigLoader.save(config, str(temp_path))

        # Load the configuration back
        loaded_config = ConfigLoader.load(str(temp_path))

        # Verify element order is preserved
        assert loaded_config.element_order == list(element_order), (
            f"Element order not preserved. Expected {list(element_order)}, "
            f"got {loaded_config.element_order}"
        )

    finally:
        # Clean up temporary file
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)
