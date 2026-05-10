"""
schedule_image.py — generates a polished PNG of the match schedule.
Requires: Pillow  (pip install Pillow)
"""

from PIL import Image, ImageDraw, ImageFont
import io
import os
from datetime import datetime

# ── Palette ───────────────────────────────────────────────────────────────────
BG_TOP      = (10,  20,  50)   # deep navy
BG_BOT      = (5,   10,  30)   # near black
ACCENT      = (220, 50,  50)   # club red
GOLD        = (212, 175, 55)   # gold
WHITE       = (255, 255, 255)
LIGHT_GREY  = (190, 200, 220)
ROW_EVEN    = (18,  33,  70)
ROW_ODD     = (14,  25,  55)
ROW_BORDER  = (40,  60, 110)
HOME_BADGE  = (30, 180, 80)
AWAY_BADGE  = (200, 80, 30)

# ── Dimensions ────────────────────────────────────────────────────────────────
W           = 1100
HEADER_H    = 160
ROW_H       = 68
FOOTER_H    = 60
COL_DATE    = 30
COL_HVA     = 240
COL_OPP     = 280
COL_COMP    = 620
COL_LOC     = 760
COL_RES     = 1010

def _font(size, bold=False):
    """Try to load a nice font; fall back to default."""
    candidates_bold = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        '/Library/Fonts/Arial Bold.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
    ]
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/Library/Fonts/Arial.ttf',
        'C:/Windows/Fonts/arial.ttf',
    ]
    pool = candidates_bold if bold else candidates
    for path in pool:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def _gradient_bg(draw, w, h):
    for y in range(h):
        t = y / h
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

def generate_schedule_png(matches: list) -> bytes:
    n_rows  = max(len(matches), 1)
    height  = HEADER_H + n_rows * ROW_H + FOOTER_H + 20

    img  = Image.new('RGB', (W, height))
    draw = ImageDraw.Draw(img)

    # Background gradient
    _gradient_bg(draw, W, height)

    # Accent stripe at very top
    draw.rectangle([(0, 0), (W, 6)], fill=ACCENT)

    # ── Header ────────────────────────────────────────────────────────────────
    # Club crest placeholder (circle with initials)
    cx, cy, cr = 70, HEADER_H // 2, 42
    draw.ellipse([(cx-cr, cy-cr), (cx+cr, cy+cr)], fill=ACCENT, outline=GOLD, width=3)
    f_crest = _font(18, bold=True)
    draw.text((cx, cy), 'FCI', font=f_crest, fill=WHITE, anchor='mm')

    f_title  = _font(38, bold=True)
    f_sub    = _font(17)
    draw.text((130, 38), 'FC IRONWALL', font=f_title, fill=WHITE)
    draw.text((132, 88), 'Official Match Schedule  ·  2025 Season', font=f_sub, fill=GOLD)

    # Generated date (right side)
    f_gen = _font(13)
    gen_str = f"Generated {datetime.now().strftime('%d %b %Y')}"
    draw.text((W - 20, HEADER_H - 22), gen_str, font=f_gen, fill=LIGHT_GREY, anchor='ra')

    # Separator line
    draw.rectangle([(0, HEADER_H - 4), (W, HEADER_H)], fill=ACCENT)

    # ── Column headers ────────────────────────────────────────────────────────
    hdr_y    = HEADER_H + 6
    hdr_h    = 36
    draw.rectangle([(0, HEADER_H), (W, HEADER_H + hdr_h)], fill=(25, 45, 95))
    f_hdr    = _font(13, bold=True)
    headers  = [
        (COL_DATE,  'DATE & TIME'),
        (COL_HVA,   'H/A'),
        (COL_OPP,   'OPPONENT'),
        (COL_COMP,  'COMPETITION'),
        (COL_LOC,   'VENUE'),
        (COL_RES,   'RESULT'),
    ]
    for x, label in headers:
        draw.text((x + 8, hdr_y + 2), label, font=f_hdr, fill=GOLD)

    # ── Rows ──────────────────────────────────────────────────────────────────
    f_main = _font(14, bold=True)
    f_sub2 = _font(13)
    f_badge = _font(12, bold=True)

    for i, m in enumerate(matches):
        y0 = HEADER_H + hdr_h + i * ROW_H
        y1 = y0 + ROW_H
        row_color = ROW_EVEN if i % 2 == 0 else ROW_ODD
        draw.rectangle([(0, y0), (W, y1)], fill=row_color)
        draw.line([(0, y1), (W, y1)], fill=ROW_BORDER)

        mid_y = y0 + ROW_H // 2

        # Date
        if isinstance(m['match_date'], str):
            dt = datetime.strptime(m['match_date'], '%Y-%m-%d %H:%M:%S')
        else:
            dt = m['match_date']
        draw.text((COL_DATE + 8, mid_y - 10), dt.strftime('%a %d %b %Y'), font=f_main, fill=WHITE, anchor='lm')
        draw.text((COL_DATE + 8, mid_y + 10), dt.strftime('%H:%M'),        font=f_sub2,  fill=LIGHT_GREY, anchor='lm')

        # Home/Away badge
        is_home = m['is_home'] if isinstance(m['is_home'], bool) else bool(m['is_home'])
        badge_col  = HOME_BADGE if is_home else AWAY_BADGE
        badge_text = 'HOME' if is_home else 'AWAY'
        bx = COL_HVA + 8
        draw.rounded_rectangle([(bx, mid_y - 12), (bx + 52, mid_y + 12)], radius=4, fill=badge_col)
        draw.text((bx + 26, mid_y), badge_text, font=f_badge, fill=WHITE, anchor='mm')

        # Opponent
        draw.text((COL_OPP + 8, mid_y), m['opponent'], font=f_main, fill=WHITE, anchor='lm')

        # Competition
        draw.text((COL_COMP + 8, mid_y), m['competition'], font=f_sub2, fill=LIGHT_GREY, anchor='lm')

        # Venue (truncated)
        venue = m['location']
        if len(venue) > 28:
            venue = venue[:26] + '…'
        draw.text((COL_LOC + 8, mid_y), venue, font=f_sub2, fill=LIGHT_GREY, anchor='lm')

        # Result
        result = m.get('result') or '—'
        res_color = GOLD if result != '—' else LIGHT_GREY
        draw.text((COL_RES + 8, mid_y), result, font=f_main, fill=res_color, anchor='lm')

    # ── Footer ────────────────────────────────────────────────────────────────
    fy = HEADER_H + hdr_h + n_rows * ROW_H
    draw.rectangle([(0, fy), (W, fy + FOOTER_H)], fill=(10, 18, 45))
    draw.rectangle([(0, fy), (W, fy + 3)], fill=ACCENT)
    f_foot = _font(13)
    draw.text((W // 2, fy + FOOTER_H // 2),
              'FC Ironwall  ·  www.fcironwall.com  ·  info@fcironwall.com',
              font=f_foot, fill=LIGHT_GREY, anchor='mm')

    # ── Serialize ─────────────────────────────────────────────────────────────
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return buf.getvalue()
