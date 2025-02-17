import ctypes
import win32con
import random
from PIL import Image, ImageDraw, ImageFont
import math

def generate_gradient_background(width, height, start_color, end_color):
    """Generate a gradient background from start_color to end_color."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    for i in range(width):
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (i / width))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (i / width))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (i / width))
        draw.line((i, 0, i, height), fill=(r, g, b))
    
    return img

def create_pulsing_effect(img, mood, width, height):
    """Create a pulsing effect for the 'gaming' mood."""
    draw = ImageDraw.Draw(img)
    for _ in range(3000):  # Draw more particles for a more dynamic effect
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        radius = int(math.sin(random.random() * 2 * math.pi) * 20 + 50)  # Pulse effect
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)

def create_neon_text(draw, text, position, font, neon_color, glow_color):
    """Create neon-style text with a glowing effect."""
    x, y = position
    # Create glow effect
    for offset in range(-10, 10, 2):
        draw.text((x + offset, y + offset), text, fill=glow_color, font=font)
    # Create actual text
    draw.text((x, y), text, fill=neon_color, font=font)

def create_mood_wallpaper(mood):
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    if mood == "focus":
        # Dark, simple design with no distractions
        img = generate_gradient_background(width, height, (25, 25, 25), (0, 0, 0))
        draw.text((width // 2 - 200, height // 2), "Focus Mode", fill=(255, 255, 255), font=ImageFont.load_default())

    elif mood == "gaming":
        # Dynamic RGB pattern with pulsing effect
        img = generate_gradient_background(width, height, (0, 0, 0), (0, 0, 50))
        create_pulsing_effect(img, mood, width, height)
        draw.text((width // 2 - 250, height // 2), "Game On!", fill=(255, 255, 255), font=ImageFont.load_default())

    elif mood == "relaxed":
        # Light, calming gradient with soft colors
        img = generate_gradient_background(width, height, (173, 216, 230), (255, 240, 245))
        draw.text((width // 2 - 200, height // 2), "Relax & Unwind", fill=(100, 100, 100), font=ImageFont.load_default())

    elif mood == "inspired":
        # Neon glowing effect text with a bold background
        img = generate_gradient_background(width, height, (255, 140, 0), (255, 223, 0))
        font = ImageFont.truetype("arial.ttf", size=100)
        create_neon_text(draw, "Stay Inspired", (width // 2 - 300, height // 2), font, neon_color=(0, 255, 255), glow_color=(0, 255, 255))

    # Save the wallpaper image
    img.save("dynamic_wallpaper.jpg")

    # Set the wallpaper
    ctypes.windll.user32.SystemParametersInfoW(win32con.SPI_SETDESKWALLPAPER, 0, "dynamic_wallpaper.jpg", 3)

if __name__ == "__main__":
    # Choose a mood to create wallpaper
    create_mood_wallpaper("gaming")
