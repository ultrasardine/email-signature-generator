"""Image rendering for email signature generation."""

import logging
import platform
import warnings
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from ..domain.config import SignatureConfig
from ..domain.models import SignatureData
from .platform_utils import FontLocator, PathManager

logger = logging.getLogger(__name__)


class ImageRenderError(Exception):
    """Raised when image rendering fails."""

    pass


class ImageRenderer:
    """Handles image creation and text rendering."""

    def __init__(self, config: SignatureConfig) -> None:
        """Initialize ImageRenderer with configuration.

        Args:
            config: SignatureConfig object with rendering settings
        """
        self.config = config
        self.fonts = self._load_fonts()

    def _load_fonts(self) -> dict[str, Any]:
        """Load fonts with platform-specific fallback chain.

        Returns:
            Dictionary with 'bold' and 'regular' font objects
        """
        system = platform.system().lower()

        # Map platform.system() output to our config keys
        platform_map = {
            "linux": "linux",
            "windows": "windows",
            "darwin": "darwin",
        }

        platform_key = platform_map.get(system, "linux")
        font_paths = self.config.font_paths.get(platform_key, [])

        fonts = {}

        # Try to load bold font (first in list)
        bold_font = self._try_load_font(font_paths[0:1] if font_paths else [], size=16)
        if bold_font:
            fonts["bold"] = bold_font
            logger.info("Loaded bold font successfully")
        else:
            # Try to find a default bold font using FontLocator
            default_fonts = FontLocator.get_default_fonts()
            default_sans_serif = default_fonts.get('sans-serif', 'Arial')
            
            # Try to find the default font
            default_font_path = FontLocator.find_font(default_sans_serif)
            if default_font_path:
                try:
                    fonts["bold"] = ImageFont.truetype(str(default_font_path), 16)
                    logger.info(f"Loaded default bold font: {default_sans_serif}")
                except Exception as e:
                    logger.warning(f"Could not load default font {default_sans_serif}: {e}")
                    fonts["bold"] = ImageFont.load_default()
                    from .platform_utils import ErrorMessageFormatter
                    font_hint = ErrorMessageFormatter.get_font_location_hint()
                    warnings.warn(
                        f"Could not load bold font, using PIL default font. "
                        f"Consider installing {default_sans_serif} or specifying a valid font path.\n\n"
                        f"{font_hint}"
                    )
            else:
                logger.warning(f"Could not find default font {default_sans_serif}, using PIL default")
                fonts["bold"] = ImageFont.load_default()
                from .platform_utils import ErrorMessageFormatter
                font_hint = ErrorMessageFormatter.get_font_location_hint()
                warnings.warn(
                    f"Could not find font {default_sans_serif}. "
                    f"Using PIL default font. For better results, install system fonts.\n\n"
                    f"{font_hint}"
                )

        # Try to load regular font (second in list)
        regular_font = self._try_load_font(font_paths[1:2] if len(font_paths) > 1 else [], size=14)
        if regular_font:
            fonts["regular"] = regular_font
            logger.info("Loaded regular font successfully")
        else:
            # Try to find a default regular font using FontLocator
            default_fonts = FontLocator.get_default_fonts()
            default_sans_serif = default_fonts.get('sans-serif', 'Arial')
            
            # Try to find the default font
            default_font_path = FontLocator.find_font(default_sans_serif)
            if default_font_path:
                try:
                    fonts["regular"] = ImageFont.truetype(str(default_font_path), 14)
                    logger.info(f"Loaded default regular font: {default_sans_serif}")
                except Exception as e:
                    logger.warning(f"Could not load default font {default_sans_serif}: {e}")
                    fonts["regular"] = ImageFont.load_default()
                    from .platform_utils import ErrorMessageFormatter
                    font_hint = ErrorMessageFormatter.get_font_location_hint()
                    warnings.warn(
                        f"Could not load regular font, using PIL default font. "
                        f"Consider installing {default_sans_serif} or specifying a valid font path.\n\n"
                        f"{font_hint}"
                    )
            else:
                logger.warning(f"Could not find default font {default_sans_serif}, using PIL default")
                fonts["regular"] = ImageFont.load_default()
                from .platform_utils import ErrorMessageFormatter
                font_hint = ErrorMessageFormatter.get_font_location_hint()
                warnings.warn(
                    f"Could not find font {default_sans_serif}. "
                    f"Using PIL default font. For better results, install system fonts.\n\n"
                    f"{font_hint}"
                )

        return fonts

    def _try_load_font(self, font_paths: list[str], size: int) -> Any:
        """Try to load a font from a list of paths.

        Args:
            font_paths: List of font file paths to try
            size: Font size in points

        Returns:
            Loaded font or None if all paths fail
        """
        for font_path in font_paths:
            try:
                path = PathManager.normalize(font_path)
                
                # Validate the font path using FontLocator
                if not FontLocator.validate_font_path(path):
                    logger.debug(f"Font path validation failed for {font_path}")
                    
                    # Try to find the font by name using FontLocator
                    # Extract just the filename without path
                    font_name = Path(font_path).name
                    found_path = FontLocator.find_font(font_name)
                    
                    if found_path:
                        logger.debug(f"Found font {font_name} at {found_path}")
                        path = found_path
                    else:
                        logger.debug(f"Could not find font {font_name} in system directories")
                        from .platform_utils import ErrorMessageFormatter
                        font_hint = ErrorMessageFormatter.get_font_location_hint()
                        warnings.warn(
                            f"Font not found: {font_path}. "
                            f"Searched in system font directories but could not locate it.\n\n"
                            f"{font_hint}"
                        )
                        continue
                
                # Try to load the font
                if PathManager.exists(path):
                    font = ImageFont.truetype(str(path), size)
                    logger.debug(f"Successfully loaded font from {path}")
                    return font
                else:
                    logger.debug(f"Font path does not exist: {path}")
                    
            except Exception as e:
                logger.debug(f"Failed to load font from {font_path}: {e}")
                continue

        return None

    def draw_text_with_outline(
        self,
        draw: Any,
        text: str,
        position: tuple[int, int],
        font: Any,
        outline_color: tuple[int, int, int] | tuple[int, ...],
        text_color: tuple[int, int, int] | tuple[int, ...],
        outline_width: int,
    ) -> None:
        """Draw text with outline for contrast.

        Args:
            draw: ImageDraw object to draw on
            text: Text string to render
            position: (x, y) position for text
            font: Font to use for rendering
            outline_color: RGB color for outline
            text_color: RGB color for text
            outline_width: Width of outline in pixels
        """
        x, y = position

        # Draw outline by rendering text at offset positions
        for offset_x in range(-outline_width, outline_width + 1):
            for offset_y in range(-outline_width, outline_width + 1):
                if offset_x != 0 or offset_y != 0:
                    draw.text((x + offset_x, y + offset_y), text, font=font, fill=outline_color)

        # Draw main text on top
        draw.text((x, y), text, font=font, fill=text_color)

    def create_signature_image(
        self, signature_data: SignatureData, logo: Image.Image
    ) -> Image.Image:
        """Create the signature image.

        Args:
            signature_data: User data for the signature
            logo: Logo image (already resized)

        Returns:
            Generated signature image with transparent background

        Raises:
            ImageRenderError: If image rendering fails
        """
        try:
            # Get configuration values
            margin = self.config.margin
            logo_margin_right = self.config.logo_margin_right
            line_height = self.config.line_height

            # Get colors from current config (ensures we use updated values)
            outline_color = self.config.colors.get("outline", (255, 255, 255))
            name_color = self.config.colors.get("name", (51, 51, 51))
            details_color = self.config.colors.get("details", (100, 100, 100))
            separator_color = self.config.colors.get("separator", (200, 0, 40, 200))
            confidentiality_color = self.config.colors.get("confidentiality", (150, 150, 150))

            # Get fonts
            bold_font = self.fonts["bold"]
            regular_font = self.fonts["regular"]

            # Create smaller font for confidentiality notice
            # Try to create a smaller version of the regular font
            try:
                if hasattr(regular_font, "path") and hasattr(regular_font, "size"):
                    small_font = ImageFont.truetype(regular_font.path, int(regular_font.size * 0.7))
                else:
                    small_font = regular_font  # Fallback to regular font
            except Exception:
                small_font = regular_font  # Fallback to regular font

            # Calculate text dimensions to determine image size
            # We'll create a temporary draw object to measure text
            temp_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)

            # Measure name
            name_bbox = temp_draw.textbbox((0, 0), signature_data.name, font=bold_font)
            name_width = name_bbox[2] - name_bbox[0]

            # Prepare element content mapping
            phone_line = self._build_phone_line(signature_data)
            email_line = f"{signature_data.email} | {signature_data.website}"

            # Map element IDs to their content and rendering properties
            element_content = {
                "name": signature_data.name,
                "position": signature_data.position,
                "address": signature_data.address,
                "phone": phone_line,
                "email": email_line,
            }

            # Measure max text width for all text elements
            max_text_width = name_width
            for element_id in ["position", "address", "phone", "email"]:
                content = element_content.get(element_id, "")
                if content:
                    bbox = temp_draw.textbbox((0, 0), content, font=regular_font)
                    line_width = bbox[2] - bbox[0]
                    max_text_width = max(max_text_width, line_width)

            # Measure confidentiality notice
            conf_bbox = temp_draw.textbbox(
                (0, 0), self.config.confidentiality_text, font=small_font
            )
            conf_width = conf_bbox[2] - conf_bbox[0]

            # Calculate image dimensions
            logo_width = logo.size[0]
            text_x = margin + logo_width + logo_margin_right

            # Image width should accommodate logo + text + margins
            image_width = int(text_x + max(max_text_width, conf_width) + margin)

            # Get element order from config, with fallback to default
            element_order = getattr(self.config, 'element_order', None)
            if not element_order:
                element_order = [
                    "logo", "name", "position", "address",
                    "phone", "email", "separator", "confidentiality"
                ]

            # Count text elements for height calculation
            text_element_count = sum(
                1 for e in element_order
                if e in element_content and element_content.get(e)
            )
            has_separator = "separator" in element_order
            has_confidentiality = "confidentiality" in element_order

            # Calculate height needed for all elements
            text_height = (
                margin  # top margin
                + line_height * text_element_count  # text lines
                + (line_height if has_separator else 0)  # separator space
                + (line_height * 2 if has_confidentiality else 0)  # confidentiality notice
                + margin  # bottom margin
            )

            logo_height_total = margin + logo.size[1] + margin
            image_height = int(max(text_height, logo_height_total))

            # Create RGBA image with transparent background
            image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            # Render elements in the specified order
            y_position = margin
            logo_rendered = False

            for element_id in element_order:
                # Handle missing elements gracefully
                if element_id == "logo":
                    if not logo_rendered:
                        image.paste(logo, (margin, margin), logo)
                        logo_rendered = True
                elif element_id == "name":
                    self.draw_text_with_outline(
                        draw,
                        signature_data.name,
                        (text_x, y_position),
                        bold_font,
                        outline_color,
                        name_color,
                        self.config.outline_width_name,
                    )
                    y_position += line_height
                elif element_id == "position":
                    self.draw_text_with_outline(
                        draw,
                        signature_data.position,
                        (text_x, y_position),
                        regular_font,
                        outline_color,
                        details_color,
                        self.config.outline_width_text,
                    )
                    y_position += line_height
                elif element_id == "address":
                    self.draw_text_with_outline(
                        draw,
                        signature_data.address,
                        (text_x, y_position),
                        regular_font,
                        outline_color,
                        details_color,
                        self.config.outline_width_text,
                    )
                    y_position += line_height
                elif element_id == "phone":
                    if phone_line:
                        self.draw_text_with_outline(
                            draw,
                            phone_line,
                            (text_x, y_position),
                            regular_font,
                            outline_color,
                            details_color,
                            self.config.outline_width_text,
                        )
                        y_position += line_height
                elif element_id == "email":
                    self.draw_text_with_outline(
                        draw,
                        email_line,
                        (text_x, y_position),
                        regular_font,
                        outline_color,
                        details_color,
                        self.config.outline_width_text,
                    )
                    y_position += line_height
                elif element_id == "separator":
                    y_position += int(line_height * 0.3)
                    separator_start = (text_x, y_position)
                    separator_end = (text_x + max_text_width, y_position)
                    draw.line([separator_start, separator_end], fill=separator_color, width=2)
                    y_position += int(line_height * 0.7)
                elif element_id == "confidentiality":
                    self.draw_text_with_outline(
                        draw,
                        self.config.confidentiality_text,
                        (text_x, y_position),
                        small_font,
                        outline_color,
                        confidentiality_color,
                        self.config.outline_width_text,
                    )
                    y_position += line_height
                # Unknown elements are silently ignored (handle missing elements gracefully)

            return image

        except Exception as e:
            logger.error(f"Failed to render signature image: {e}")
            raise ImageRenderError(f"Failed to render signature image: {e}") from e

    def _build_phone_line(self, signature_data: SignatureData) -> str:
        """Build the phone line from signature data.

        Args:
            signature_data: User data for the signature

        Returns:
            Formatted phone line or empty string if no phone numbers
        """
        phone_parts = []
        if signature_data.phone:
            phone_parts.append(f"Tel: {signature_data.phone}")
        if signature_data.mobile:
            phone_parts.append(f"Tlm: {signature_data.mobile}")
        return " | ".join(phone_parts) if phone_parts else ""
