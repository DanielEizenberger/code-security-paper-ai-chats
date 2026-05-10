"""
Generate a polished match-schedule PNG for FC Irongate.
Uses only Pillow (no network needed).
"""

import os
from PIL import Image, ImageDraw, ImageFont

MATCHES = [
    ("Aug 10", "FC Irongate",      "vs", "Riverside FC",     "Home", "15:00"),
    ("Aug 17", "Northgate United", "vs", "FC Irongate",      "Away", "14:00"),
    ("Aug 24", "FC Irongate",      "vs", "Valley Athletic",  "Home", "15:00"),
    ("Sep 07", "Eastbridge City",  "vs", "FC Irongate",      "Away", "16:00"),
    ("Sep 14", "FC Irongate",      "vs", "Portside Rovers",  "Home", "15:00"),
    ("Sep 21", "FC Irongate",      "vs", "Millbrook Town",   "Home", "14:00"),
    ("Oct 05", "Southbank SC",     "vs", "FC Irongate",      "Away", "15:00"),
    ("Oct 19", "FC Irongate",      "vs", "Harrow City",      "Home", "15:00"),
    ("Nov 02", "FC Irongate",      "vs", "Crestwood FC",     "Home", "14:00"),
    ("Nov 16", "Lakeside Rangers", "vs", "FC Irongate",      "Away", "15:00"),
]

# Colour palette
C_BG        = (10,  18,  40)   # deep navy
C_CARD      = (18,  30,  62)   # slightly lighter navy
C_ACCENT    = (220, 40,  40)   # iron-red
C_ACCENT2   = (255, 200, 0)    # gold
C_WHITE     = (255, 255, 255)
C_MUTED     = (140, 155, 190)
C_HOME      = (30,  180, 100)
C_AWAY      = (220, 80,  80)
C_STRIPE    = (22,  36,  72)


def _font(size, bold=False):
    """Load a system font, fall back to default."""
    candidates_bold   = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                         "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
                         "/Library/Fonts/Arial Bold.ttf"]
    candidates_regular= ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                         "/usr/share/fonts/TTF/DejaVuSans.ttf",
                         "/Library/Fonts/Arial.ttf"]
    paths = candidates_bold if bold else candidates_regular
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def generate_schedule_image(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    W, ROW_H = 900, 62
    HEADER_H  = 160
    FOOTER_H  = 60
    H = HEADER_H + len(MATCHES) * ROW_H + FOOTER_H

    img  = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)

    # ── Background subtle diagonal stripes ──────────────────────────────────
    for x in range(-H, W, 28):
        draw.line([(x, 0), (x + H, H)], fill=C_STRIPE, width=1)

    # ── Header bar ───────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, HEADER_H], fill=C_ACCENT)
    # Shield outline
    shield_cx, shield_cy = 68, HEADER_H // 2
    sw, sh = 52, 64
    sx, sy = shield_cx - sw // 2, shield_cy - sh // 2
    pts = [
        (sx, sy),
        (sx + sw, sy),
        (sx + sw, sy + sh - 18),
        (shield_cx, sy + sh),
        (sx, sy + sh - 18),
    ]
    draw.polygon(pts, fill=C_BG)
    draw.polygon(pts, outline=C_ACCENT2, width=3)
    draw.text((shield_cx, shield_cy - 5), "FC", font=_font(17, bold=True),
              fill=C_ACCENT2, anchor="mm")
    draw.text((shield_cx, shield_cy + 14), "IG", font=_font(13, bold=True),
              fill=C_WHITE, anchor="mm")

    draw.text((122, 42), "FC IRONGATE", font=_font(40, bold=True),
              fill=C_WHITE, anchor="lm")
    draw.text((122, 78), "2025 / 2026 · MATCH SCHEDULE", font=_font(16),
              fill=C_ACCENT2, anchor="lm")
    draw.text((122, 106), "Irongate Stadium · Founded 1923",
              font=_font(13), fill=(255, 220, 220), anchor="lm")

    # Red accent stripe below header
    draw.rectangle([0, HEADER_H - 6, W, HEADER_H], fill=C_ACCENT2)

    # ── Column headers ───────────────────────────────────────────────────────
    COLS = {
        "DATE":    (26,  80),
        "HOME":    (130, 160),
        "VS":      (300, 20),
        "AWAY":    (330, 160),
        "VENUE":   (590, 68),
        "KO TIME": (720, 80),
    }
    yh = HEADER_H + 10
    fh = _font(11, bold=True)
    for label, (xpos, width) in COLS.items():
        draw.text((xpos, yh), label, font=fh, fill=C_MUTED)

    # ── Match rows ────────────────────────────────────────────────────────────
    f_date  = _font(13, bold=True)
    f_team  = _font(14, bold=True)
    f_vs    = _font(12)
    f_venue = _font(13)
    f_time  = _font(14, bold=True)

    for i, (date, home, vs, away, venue, kickoff) in enumerate(MATCHES):
        y0 = HEADER_H + ROW_H * i + 26
        row_bg = C_CARD if i % 2 == 0 else C_BG
        draw.rectangle([0, HEADER_H + ROW_H * i,
                        W, HEADER_H + ROW_H * (i + 1)], fill=row_bg)

        # Left red accent bar
        draw.rectangle([0, HEADER_H + ROW_H * i + 4,
                        4, HEADER_H + ROW_H * (i + 1) - 4], fill=C_ACCENT)

        is_home = home == "FC Irongate"

        draw.text((26,  y0), date,    font=f_date,  fill=C_ACCENT2)
        draw.text((130, y0), home,    font=f_team,
                  fill=C_WHITE if is_home else C_MUTED)
        draw.text((320, y0), "vs",    font=f_vs,    fill=C_MUTED)
        draw.text((350, y0), away,    font=f_team,
                  fill=C_WHITE if not is_home else C_MUTED)

        # Venue badge
        v_color = C_HOME if venue == "Home" else C_AWAY
        vx = 590
        badge_w = 52
        draw.rounded_rectangle([vx, y0 - 4, vx + badge_w, y0 + 18],
                                radius=4, fill=v_color)
        draw.text((vx + badge_w // 2, y0 + 7), venue,
                  font=_font(11, bold=True), fill=C_WHITE, anchor="mm")

        draw.text((720, y0), kickoff, font=f_time,  fill=C_WHITE)

        # Separator line
        draw.line([14, HEADER_H + ROW_H * (i + 1) - 1,
                   W - 14, HEADER_H + ROW_H * (i + 1) - 1],
                  fill=C_STRIPE, width=1)

    # ── Footer ────────────────────────────────────────────────────────────────
    fy = HEADER_H + len(MATCHES) * ROW_H
    draw.rectangle([0, fy, W, H], fill=C_ACCENT)
    draw.text((W // 2, fy + 30),
              "fcirongate.com  ·  All times local  ·  Subject to change",
              font=_font(12), fill=(255, 220, 220), anchor="mm")

    img.save(output_path, format="PNG", optimize=True)
    print(f"[schedule_gen] Saved to {output_path}")
