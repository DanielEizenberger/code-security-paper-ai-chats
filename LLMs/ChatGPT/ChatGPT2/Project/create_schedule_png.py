from PIL import Image, ImageDraw, ImageFont

width = 1000
height = 700

image = Image.new('RGB', (width, height), color=(20, 20, 20))

draw = ImageDraw.Draw(image)

# Title

draw.text(
    (40, 40),
    'Football Club 2026 Schedule',
    fill=(255, 255, 255)
)

matches = [
    'May 15 - FC Eagles vs Tigers',
    'May 22 - FC Eagles vs Lions',
    'June 05 - FC Eagles vs Sharks',
    'June 12 - FC Eagles vs Wolves',
    'June 19 - FC Eagles vs Panthers'
]

start_y = 120

for match in matches:
    draw.text((60, start_y), match, fill=(200, 200, 200))
    start_y += 80

image.save('static/schedules/season_schedule.png')

print('Schedule PNG generated successfully.')
