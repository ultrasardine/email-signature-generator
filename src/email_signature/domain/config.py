"""Configuration models for email signature generation."""

from dataclasses import dataclass, field


@dataclass
class SignatureConfig:
    """Configuration for signature generation.

    Attributes:
        logo_height: Target height for logo in pixels
        margin: Margin around signature elements in pixels
        logo_margin_right: Space between logo and text in pixels
        line_height: Height of each text line in pixels
        outline_width_name: Outline width for name text in pixels
        outline_width_text: Outline width for other text in pixels
        font_paths: Platform-specific font file paths
        colors: Color definitions for various elements
        logo_search_paths: Paths to search for logo files
        confidentiality_text: Legal confidentiality notice text
    """

    # Dimensions
    logo_height: int = 70
    margin: int = 15
    logo_margin_right: int = 20
    line_height: int = 22

    # Outline widths
    outline_width_name: int = 2
    outline_width_text: int = 1

    # Font paths by platform
    font_paths: dict[str, list[str]] = field(
        default_factory=lambda: {
            "linux": [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ],
            "windows": [
                "C:\\Windows\\Fonts\\arialbd.ttf",
                "C:\\Windows\\Fonts\\arial.ttf",
            ],
            "darwin": [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/HelveticaNeue.ttc",
            ],
        }
    )

    # Colors (RGB or RGBA tuples)
    colors: dict[str, tuple[int, ...]] = field(
        default_factory=lambda: {
            "outline": (255, 255, 255),
            "name": (51, 51, 51),
            "details": (100, 100, 100),
            "separator": (200, 0, 40, 200),
            "confidentiality": (150, 150, 150),
        }
    )

    # Logo search paths
    logo_search_paths: list[str] = field(
        default_factory=lambda: [
            "logo.png",
            "logo.jpg",
            "./logo/logo.png",
            "./logo/logo.jpg",
        ]
    )

    # Confidentiality text
    confidentiality_text: str = (
        "CONFIDENTIALITY: This message is intended solely for the use of the addressee "
        "and may contain confidential information."
    )


class ConfigLoader:
    """Loads and saves configuration from/to YAML file with defaults."""

    @staticmethod
    def load(config_path: str | None = None) -> SignatureConfig:
        """Load configuration from file or use defaults.

        Args:
            config_path: Path to YAML config file, None for defaults

        Returns:
            SignatureConfig object with loaded or default values
        """
        # Start with default config
        config = SignatureConfig()

        # If no config path provided, return defaults
        if config_path is None:
            return config

        # Try to load from file
        try:
            from pathlib import Path
            import warnings

            import yaml
            
            # Import PathManager, FontLocator, and LineEndingHandler for cross-platform path handling
            from ..infrastructure.platform_utils import (
                FontLocator,
                LineEndingHandler,
                PathManager,
            )

            config_file = PathManager.normalize(config_path)
            if not PathManager.exists(config_file):
                # File doesn't exist, return defaults
                return config

            # Use LineEndingHandler to read file with universal line ending support
            content = LineEndingHandler.read_text_universal(config_file)
            data = yaml.safe_load(content)

            # If file is empty or invalid, return defaults
            if not data or not isinstance(data, dict):
                return config

            # Extract signature section if it exists
            sig_data = data.get("signature", {})
            if not isinstance(sig_data, dict):
                return config

            # Load dimensions
            dimensions = sig_data.get("dimensions", {})
            if isinstance(dimensions, dict):
                # Update only the dimension fields, preserving other defaults
                if "logo_height" in dimensions:
                    config.logo_height = dimensions["logo_height"]
                if "margin" in dimensions:
                    config.margin = dimensions["margin"]
                if "logo_margin_right" in dimensions:
                    config.logo_margin_right = dimensions["logo_margin_right"]
                if "line_height" in dimensions:
                    config.line_height = dimensions["line_height"]

            # Load outline widths
            outline = sig_data.get("outline", {})
            if isinstance(outline, dict):
                config.outline_width_name = outline.get("name_width", config.outline_width_name)
                config.outline_width_text = outline.get("text_width", config.outline_width_text)

            # Load colors
            colors = sig_data.get("colors", {})
            if isinstance(colors, dict):
                for color_name, color_value in colors.items():
                    if isinstance(color_value, list) and len(color_value) in (3, 4):
                        config.colors[color_name] = tuple(color_value)

            # Load font paths with validation
            fonts = sig_data.get("fonts", {})
            if isinstance(fonts, dict):
                for platform, paths in fonts.items():
                    if isinstance(paths, list):
                        # Validate each font path
                        validated_paths = []
                        for font_path in paths:
                            path_obj = PathManager.normalize(font_path)
                            if FontLocator.validate_font_path(path_obj):
                                validated_paths.append(font_path)
                            else:
                                # Warn about invalid font path but don't fail
                                warnings.warn(
                                    f"Invalid font path in configuration: {font_path}. "
                                    f"Path does not exist, is not a file, or does not have a valid font extension. "
                                    f"This font will be skipped and fallback fonts will be used."
                                )
                        
                        # Only update if we have at least some valid paths
                        # Otherwise keep the defaults
                        if validated_paths:
                            config.font_paths[platform] = validated_paths

            # Load logo search paths
            logo = sig_data.get("logo", {})
            if isinstance(logo, dict):
                search_paths = logo.get("search_paths", [])
                if isinstance(search_paths, list) and search_paths:
                    config.logo_search_paths = search_paths

            # Load confidentiality text
            text = sig_data.get("text", {})
            if isinstance(text, dict):
                conf_text = text.get("confidentiality")
                if isinstance(conf_text, str):
                    config.confidentiality_text = conf_text

            return config

        except Exception:
            # Any error loading config, return defaults
            return config


    @staticmethod
    def save(config: SignatureConfig, config_path: str) -> None:
        """Save configuration to YAML file with platform-native line endings.

        Args:
            config: SignatureConfig object to save
            config_path: Path to YAML config file

        Raises:
            IOError: If file cannot be written
        """
        import yaml

        from ..infrastructure.platform_utils import LineEndingHandler, PathManager

        # Normalize the path
        config_file = PathManager.normalize(config_path)

        # Ensure parent directories exist
        PathManager.ensure_parent_dirs(config_file)

        # Convert config to dictionary
        config_data = {
            "signature": {
                "dimensions": {
                    "logo_height": config.logo_height,
                    "margin": config.margin,
                    "logo_margin_right": config.logo_margin_right,
                    "line_height": config.line_height,
                },
                "outline": {
                    "name_width": config.outline_width_name,
                    "text_width": config.outline_width_text,
                },
                "colors": {
                    name: list(color) for name, color in config.colors.items()
                },
                "fonts": config.font_paths,
                "logo": {
                    "search_paths": config.logo_search_paths,
                },
                "text": {
                    "confidentiality": config.confidentiality_text,
                },
            }
        }

        # Convert to YAML string
        yaml_content = yaml.dump(config_data, default_flow_style=False, sort_keys=False)

        # Write with platform-native line endings
        LineEndingHandler.write_text_platform(config_file, yaml_content)
