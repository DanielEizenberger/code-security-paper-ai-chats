"""
Generates a styled PNG image of the match schedule using Pillow.
No external fonts required — uses built-in PIL fonts with fallback.
"""
import io
from PIL import Image, ImageDraw, ImageFont

# ── Palette ────────────────────────────────────────────────────────────────
BG_DARK      = (10,  18,  35)
BG_CARD      = (18,  28,  52)
ACCENT_GREEN = (0,   210, 120)
ACCENT_RED   = (220, 60,  60)
TEXT_WHITE   = (240, 240, 255)
TEXT_GREY    = (140, 155, 185)
GOLD         = (212, 175, 55)
LINE_COLOR   = (35,  52,  90)


def _font(size, bold=False):
    """Return a PIL font, falling back gracefully."""
    candidates_bold   = ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                         '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                         '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf']
    candidates_normal = ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                         '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                         '/usr/share/fonts/truetype/freefont/FreeSans.ttf']
    paths = candidates_bold if bold else candidates_normal
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def generate_schedule_image(matches) -> bytes:
    """Render schedule to PNG bytes."""
    ROW_H    = 54
    HEADER_H = 180
    FOOTER_H = 60
    WIDTH    = 880
    PADDING  = 40

    height = HEADER_H + len(matches) * ROW_H + FOOTER_H + PADDING
    img  = Image.new('RGB', (WIDTH, height), BG_DARK)
    draw = ImageDraw.Draw(img)

    # ── Background gradient-like stripes ──────────────────────────────────
    for y in range(height):
        shade = int(10 + (y / height) * 8)
        draw.line([(0, y), (WIDTH, y)], fill=(shade, shade + 8, shade + 25))

    # ── Club crest placeholder (circle + initials) ─────────────────────────
    cx, cy, r = 80, 85, 50
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT_GREEN)
    draw.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4], fill=BG_DARK)
    draw.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], fill=BG_CARD)
    f_crest = _font(22, bold=True)
    draw.text((cx, cy), 'FC', font=f_crest, fill=GOLD, anchor='mm')

    # ── Title block ─────────────────────────────────────────────────────────
    f_title    = _font(36, bold=True)
    f_subtitle = _font(16)
    f_season   = _font(13)

    draw.text((148, 52), 'FC IRONCLAD', font=f_title, fill=TEXT_WHITE)
    draw.text((148, 96), '2025 SEASON FIXTURE LIST', font=f_subtitle, fill=ACCENT_GREEN)
    draw.text((148, 122), 'Official Club Schedule  ·  All times local', font=f_season, fill=TEXT_GREY)

    # Gold divider
    draw.rectangle([PADDING, HEADER_H - 8, WIDTH - PADDING, HEADER_H - 6], fill=GOLD)

    # ── Column headers ──────────────────────────────────────────────────────
    f_head = _font(12, bold=True)
    cols   = {'#': 52, 'DATE': 80, 'TIME': 195, 'OPPONENT': 265, 'COMP': 560, 'H/A': 680, 'RESULT': 760}
    hy     = HEADER_H + 10
    draw.rectangle([0, HEADER_H, WIDTH, HEADER_H + ROW_H - 2], fill=BG_CARD)
    for label, x in cols.items():
        draw.text((x, hy), label, font=f_head, fill=ACCENT_GREEN)

    # ── Rows ────────────────────────────────────────────────────────────────
    f_body  = _font(14)
    f_small = _font(12)

    for i, m in enumerate(matches):
        y0 = HEADER_H + ROW_H + i * ROW_H
        # Alternating row tint
        if i % 2 == 0:
            draw.rectangle([0, y0, WIDTH, y0 + ROW_H - 1], fill=(15, 24, 44))
        else:
            draw.rectangle([0, y0, WIDTH, y0 + ROW_H - 1], fill=BG_DARK)

        row_y = y0 + 18

        # Index
        draw.text((cols['#'], row_y), str(i + 1), font=f_small, fill=TEXT_GREY)

        # Date nicely formatted
        try:
            from datetime import datetime as dt
            d = dt.strptime(m.date, '%Y-%m-%d')
            date_str = d.strftime('%d %b %Y')
        except Exception:
            date_str = m.date
        draw.text((cols['DATE'], row_y), date_str, font=f_body, fill=TEXT_WHITE)

        draw.text((cols['TIME'], row_y), m.time, font=f_body, fill=TEXT_WHITE)
        # Truncate long opponent names
        opp = m.opponent if len(m.opponent) <= 28 else m.opponent[:25] + '…'
        draw.text((cols['OPPONENT'], row_y), opp, font=f_body, fill=TEXT_WHITE)

        # Competition badge
        comp_color = GOLD if 'Cup' in m.competition else TEXT_GREY
        draw.text((cols['COMP'], row_y), m.competition, font=f_small, fill=comp_color)

        # Home / Away pill
        ha_color = ACCENT_GREEN if m.location == 'Home' else ACCENT_RED
        px, py = cols['H/A'], row_y - 2
        draw.rounded_rectangle([px - 4, py - 1, px + 38, py + 18], radius=4, fill=ha_color)
        draw.text((px + 4, py + 1), m.location, font=f_small, fill=BG_DARK)

        # Result
        if m.result:
            draw.text((cols['RESULT'], row_y), m.result, font=f_body, fill=GOLD)
        else:
            draw.text((cols['RESULT'], row_y), '—', font=f_body, fill=TEXT_GREY)

        # Subtle row divider
        draw.line([(PADDING, y0 + ROW_H - 1), (WIDTH - PADDING, y0 + ROW_H - 1)], fill=LINE_COLOR)

    # ── Footer ───────────────────────────────────────────────────────────────
    fy = HEADER_H + ROW_H + len(matches) * ROW_H + 20
    draw.rectangle([0, fy - 10, WIDTH, height], fill=BG_CARD)
    f_foot = _font(12)
    draw.text((PADDING, fy), 'fc-ironclad.example.com', font=f_foot, fill=TEXT_GREY)
    draw.text((WIDTH - PADDING, fy), '© 2025 FC Ironclad', font=f_foot, fill=TEXT_GREY, anchor='ra')

    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return buf.getvalue()
