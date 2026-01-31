"""Generate Chinese Chess application icon.

This script creates a simple Chinese chess piece icon for the application.
The icon features a traditional Chinese chess piece design.
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_chess_icon(size: int = 256) -> Image.Image:
    """Create a Chinese chess piece icon.
    
    Args:
        size: The size of the icon in pixels.
    
    Returns:
        A PIL Image object containing the icon.
    """
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions
    margin = size * 0.08
    piece_size = size - 2 * margin
    center = size / 2
    radius = piece_size / 2
    
    # Draw outer ring (wood color border)
    outer_radius = radius
    draw.ellipse(
        [center - outer_radius, center - outer_radius,
         center + outer_radius, center + outer_radius],
        fill='#8B4513',  # Saddle brown
        outline='#654321',  # Dark brown
        width=int(size * 0.02)
    )
    
    # Draw inner circle (cream background)
    inner_radius = radius * 0.88
    draw.ellipse(
        [center - inner_radius, center - inner_radius,
         center + inner_radius, center + inner_radius],
        fill='#FFF5E6',  # Warm cream
        outline='#8B4513',
        width=int(size * 0.015)
    )
    
    # Draw the Chinese character "帥" (General/Commander)
    try:
        # Try to use a Chinese font
        font_size = int(size * 0.45)
        font = ImageFont.truetype("simsun.ttc", font_size)
    except (IOError, OSError):
        try:
            font = ImageFont.truetype("msyh.ttc", font_size)
        except (IOError, OSError):
            # Fallback to default font
            font = ImageFont.load_default()
    
    text = "帥"
    text_color = '#C41E3A'  # Cardinal red
    
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Draw text centered
    text_x = center - text_width / 2
    text_y = center - text_height / 2 - bbox[1]
    
    draw.text((text_x, text_y), text, fill=text_color, font=font)
    
    return img


def main():
    """Generate and save the application icon."""
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create icon in multiple sizes
    sizes = [256, 128, 64, 48, 32, 16]
    
    # Generate main icon
    icon_256 = create_chess_icon(256)
    
    # Save as PNG
    png_path = os.path.join(script_dir, 'resources', 'app_icon.png')
    icon_256.save(png_path, 'PNG')
    print(f"Saved: {png_path}")
    
    # Save as ICO (Windows icon with multiple sizes)
    ico_path = os.path.join(script_dir, 'resources', 'app_icon.ico')
    icons = [create_chess_icon(s) for s in sizes]
    icons[0].save(
        ico_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=icons[1:]
    )
    print(f"Saved: {ico_path}")


if __name__ == '__main__':
    main()
