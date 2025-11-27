#!/usr/bin/env python3
"""Script to generate a generic placeholder logo for the email signature generator.

This script creates a simple, non-proprietary logo that can be used for
demonstration purposes without any legal concerns.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def create_generic_logo(output_path: str = "logo.png", size: int = 200) -> None:
    """Create a simple generic placeholder logo.

    Args:
        output_path: Path where the logo will be saved
        size: Size of the square logo in pixels (default: 200)
    """
    # Create image with transparency (RGBA)
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw simple circle with neutral blue-gray color
    circle_color = (100, 100, 150, 255)
    margin = 20
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=circle_color,
    )

    # Add text "LOGO"
    try:
        # Try to use a common system font
        font = ImageFont.truetype("Arial.ttf", 40)
    except OSError:
        try:
            # Fallback for Linux systems
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except OSError:
            # Use default font if no TrueType fonts available
            font = ImageFont.load_default()

    text = "LOGO"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2

    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)

    # Save as PNG
    img.save(output_path, "PNG")
    print(f"Generic logo created: {output_path}")
    print(f"Format: PNG, Mode: RGBA, Size: {size}x{size}")


if __name__ == "__main__":
    import sys

    # Allow custom output path from command line
    output_path = sys.argv[1] if len(sys.argv) > 1 else "logo_temp.png"
    create_generic_logo(output_path)
