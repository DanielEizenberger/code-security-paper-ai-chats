from PIL import Image, ImageDraw, ImageFont
import os

def generate_schedule_image():
    """Generate a PNG image of the game schedule"""
    # Create an image with white background
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a nice font, fallback to default
    try:
        font_title = ImageFont.truetype("arial.ttf", 32)
        font_header = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 18)
    except:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Title
    draw.text((width//2 - 150, 30), "FC CHAMPIONS - GAME SCHEDULE", fill='black', font=font_title)
    
    # Schedule data (example)
    schedule = [
        ("Date", "Opponent", "Venue", "Time"),
        ("Mar 15, 2025", "City Rangers", "Home", "15:00"),
        ("Mar 22, 2025", "United FC", "Away", "17:30"),
        ("Mar 29, 2025", "Thunderbolts", "Home", "14:00"),
        ("Apr 5, 2025", "Legends FC", "Away", "16:00"),
        ("Apr 12, 2025", "Phoenix United", "Home", "15:00"),
        ("Apr 19, 2025", "Royal Kings", "Away", "18:00"),
    ]
    
    # Draw table
    y_start = 120
    row_height = 45
    col_widths = [150, 200, 150, 100]
    x_positions = [50, 200, 400, 550]
    
    # Header background
    for i, col in enumerate(schedule[0]):
        draw.rectangle([x_positions[i], y_start, x_positions[i] + col_widths[i], y_start + row_height], fill='lightgray', outline='black')
        draw.text((x_positions[i] + 10, y_start + 10), col, fill='black', font=font_header)
    
    # Rows
    y = y_start + row_height
    for row in schedule[1:]:
        for i, cell in enumerate(row):
            draw.rectangle([x_positions[i], y, x_positions[i] + col_widths[i], y + row_height], fill='white', outline='black')
            draw.text((x_positions[i] + 10, y + 10), cell, fill='black', font=font_text)
        y += row_height
    
    # Footer
    draw.text((50, height - 40), "* All times local. Home games at Champions Stadium. Tickets at gate.", fill='gray', font=font_text)
    
    # Save image
    static_dir = 'static'
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    img_path = os.path.join(static_dir, 'schedule.png')
    image.save(img_path)
    return img_path

if __name__ == '__main__':
    generate_schedule_image()