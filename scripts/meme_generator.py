import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

def get_text_size(draw, text, font):
    """
    Returns (width, height) of the given text using the textbbox method.
    """
    # Get the bounding box of the text starting at (0, 0)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

def create_meme(text, 
                template_path="template.jpg", 
                output_path="meme_result.jpg", 
                font_path="impact.ttf",
                watermark_text="© MyMemeGenerator"):
    # Try to open the image template.
    try:
        img = Image.open(template_path)
    except FileNotFoundError:
        print(f"Template file '{template_path}' not found.")
        return
    
    draw = ImageDraw.Draw(img)
    
    # Determine font size relative to image width and try to load the Impact font.
    try:
        font_size = int(img.width / 15)
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font file '{font_path}' not found. Using default font.")
        font = ImageFont.load_default()
        font_size = 20  # Fallback font size
    
    # If a delimiter is present, split the text into top and bottom parts.
    if "||" in text:
        top_text, bottom_text = text.split("||", 1)
    else:
        top_text, bottom_text = text, ""
    
    def draw_text_with_outline(text, pos_y):
        """Draws wrapped text (all in uppercase) centered horizontally with an outline."""
        # Convert text to uppercase for a classic meme look.
        text = text.upper()
        # Wrap text so that each line isn't too long.
        lines = textwrap.wrap(text, width=20)
        # Calculate total height of the text block.
        total_height = sum(get_text_size(draw, line, font)[1] for line in lines)
        current_y = pos_y
        outline_thickness = max(1, int(font_size / 15))
        
        for line in lines:
            line_width, line_height = get_text_size(draw, line, font)
            x = (img.width - line_width) / 2  # Center horizontally

            # Optionally, add a drop shadow (uncomment the next two lines to enable)
            # shadow_offset = outline_thickness
            # draw.text((x + shadow_offset, current_y + shadow_offset), line, font=font, fill="gray")
            
            # Draw outline (stroke) by drawing the text several times in a black color around the position.
            for adj_x in range(-outline_thickness, outline_thickness + 1):
                for adj_y in range(-outline_thickness, outline_thickness + 1):
                    draw.text((x + adj_x, current_y + adj_y), line, font=font, fill="black")
            # Draw the main text.
            draw.text((x, current_y), line, font=font, fill="white")
            current_y += line_height

    # Draw top text near the top of the image.
    if top_text:
        draw_text_with_outline(top_text, pos_y=10)
    
    # Draw bottom text near the bottom of the image.
    if bottom_text:
        # Calculate height for bottom text block.
        lines = textwrap.wrap(bottom_text.upper(), width=20)
        total_text_height = sum(get_text_size(draw, line, font)[1] for line in lines)
        draw_text_with_outline(bottom_text, pos_y=img.height - total_text_height - 10)
    
    # Optional: Add a small watermark at the bottom-right corner.
    watermark_font_size = max(12, int(font_size / 2))
    try:
        watermark_font = ImageFont.truetype(font_path, watermark_font_size)
    except IOError:
        watermark_font = ImageFont.load_default()
    watermark_width, watermark_height = get_text_size(draw, watermark_text, watermark_font)
    watermark_x = img.width - watermark_width - 10
    watermark_y = img.height - watermark_height - 10
    # Draw watermark with a slight outline.
    for adj_x in range(-1, 2):
        for adj_y in range(-1, 2):
            draw.text((watermark_x + adj_x, watermark_y + adj_y), watermark_text, font=watermark_font, fill="black")
    draw.text((watermark_x, watermark_y), watermark_text, font=watermark_font, fill="white")
    
    # Save the generated meme and open it.
    img.save(output_path)
    os.startfile(output_path)

# Example usage:
# To provide both top and bottom text, separate them with "||"
create_meme("When the chatbot actually solves your problem||#FeelingProud")
