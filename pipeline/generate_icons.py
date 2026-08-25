"""
Generates PWA App Icons (192x192, 512x512) and Favicon for the Borewell Siting PWA.
"""
import os
from PIL import Image, ImageDraw, ImageFont

def generate_icons(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    sizes = [192, 512, 64, 32]
    for size in sizes:
        img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Rounded background rectangle
        radius = int(size * 0.22)
        draw.rounded_rectangle([(0, 0), (size, size)], radius=radius, fill=(2, 132, 199, 255))
        
        # Inner gradient-like ring
        inner_pad = int(size * 0.08)
        draw.rounded_rectangle(
            [(inner_pad, inner_pad), (size - inner_pad, size - inner_pad)],
            radius=int(radius * 0.8),
            fill=(14, 165, 233, 255)
        )
        
        # Water droplet / well siting symbol
        cx, cy = size // 2, size // 2
        r = int(size * 0.28)
        
        # Draw concentric target rings (siting symbol)
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(255, 255, 255, 255), width=max(2, size // 32))
        r2 = int(r * 0.6)
        draw.ellipse([(cx - r2, cy - r2), (cx + r2, cy + r2)], outline=(255, 255, 255, 220), width=max(2, size // 40))
        r3 = int(r * 0.25)
        draw.ellipse([(cx - r3, cy - r3), (cx + r3, cy + r3)], fill=(255, 255, 255, 255))
        
        filename = f"icon-{size}.png" if size > 64 else f"favicon-{size}.png"
        img.save(os.path.join(output_dir, filename), 'PNG')
        if size == 32:
            img.save(os.path.join(output_dir, "favicon.ico"), 'ICO')

    print(f"PWA icons successfully generated in {output_dir}")

if __name__ == "__main__":
    icon_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web", "icons"))
    generate_icons(icon_dir)
