from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def generate_schedule_png(games):
    # Create image
    width, height = 800, 400 + (len(games) * 40)
    img = Image.new('RGB', (width, height), color=(34, 139, 34))  # Football green
    draw = ImageDraw.Draw(img)
    
    # Load fonts (default PIL font)
    try:
        title_font = ImageFont.truetype("arial.ttf", 32)
        header_font = ImageFont.truetype("arial.ttf", 24)
        text_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Title
    draw.text((width//2 - 150, 20), "⚽ FC CLUB SCHEDULE ⚽", fill="white", font=title_font)
    draw.text((width//2 - 100, 60), datetime.now().strftime("%B %Y"), fill="white", font=header_font)
    
    # Table headers
    y_start = 120
    draw.text((50, y_start), "Date", fill="yellow", font=header_font)
    draw.text((200, y_start), "Time", fill="yellow", font=header_font)
    draw.text((350, y_start), "Opponent", fill="yellow", font=header_font)
    draw.text((600, y_start), "Location", fill="yellow", font=header_font)
    
    # Draw line
    draw.line([(30, y_start + 30), (width - 30, y_start + 30)], fill="white", width=2)
    
    # Rows
    y = y_start + 50
    for game in games:
        date_str = game['game_date'].strftime("%d %b %Y") if hasattr(game['game_date'], 'strftime') else str(game['game_date'])
        time_str = str(game['game_time'])[:5] if game['game_time'] else "TBD"
        
        draw.text((50, y), date_str, fill="white", font=text_font)
        draw.text((200, y), time_str, fill="white", font=text_font)
        draw.text((350, y), game['opponent'], fill="white", font=text_font)
        draw.text((600, y), game['location'], fill="white", font=text_font)
        y += 40
    
    # Footer
    draw.text((width//2 - 200, height - 30), "⚽ Come support your team! ⚽", fill="white", font=title_font)
    
    # Save
    os.makedirs('static', exist_ok=True)
    img.save('static/schedule.png')
    return True