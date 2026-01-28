#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont

# Create a 192x192 favicon (high res for retina displays)
size = 192
radius = 30  # Corner radius for rounded edges

# Create the image with transparency
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw rounded rectangle background
draw.rounded_rectangle([(0, 0), (size, size)], radius=radius, fill='#f5f0e6')

# Load the AGRevue font at a smaller size to fit better
font_path = 'fonts/AGRevueCyr Roman Medium.ttf'
font = ImageFont.truetype(font_path, 80)

# Draw YAG text in dark brown
text = "YAG"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Center the text with proper padding
x = (size - text_width) // 2
y = (size - text_height) // 2

# Draw the text
draw.text((x, y), text, fill='#8B7355', font=font)

# Save as PNG
img.save('favicon.png')
print("✅ Created favicon.png with AGRevue font and rounded corners")
