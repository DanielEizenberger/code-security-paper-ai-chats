"""
schedule_image.py – Render the fixture list as a downloadable PNG.
"""

import io
import datetime
from PIL import Image, ImageDraw, ImageFont
import db

# ── Palette ──────────────────────────────────────────────────────────────────
BG          = (10,  14,  30)
HEADER_BG   = (20,  26,  58)
ROW_ODD     = (18,  24,  48)
ROW_EVEN    = (24,  32,  62)
ACCENT      = (220, 50,  50)
GOLD        = (255, 195, 40)
WHITE       = (255, 255, 255)
GREY        = (160, 170, 200)
RESULT_WIN  = (60,  200, 100)
RESULT_DRAW = (220, 180,  40)
RESULT_LOSS = (220,  70,  70)

# ── Dimensions ───────────────────────────────────────────────────────────────
W           = 1080
ROW_H       = 54
PADDING     = 32
HEADER_H    = 120
FOOTER_H    = 48


def _font(size: int, bold: bool = False):
    """Return a PIL font – falls back to default if no TTF is found."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _result_color(result: str | None, is_home: bool):
    if not result:
        return GREY
    try:
        parts = result.split("-")
        home_g, away_g = int(parts[0]), int(parts[1])
        our_g  = home_g if is_home else away_g
        opp_g  = away_g if is_home else home_g
        if our_g > opp_g: return RESULT_WIN
        if our_g == opp_g: return RESULT_DRAW
        return RESULT_LOSS
    except Exception:
        return GREY


def generate_schedule_png() -> bytes:
    fixtures = db.list_fixtures()
    n_rows   = max(len(fixtures), 1)
    H        = HEADER_H + n_rows * ROW_H + FOOTER_H + PADDING

    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── Subtle diagonal stripe texture ──────────────────────────────────────
    for i in range(0, W + H, 18):
        draw.line([(i, 0), (0, i)], fill=(255, 255, 255, 5), width=1)

    # ── Header ───────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, HEADER_H], fill=HEADER_BG)
    # accent bar
    draw.rectangle([0, HEADER_H - 4, W, HEADER_H], fill=ACCENT)
    # club name
    f_title = _font(42, bold=True)
    draw.text((PADDING, 18), "FC IRONCLAD", font=f_title, fill=WHITE)
    # subtitle
    f_sub = _font(18)
    draw.text((PADDING, 70), "OFFICIAL MATCH SCHEDULE  •  SEASON 2025/26", font=f_sub, fill=GOLD)
    # generated date (top-right)
    f_small = _font(14)
    now_str = datetime.datetime.now().strftime("Generated %d %b %Y")
    draw.text((W - 200, 20), now_str, font=f_small, fill=GREY)

    # ── Column headers ───────────────────────────────────────────────────────
    f_col = _font(14, bold=True)
    col_y = HEADER_H + 6
    draw.text((PADDING,        col_y), "DATE",        font=f_col, fill=GOLD)
    draw.text((PADDING + 130,  col_y), "KICK-OFF",    font=f_col, fill=GOLD)
    draw.text((PADDING + 230,  col_y), "HOME",        font=f_col, fill=GOLD)
    draw.text((PADDING + 460,  col_y), "AWAY",        font=f_col, fill=GOLD)
    draw.text((PADDING + 690,  col_y), "VENUE",       font=f_col, fill=GOLD)
    draw.text((PADDING + 880,  col_y), "RESULT",      font=f_col, fill=GOLD)

    # ── Row separator after column headers ───────────────────────────────────
    sep_y = HEADER_H + ROW_H - 2
    draw.rectangle([0, sep_y, W, sep_y + 2], fill=ACCENT)

    # ── Fixture rows ─────────────────────────────────────────────────────────
    f_body = _font(16)
    for idx, fx in enumerate(fixtures):
        y0  = HEADER_H + ROW_H + idx * ROW_H
        y1  = y0 + ROW_H
        row_color = ROW_ODD if idx % 2 == 0 else ROW_EVEN
        draw.rectangle([0, y0, W, y1], fill=row_color)

        cy   = y0 + ROW_H // 2 - 8        # vertical centre

        # parse date
        try:
            dt = datetime.datetime.strptime(fx["match_date"], "%Y-%m-%d")
            date_str = dt.strftime("%d %b %Y")
        except Exception:
            date_str = str(fx["match_date"])

        # kick-off
        ko = str(fx["kick_off"])[:5]

        is_home = fx["home_team"].upper().startswith("FC IRONCLAD")
        res_col = _result_color(fx.get("result"), is_home)

        draw.text((PADDING,        cy), date_str,           font=f_body, fill=WHITE)
        draw.text((PADDING + 130,  cy), ko,                 font=f_body, fill=GREY)
        draw.text((PADDING + 230,  cy), fx["home_team"][:22],font=f_body, fill=WHITE)
        draw.text((PADDING + 460,  cy), fx["away_team"][:22],font=f_body, fill=WHITE)
        draw.text((PADDING + 690,  cy), fx["venue"][:22],   font=f_body, fill=GREY)

        result_txt = fx.get("result") or "TBD"
        draw.text((PADDING + 880,  cy), result_txt,         font=f_body, fill=res_col)

        # left accent stripe for FC Ironclad home games
        if is_home:
            draw.rectangle([0, y0, 4, y1], fill=ACCENT)

    # ── Footer ───────────────────────────────────────────────────────────────
    fy = HEADER_H + ROW_H + n_rows * ROW_H
    draw.rectangle([0, fy, W, H], fill=HEADER_BG)
    draw.rectangle([0, fy, W, fy + 2], fill=ACCENT)
    draw.text((PADDING, fy + 14), "fcironclad.com  •  All times local",
              font=f_small, fill=GREY)
    draw.text((W - 300, fy + 14), "Red = away  |  Win / Draw / Loss colours",
              font=f_small, fill=GREY)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
