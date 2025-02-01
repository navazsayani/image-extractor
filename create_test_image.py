from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_invoice():
    # Create a white image
    width = 800
    height = 1000
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Use a basic font
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Sample invoice content
    content = [
        ("INVOICE", (width//2, 50)),
        ("Invoice #: INV-2024-001", (50, 120)),
        ("Date: 01/02/2024", (50, 160)),
        ("Bill To:", (50, 220)),
        ("John Smith", (50, 260)),
        ("123 Main Street", (50, 300)),
        ("Email: john@example.com", (50, 340)),
        ("Phone: (555) 123-4567", (50, 380)),
        ("Description", (50, 460)),
        ("Web Development Services", (50, 500)),
        ("Amount: $1,500.00", (50, 540)),
        ("Tax (10%): $150.00", (50, 580)),
        ("Total: $1,650.00", (50, 620)),
    ]
    
    # Draw text on the image
    for text, position in content:
        draw.text(position, text, fill='black', font=font)
    
    # Save the image
    if not os.path.exists('test_images'):
        os.makedirs('test_images')
    
    image_path = os.path.join('test_images', 'sample_invoice.png')
    image.save(image_path)
    print(f"Test image created: {image_path}")
    return image_path

if __name__ == "__main__":
    create_sample_invoice()
