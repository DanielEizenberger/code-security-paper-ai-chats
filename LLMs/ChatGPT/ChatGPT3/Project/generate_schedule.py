from PIL import Image, ImageDraw, ImageFont

schedule = [
    "Football Club Schedule",
    "",
    "May 20 - FC Eagles vs Thunder",
    "May 27 - FC Eagles vs Wolves",
    "June 3 - FC Eagles vs Lions",
    "June 10 - FC Eagles vs Hawks",
]

width = 1000
height = 600

image = Image.new("RGB", (width, height), color=(15, 30, 60))
draw = ImageDraw.Draw(image)

try:
    title_font = ImageFont.truetype("arial.ttf", 42)
    text_font = ImageFont.truetype("arial.ttf", 28)
except:
    title_font = ImageFont.load_default()
    text_font = ImageFont.load_default()

current_y = 60

for i, line in enumerate(schedule):
    font = title_font if i == 0 else text_font
    draw.text((60, current_y), line, fill=(255, 255, 255), font=font)
    current_y += 70

image.save("static/images/game_schedule.png")

print("Schedule PNG generated successfully.")
