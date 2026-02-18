from PIL import Image, ImageDraw, ImageFont

# Create a new image with white background
img = Image.new('RGB', (800, 200), color='white')
d = ImageDraw.Draw(img)

# Text to be OCR'd
text = "What is the total transaction amount for UPI?"

# Use default font
d.text((50, 80), text, fill=(0, 0, 0))

# Save the image
img.save('test_ocr_input.png')
print("Created test_ocr_input.png")
