#!/usr/bin/env python3
"""Build entry.png for news-image-20261122 v2 (Sunday 22 November 2026).

A single-sheet 1024x1024 front page drawn entirely with PIL primitives.
Every panel, icon and the world map is drawn by this script in this
session; no image is placed, downloaded or copied from anywhere.
"""
import hashlib
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SANS = "DejaVuSans.ttf"
SANSB = "DejaVuSans-Bold.ttf"
SERIFB = "DejaVuSerif-Bold.ttf"
MONOB = "DejaVuSansMono-Bold.ttf"

W = H = 1024
MX = 10                      # side margin
CW = W - 2 * MX              # content width

PAPER = (247, 243, 233)
INK = (22, 22, 22)
NAVY = (23, 33, 52)
NAVY2 = (38, 53, 80)
GOLD = (216, 178, 60)
RED = (176, 32, 32)
REDD = (138, 24, 24)
GREEN = (28, 102, 50)
AMBER = (176, 84, 8)
BLUE = (35, 92, 200)
GREY = (112, 110, 102)
LINE = (178, 172, 156)
WHITE = (255, 255, 255)
CREAM = (255, 252, 244)
BLACK = (16, 16, 16)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def tag_chip(d, x, y, label, fill, size=9):
    """Small certainty tag; returns its width."""
    f = font(SANSB, size)
    w = int(d.textlength(label, font=f)) + 10
    h = size + 5
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill)
    d.text((x + 5, y + 2), label, font=f, fill=WHITE)
    return w


def pin_chip(d, x, y, num, r=7):
    """Red numbered circle used to key a story to the world map."""
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=RED, outline=WHITE, width=1)
    f = font(SANSB, 9)
    t = str(num)
    tw = d.textlength(t, font=f)
    d.text((x + r - tw / 2, y + r - 5), t, font=f, fill=WHITE)
    return 2 * r


def hline(d, x0, x1, y, fill=INK, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def section_head(d, x, y, text, size=12):
    """Bold section header with a rule underneath; returns height used."""
    f = font(SANSB, size)
    d.text((x, y), text, font=f, fill=NAVY)
    hline(d, x, x + CW, y + size + 4, fill=NAVY, width=2)
    return size + 7


# --------------------------------------------------------------------------
# Pictorial panels (all PIL primitives)
# --------------------------------------------------------------------------

def panel_cop31(x0, y0, w, h):
    """Gavel over a cracked summit table, with a NO DEAL stamp."""
    img = Image.new("RGB", (w, h), (18, 52, 44))
    d = ImageDraw.Draw(img)
    # hall glow
    d.ellipse([w // 2 - 90, -70, w // 2 + 90, 70], fill=(30, 80, 66))
    # floor line
    d.rectangle([0, h - 26, w, h], fill=(12, 36, 30))
    # summit table: two halves with a crack between them
    ty = h - 62
    d.rectangle([14, ty, w // 2 - 8, ty + 16], fill=(150, 108, 62))
    d.rectangle([w // 2 + 8, ty, w - 14, ty + 16], fill=(150, 108, 62))
    d.rectangle([20, ty + 16, 28, h - 26], fill=(110, 76, 42))
    d.rectangle([w - 28, ty + 16, w - 20, h - 26], fill=(110, 76, 42))
    crack = [(w // 2 - 8, ty), (w // 2 - 2, ty + 6), (w // 2 - 7, ty + 11),
             (w // 2 + 2, ty + 16)]
    d.line(crack, fill=(255, 220, 120), width=2)
    # empty chairs
    for cx in (44, w - 70):
        d.rectangle([cx, ty - 26, cx + 22, ty - 4], outline=(220, 210, 180),
                    width=3)
        d.line([(cx + 4, ty - 4), (cx + 4, ty + 2)], fill=(220, 210, 180),
               width=3)
        d.line([(cx + 18, ty - 4), (cx + 18, ty + 2)], fill=(220, 210, 180),
               width=3)
    # gavel, drawn on a temp layer then rotated
    g = Image.new("RGBA", (96, 72), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    gd.rounded_rectangle([14, 6, 82, 28], radius=6, fill=(190, 140, 80))
    gd.rectangle([45, 24, 53, 66], fill=(160, 112, 60))
    gd.ellipse([40, 63, 58, 71], fill=(190, 140, 80))
    g = g.rotate(25, expand=True, resample=Image.BICUBIC)
    img.paste(g, (w // 2 - g.width // 2 - 30, 2), g)
    # NO DEAL stamp
    s = Image.new("RGBA", (126, 36), (0, 0, 0, 0))
    sd = ImageDraw.Draw(s)
    sd.rectangle([2, 2, 123, 33], outline=(235, 70, 60), width=3)
    sd.text((12, 7), "NO DEAL", font=font(SANSB, 18), fill=(235, 70, 60))
    s = s.rotate(-11, expand=True, resample=Image.BICUBIC)
    img.paste(s, (w - s.width - 6, h - s.height - 2), s)
    return img


def panel_drones(x0, y0, w, h):
    """Night sky, drone silhouettes, a damaged apartment block."""
    img = Image.new("RGB", (w, h), (13, 27, 46))
    d = ImageDraw.Draw(img)
    rnd = random.Random(22)
    for _ in range(26):
        sx, sy = rnd.randint(4, w - 4), rnd.randint(2, h // 2)
        d.ellipse([sx, sy, sx + 1, sy + 1], fill=(220, 225, 235))
    # moon (kept left of the top-right corner, where the tag chip sits)
    d.ellipse([w - 108, 4, w - 82, 30], fill=(235, 225, 170))
    d.ellipse([w - 102, 2, w - 78, 28], fill=(13, 27, 46))
    # searchlight beam
    d.polygon([(26, h), (70, h), (150, 6), (120, 6)], fill=(52, 84, 122))
    # apartment block, left half intact, right half broken
    bx, by, bw, bh = 8, h - 52, 150, 52
    d.rectangle([bx, by, bx + bw, by + bh], fill=(88, 100, 118))
    for r in range(3):
        for c in range(6):
            wx, wy = bx + 8 + c * 22, by + 8 + r * 14
            lit = (r + c) % 3 == 0
            d.rectangle([wx, wy, wx + 12, wy + 8],
                        fill=(255, 205, 90) if lit else (40, 48, 62))
    # broken section: jagged top + scorch + fire glow
    jag = [(bx + 92, by), (bx + 104, by - 8), (bx + 116, by - 2),
           (bx + 128, by - 10), (bx + 140, by - 3), (bx + bw, by - 6),
           (bx + bw, by + 20), (bx + 92, by + 20)]
    d.polygon(jag, fill=(30, 30, 34))
    d.ellipse([bx + 96, by - 2, bx + 146, by + 22], fill=(255, 120, 30))
    d.ellipse([bx + 108, by + 2, bx + 134, by + 18], fill=(255, 200, 60))
    # drones
    def drone(cx, cy, s):
        d.ellipse([cx - 3 * s, cy - 2 * s, cx + 3 * s, cy + 2 * s],
                  fill=(200, 205, 215))
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            d.line([(cx, cy), (cx + dx * 9 * s, cy + dy * 6 * s)],
                   fill=(200, 205, 215), width=2)
            d.ellipse([cx + dx * 9 * s - 2, cy + dy * 6 * s - 1,
                       cx + dx * 9 * s + 2, cy + dy * 6 * s + 1],
                      fill=(255, 90, 70))
    drone(200, 16, 1.0)
    drone(252, 34, 0.8)
    drone(168, 40, 0.7)
    return img


def panel_radar(x0, y0, w, h):
    """Radar dish with sweep, range rings and blips."""
    img = Image.new("RGB", (w, h), (12, 32, 20))
    d = ImageDraw.Draw(img)
    cx, cy = w // 2 - 30, h - 6
    for r in (30, 55, 80):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(46, 120, 70),
                  width=2)
    # sweep wedge
    d.polygon([(cx, cy), (cx + 78, cy - 12), (cx + 62, cy - 58)],
              fill=(64, 170, 95))
    # dish
    d.arc([cx - 34, cy - 66, cx + 34, cy + 2], start=200, end=340,
          fill=(210, 220, 210), width=5)
    d.line([(cx, cy - 34), (cx, cy)], fill=(210, 220, 210), width=4)
    d.line([(cx - 18, cy), (cx + 18, cy)], fill=(210, 220, 210), width=4)
    # blips
    for bx, by in ((cx + 40, cy - 44), (cx + 66, cy - 26), (cx - 44, cy - 40),
                   (cx - 20, cy - 66)):
        d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(140, 255, 170))
    # incoming track: dotted arc, right side below the tag chip
    for i in range(9):
        t = i / 8.0
        px = w - 14 - int(70 * t)
        py = 22 + int(22 * t * t) + int(12 * t)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 120, 90))
    return img


def panel_ballot(x0, y0, w, h):
    """Ballot box with a paper going in; big turnout figure."""
    img = Image.new("RGB", (w, h), (143, 29, 34))
    d = ImageDraw.Draw(img)
    d.text((10, 4), "98.79%", font=font(SANSB, 24), fill=WHITE)
    d.text((10, 30), "TURNOUT — RECORD", font=font(SANSB, 9), fill=(255, 210, 210))
    # ballot box
    bx, by = w - 118, h - 46
    d.rectangle([bx, by, bx + 96, by + 38], fill=(23, 33, 52))
    d.rectangle([bx - 4, by - 6, bx + 100, by + 2], fill=(38, 53, 80))
    d.rectangle([bx + 30, by - 5, bx + 66, by - 1], fill=(10, 10, 10))
    # paper sliding in
    p = Image.new("RGBA", (46, 60), (0, 0, 0, 0))
    pd = ImageDraw.Draw(p)
    pd.rectangle([4, 4, 42, 56], fill=(255, 252, 244))
    pd.line([(12, 34), (20, 44), (34, 20)], fill=(28, 102, 50), width=5)
    p = p.rotate(-14, expand=True, resample=Image.BICUBIC)
    img.paste(p, (bx + 26, by - 44), p)
    # tick on the box
    d.line([(bx + 12, by + 22), (bx + 24, by + 32), (bx + 40, by + 10)],
           fill=(120, 220, 140), width=5)
    return img


# --------------------------------------------------------------------------
# Medium icons (small flat glyphs, 50x33)
# --------------------------------------------------------------------------

def icon_base(bg):
    img = Image.new("RGB", (50, 33), bg)
    return img, ImageDraw.Draw(img)


def icon_cricket():
    img, d = icon_base((24, 92, 48))
    b = Image.new("RGBA", (40, 30), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    bd.rounded_rectangle([14, 2, 24, 22], radius=3, fill=(232, 220, 190))
    bd.rectangle([17, 20, 21, 29], fill=(150, 110, 60))
    b = b.rotate(28, expand=True, resample=Image.BICUBIC)
    img.paste(b, (6, 0), b)
    d.ellipse([34, 18, 44, 28], fill=(200, 40, 40))
    return img


def icon_football():
    img, d = icon_base((24, 92, 48))
    d.ellipse([12, 3, 38, 29], fill=(250, 250, 250))
    d.polygon([(25, 11), (30, 15), (28, 21), (22, 21), (20, 15)],
              fill=(20, 20, 20))
    for px, py in ((16, 8), (32, 9), (15, 20), (33, 21), (25, 26)):
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(20, 20, 20))
    return img


def icon_tennis():
    img, d = icon_base((30, 70, 140))
    d.ellipse([6, 2, 28, 22], outline=(240, 230, 90), width=3)
    d.line([(7, 12), (27, 12)], fill=(240, 230, 90), width=1)
    d.line([(17, 3), (17, 21)], fill=(240, 230, 90), width=1)
    d.line([(24, 20), (34, 30)], fill=(200, 160, 110), width=4)
    d.ellipse([36, 20, 46, 30], fill=(230, 220, 60))
    return img


def icon_f1():
    img, d = icon_base((30, 30, 36))
    d.polygon([(4, 22), (10, 14), (24, 12), (34, 14), (44, 18), (46, 22)],
              fill=(220, 30, 30))
    d.rectangle([28, 8, 36, 14], fill=(220, 30, 30))
    d.ellipse([10, 19, 20, 29], fill=(10, 10, 10))
    d.ellipse([32, 19, 42, 29], fill=(10, 10, 10))
    d.ellipse([13, 22, 17, 26], fill=(180, 180, 180))
    d.ellipse([35, 22, 39, 26], fill=(180, 180, 180))
    return img


def icon_basketball():
    img, d = icon_base((180, 84, 20))
    d.ellipse([12, 3, 38, 29], fill=(240, 120, 40))
    d.line([(12, 16), (38, 16)], fill=(90, 40, 10), width=2)
    d.line([(25, 3), (25, 29)], fill=(90, 40, 10), width=2)
    d.arc([16, -6, 44, 22], start=300, end=60, fill=(90, 40, 10), width=2)
    d.arc([6, 10, 34, 38], start=120, end=240, fill=(90, 40, 10), width=2)
    return img


def icon_drone():
    img, d = icon_base((13, 27, 46))
    d.ellipse([20, 13, 30, 19], fill=(210, 215, 225))
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        d.line([(25, 16), (25 + dx * 12, 16 + dy * 8)],
               fill=(210, 215, 225), width=2)
        d.ellipse([25 + dx * 12 - 2, 16 + dy * 8 - 1,
                   25 + dx * 12 + 2, 16 + dy * 8 + 1], fill=(255, 90, 70))
    d.ellipse([38, 4, 46, 12], fill=(255, 150, 40))
    return img


def icon_intercept():
    img, d = icon_base((40, 20, 60))
    # shield
    d.polygon([(14, 5), (34, 5), (34, 16), (24, 29), (14, 16)],
              fill=(70, 140, 220))
    d.line([(19, 15), (23, 20), (30, 10)], fill=(255, 255, 255), width=3)
    # incoming missile, bursting
    d.line([(46, 4), (38, 12)], fill=(255, 150, 60), width=3)
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.line([(38, 12), (38 + int(7 * math.cos(r)), 12 + int(7 * math.sin(r)))],
               fill=(255, 200, 80), width=2)
    return img


def icon_fire():
    img, d = icon_base((40, 16, 10))
    d.polygon([(25, 2), (34, 12), (38, 20), (34, 30), (16, 30), (12, 20),
               (16, 12)], fill=(255, 120, 20))
    d.polygon([(25, 12), (30, 18), (31, 24), (27, 29), (20, 29), (18, 23),
               (21, 17)], fill=(255, 210, 60))
    return img


ICONS = {
    "cricket": icon_cricket,
    "football": icon_football,
    "tennis": icon_tennis,
    "f1": icon_f1,
    "basketball": icon_basketball,
    "drone": icon_drone,
    "intercept": icon_intercept,
    "fire": icon_fire,
}


# --------------------------------------------------------------------------
# Sheet assembly
# --------------------------------------------------------------------------

def draw_masthead(d, y):
    """Navy masthead bar: date, edition, press time, story count."""
    d.rectangle([MX, y, MX + CW, y + 56], fill=NAVY)
    d.rectangle([MX, y + 56, MX + CW, y + 59], fill=GOLD)
    f_date = font(SERIFB, 34)
    date = "SUNDAY 22 NOVEMBER 2026"
    tw = d.textlength(date, font=f_date)
    d.text((MX + (CW - tw) / 2, y + 9), date, font=f_date, fill=WHITE)
    f_small = font(SANSB, 12)
    d.text((MX + 12, y + 10), "EVENING EDITION", font=f_small, fill=GOLD)
    d.text((MX + 12, y + 30), "38 STORIES", font=f_small, fill=WHITE)
    rt = "PRESS TIME 23:45 UTC"
    d.text((MX + CW - 12 - d.textlength(rt, font=f_small), y + 10), rt,
           font=f_small, fill=GOLD)
    rt2 = "ALL SUNDAY"
    d.text((MX + CW - 12 - d.textlength(rt2, font=f_small), y + 30), rt2,
           font=f_small, fill=WHITE)
    return 62


def draw_subhead(d, y):
    f = font(SANSB, 15)
    txt = ("COP31 COLLAPSES  \u2022  186 DRONES OVERNIGHT  \u2022  "
           "IRAN\u2013BAHRAIN CLAIM VS DENIAL  \u2022  38 STORIES, ALL SUNDAY")
    tw = d.textlength(txt, font=f)
    d.text((MX + (CW - tw) / 2, y + 3), txt, font=f, fill=REDD)
    hline(d, MX, MX + CW, y + 23, fill=LINE, width=1)
    return 25


def draw_stats(d, y):
    """Black stats strip; every figure labelled with its day."""
    d.rectangle([MX, y, MX + CW, y + 27], fill=BLACK)
    f = font(MONOB, 11)
    segs = [
        ("GOLD", "$3,584 +1.4% Sun"),
        ("BTC", "$61,271 +1.8% Sun"),
        ("BRENT", "$92.57 Fri settle"),
        ("COP31", "NO DEAL"),
        ("DRONES", "186 (161 downed)"),
        ("HK TURNOUT", "98.79%"),
    ]
    sep = "  \u00b7  "
    parts = []
    total = 0
    for lab, val in segs:
        parts.append((lab, val))
        total += d.textlength(lab + " " + val, font=f)
    total += d.textlength(sep, font=f) * (len(segs) - 1)
    x = MX + (CW - total) / 2
    yy = y + 7
    for i, (lab, val) in enumerate(parts):
        if i:
            d.text((x, yy), sep, font=f, fill=(140, 140, 140))
            x += d.textlength(sep, font=f)
        d.text((x, yy), lab, font=f, fill=GOLD)
        x += d.textlength(lab, font=f)
        d.text((x, yy), " " + val, font=f, fill=WHITE)
        x += d.textlength(" " + val, font=f)
    return 29


def draw_regions(d, y):
    f = font(SANSB, 11)
    txt = ("EUROPE   \u2022   MIDDLE EAST   \u2022   ASIA   \u2022   AMERICAS"
           "   \u2022   AFRICA   \u2022   OCEANIA   \u2022   SPORT")
    tw = d.textlength(txt, font=f)
    d.text((MX + (CW - tw) / 2, y + 2), txt, font=f, fill=NAVY2)
    hline(d, MX, MX + CW, y + 19, fill=NAVY, width=2)
    return 21


def draw_lead1(sheet, d, y):
    """Full-width lead: COP31 COLLAPSES."""
    h = 148
    d.rectangle([MX, y, MX + CW, y + h], fill=CREAM, outline=INK, width=2)
    pin_chip(d, MX + 10, y + 9, 1)
    f_head = font(SERIFB, 30)
    d.text((MX + 30, y + 5), "COP31 COLLAPSES", font=f_head, fill=INK)
    tag_chip(d, MX + CW - 96, y + 12, "CONFIRMED", GREEN, size=10)
    hline(d, MX + 8, MX + CW - 8, y + 42, fill=LINE, width=1)
    body = (
        "The final text was rejected on Sunday afternoon in Antalya \u2014 "
        "no consensus after 49+ hours overtime. The longest COP ever, and "
        "the first failure since Copenhagen 2009. The EU and island states "
        "refused a text silent on fossil fuels. Bowen: \u201cVery "
        "disappointing.\u201d Kurum gavelled the close: \u201cThere will be "
        "no new text from now on.\u201d 190+ countries; 92,000+ registered "
        "\u2014 the largest COP on record."
    )
    f_body = font(SANS, 12)
    lines = wrap(d, body, f_body, 636)
    yy = y + 50
    for ln in lines:
        d.text((MX + 12, yy), ln, font=f_body, fill=INK)
        yy += 15
    art = panel_cop31(0, 0, 330, 96)
    sheet.paste(art, (MX + CW - 342, y + 46))
    d.rectangle([MX + CW - 342, y + 46, MX + CW - 12, y + 142],
                outline=INK, width=1)
    return h + 2


def draw_leads_row(sheet, d, y):
    """Three pictorial leads side by side."""
    h = 150
    col_w = 330
    gap = 7
    leads = [
        {
            "pin": 2, "art": panel_drones, "tag": ("CONFIRMED", GREEN),
            "head": "186 DRONES OVERNIGHT", "hsize": 19,
            "body": ("186 launched, 161 downed. Dymer: at least 5 dead by "
                     "late Sunday, 11 unaccounted; a boy aged 7 was pulled "
                     "alive after 14 hours. Vyshneve supermarket: 3 killed, "
                     "13 wounded. 70+ strikes across 10 regions."),
        },
        {
            "pin": 3, "art": panel_radar, "tag": ("CLAIM", AMBER),
            "head": "IRAN\u2013BAHRAIN: CLAIM VS DENIAL", "hsize": 16,
            "body": ("IRGC claims two US Patriot radars hit at al-Riffa and "
                     "Awali (attack Sat night). Bahrain: civilian site at "
                     "Sitra hit, 2 injured. US official: no damage to US "
                     "personnel or facilities. IRGC named inconsistent "
                     "targets; F-16 claim denied by CENTCOM."),
        },
        {
            "pin": 4, "art": panel_ballot, "tag": ("CONFIRMED", GREEN),
            "head": "HONG KONG VOTES", "hsize": 19,
            "body": ("Record 98.79% turnout; 723 seats, 856 candidates; "
                     "5,640 voters. Polls closed 18:00, count done 22:15. "
                     "New term from 1 Feb 2027."),
        },
    ]
    for i, lead in enumerate(leads):
        x0 = MX + i * (col_w + gap)
        d.rectangle([x0, y, x0 + col_w, y + h], fill=CREAM, outline=INK,
                    width=2)
        art = lead["art"](0, 0, col_w - 4, 52)
        sheet.paste(art, (x0 + 2, y + 2))
        # tag chip rides on the dark illustration, top right, so the
        # headline below it keeps its full width
        f_chip = font(SANSB, 8)
        cw = int(d.textlength(lead["tag"][0], font=f_chip)) + 10
        tag_chip(d, x0 + col_w - cw - 8, y + 7, lead["tag"][0],
                 lead["tag"][1], size=8)
        pin_chip(d, x0 + 8, y + 62, lead["pin"], r=6)
        f_head = font(SANSB, lead["hsize"])
        d.text((x0 + 26, y + 60), lead["head"], font=f_head, fill=INK)
        f_body = font(SANS, 10)
        lines = wrap(d, lead["body"], f_body, col_w - 16)
        yy = y + 84
        for ln in lines[:5]:
            d.text((x0 + 8, yy), ln, font=f_body, fill=INK)
            yy += 12
    return h + 2


def draw_timeline(d, y):
    """UTC timeline strip, Sunday 22 November only."""
    h = 52
    d.rectangle([MX, y, MX + CW, y + h], fill=(238, 234, 220),
                outline=LINE, width=1)
    f_h = font(SANSB, 11)
    d.text((MX + 8, y + 3), "SUNDAY 22 NOVEMBER \u2014 IN UTC", font=f_h,
           fill=NAVY)
    hline(d, MX + 8, MX + CW - 8, y + 18, fill=LINE, width=1)
    entries = [
        ("00:00\u201302:30", "Khartoum drone strikes"),
        ("02:30", "Seoul minister resigns"),
        ("05:30", "Verstappen wins Las Vegas GP"),
        ("05:40", "Wembanyama scores 50"),
        ("07:54", "M5.3 quake off Balut Island"),
        ("11:30", "Pope\u2019s lunch for 1,300"),
        ("AFTERNOON", "COP31 collapses"),
        ("18:00", "HK polls close; Fukushima freed"),
        ("18:25", "Liverpool 4\u20130 Man Utd (FT)"),
        ("22:15", "HK count done: 98.79% turnout"),
    ]
    f_t = font(SANSB, 9)
    f_x = font(SANS, 9)
    cell = (CW - 16) / 5
    for i, (tm, tx) in enumerate(entries):
        cx = MX + 8 + (i % 5) * cell
        cy = y + 21 + (i // 5) * 15
        d.text((cx, cy), tm, font=f_t, fill=REDD)
        tw = d.textlength(tm, font=f_t)
        # time and text on one line when it fits, else text below the time
        if tw + 5 + d.textlength(tx, font=f_x) <= cell - 4:
            d.text((cx + tw + 5, cy), tx, font=f_x, fill=INK)
        else:
            d.text((cx, cy + 8), tx, font=f_x, fill=INK)
    return h + 2


MEDIUMS = [
    {"pin": 5, "icon": "cricket", "head": "INDIA DECLARE 720/9",
     "body": "Pant 128; stumps NZ 119/2, trail by 233. Day 4, Wellington."},
    {"pin": 6, "icon": "football", "head": "LIVERPOOL 4\u20130 MAN UTD",
     "body": "Pochettino debut; Yoro sent off 8\u2032. Szoboszlai 10\u2032, "
             "Wirtz 13\u2032."},
    {"pin": 7, "icon": "tennis", "head": "ALCARAZ WINS ATP FINALS",
     "body": "Beat Zverev 6\u20132, 7\u20136(7) in Turin \u2014 first ATP "
             "Finals title."},
    {"pin": 8, "icon": "f1", "head": "VERSTAPPEN WINS LAS VEGAS GP",
     "body": "By 0.639s over Norris; 75th career win."},
    {"pin": None, "icon": "basketball", "head": "WEMBANYAMA SCORES 50",
     "body": "Spurs 114\u201391 Pelicans; 19 rebounds, 5 blocks."},
    {"pin": 9, "icon": "drone", "head": "KHARTOUM DRONE STRIKES",
     "body": "4 killed; UN building hit. Ethiopia launch claim REPORTED, "
             "unverified."},
    {"pin": 10, "icon": "intercept", "head": "SAUDI INTERCEPTS DRONE & MISSILE",
     "body": "Coalition downs Houthi drone toward Riyadh, missile west."},
    {"pin": 11, "icon": "fire", "head": "CIKANDE FACTORY FIRE",
     "body": "3 dead, 34 missing; 24 body bags recovered by Sunday evening."},
]


def draw_mediums(sheet, d, y):
    """Eight medium stories, two columns, each with a small icon."""
    y += section_head(d, MX, y, "SPORT & WORLD \u2014 SUNDAY\u2019S OTHER STORIES")
    row_h = 37
    col_w = (CW - 8) // 2
    f_head = font(SANSB, 11)
    f_body = font(SANS, 9)
    for i, m in enumerate(MEDIUMS):
        x0 = MX + (i % 2) * (col_w + 8)
        yy = y + (i // 2) * row_h
        d.rectangle([x0, yy, x0 + col_w, yy + row_h - 3], fill=CREAM,
                    outline=LINE, width=1)
        sheet.paste(ICONS[m["icon"]](), (x0 + 2, yy + 2))
        tx = x0 + 56
        if m["pin"] is not None:
            pin_chip(d, tx, yy + 3, m["pin"], r=6)
            tx += 15
        d.text((tx, yy + 2), m["head"], font=f_head, fill=INK)
        tag_chip(d, x0 + col_w - 72, yy + 3, "CONFIRMED", GREEN, size=8)
        lines = wrap(d, m["body"], f_body, col_w - 60)
        ly = yy + 16
        for ln in lines[:2]:
            d.text((x0 + 56, ly), ln, font=f_body, fill=INK)
            ly += 10
    return 12 + 7 + 4 * row_h + 2


# --------------------------------------------------------------------------
# World map (simplified continents, equirectangular)
# --------------------------------------------------------------------------

LAND = [
    # North America
    [(-168, 66), (-158, 71), (-140, 70), (-128, 70), (-120, 72), (-110, 68),
     (-95, 70), (-85, 68), (-80, 73), (-70, 62), (-60, 60), (-65, 52),
     (-55, 52), (-60, 46), (-70, 42), (-75, 35), (-80, 32), (-81, 25),
     (-90, 21), (-97, 26), (-105, 23), (-110, 24), (-115, 30), (-120, 34),
     (-125, 40), (-124, 48), (-130, 55), (-140, 60), (-155, 58), (-165, 60)],
    # Central America
    [(-92, 18), (-86, 16), (-83, 10), (-79, 9), (-81, 13), (-86, 15),
     (-90, 15)],
    # South America
    [(-79, 9), (-72, 12), (-62, 10), (-52, 5), (-44, 0), (-35, -8),
     (-38, -15), (-41, -23), (-48, -28), (-52, -33), (-58, -38), (-65, -45),
     (-68, -52), (-70, -54), (-73, -45), (-73, -37), (-71, -30), (-70, -20),
     (-75, -15), (-79, -8), (-81, 0), (-80, 5)],
    # Europe
    [(-9, 37), (-9, 43), (-2, 44), (-4, 48), (-1, 50), (2, 51), (5, 53),
     (8, 55), (10, 58), (12, 56), (18, 56), (21, 60), (18, 62), (24, 66),
     (28, 70), (32, 70), (30, 66), (28, 62), (32, 60), (36, 56), (40, 52),
     (38, 48), (34, 45), (30, 45), (26, 47), (22, 48), (20, 50), (16, 50),
     (12, 48), (10, 45), (8, 44), (12, 42), (16, 40), (15, 38), (12, 40),
     (8, 39), (3, 39), (0, 38), (-2, 37), (-6, 36)],
    # Anatolia
    [(26, 36), (30, 36), (34, 36), (38, 37), (42, 38), (44, 40), (40, 41),
     (36, 41), (32, 41), (28, 40)],
    # Africa
    [(-17, 15), (-16, 21), (-10, 28), (-6, 33), (0, 36), (10, 37), (11, 34),
     (20, 32), (30, 31), (32, 31), (35, 28), (34, 23), (37, 18), (40, 15),
     (43, 12), (48, 11), (51, 12), (48, 8), (42, 2), (40, -5), (39, -12),
     (36, -18), (33, -25), (32, -29), (28, -33), (20, -35), (17, -32),
     (15, -27), (13, -20), (12, -8), (9, -1), (9, 4), (4, 6), (-4, 5),
     (-8, 5), (-13, 8)],
    # Arabia
    [(43, 12), (48, 14), (52, 16), (55, 18), (58, 20), (60, 23), (57, 26),
     (52, 28), (48, 29), (45, 28), (42, 25), (40, 20), (42, 16)],
    # Asia (main)
    [(30, 42), (35, 45), (40, 48), (45, 50), (50, 52), (55, 55), (60, 58),
     (65, 60), (70, 62), (75, 65), (80, 68), (90, 70), (100, 72), (110, 73),
     (120, 74), (130, 73), (140, 72), (150, 71), (160, 70), (170, 68),
     (178, 66), (178, 62), (170, 60), (162, 60), (155, 58), (150, 55),
     (145, 52), (140, 50), (135, 45), (130, 42), (127, 40), (124, 34),
     (120, 28), (117, 24), (112, 22), (108, 22), (105, 24), (102, 20),
     (100, 25), (95, 28), (90, 25), (85, 22), (80, 20), (75, 22), (70, 25),
     (65, 25), (60, 27), (55, 28), (50, 30), (45, 32), (40, 35), (35, 38)],
    # India
    [(68, 23), (72, 20), (76, 8), (80, 8), (80, 15), (85, 20), (88, 22),
     (90, 25), (88, 26), (85, 24), (82, 22), (78, 18), (75, 15), (72, 20)],
    # SE Asia
    [(92, 22), (95, 18), (97, 16), (100, 10), (103, 2), (105, 8), (107, 12),
     (109, 14), (106, 20), (104, 22), (100, 20), (97, 22), (95, 25)],
    # Korea
    [(124, 38), (126, 35), (127, 35), (129, 36), (129, 39), (127, 41),
     (125, 40)],
    # UK
    [(-5, 50), (-3, 53), (-6, 56), (-5, 58), (-3, 58), (-1, 56), (1, 52),
     (0, 50), (-2, 50)],
    # Japan
    [(130, 31), (133, 34), (136, 35), (139, 36), (141, 39), (142, 42),
     (144, 44), (141, 45), (139, 41), (137, 38), (134, 34), (131, 32)],
    # Indonesia
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (125, -9), (130, -3), (135, -4), (140, -8), (136, -2), (130, 1),
     (125, 1), (120, 0), (115, 2), (110, 0), (105, 3), (100, 5)],
    # Australia
    [(114, -22), (118, -18), (122, -15), (128, -14), (132, -12), (136, -12),
     (140, -15), (142, -11), (146, -19), (150, -23), (153, -27), (153, -32),
     (150, -37), (146, -39), (140, -38), (135, -35), (130, -32), (126, -32),
     (120, -34), (115, -33), (113, -28)],
    # New Zealand
    [(167, -46), (170, -43), (173, -40), (176, -38), (178, -38), (175, -41),
     (172, -44), (168, -47)],
    # Madagascar
    [(44, -16), (47, -15), (50, -17), (49, -22), (47, -25), (44, -22),
     (43, -18)],
]

# (number, label, lon, lat, label dx, label dy)
PINS = [
    (1, "Antalya", 30.7, 36.9, -42, 10),
    (2, "Kyiv", 30.5, 50.5, 8, -4),
    (3, "Bahrain", 50.6, 26.2, 8, -12),
    (4, "Hong Kong", 114.2, 22.3, 8, 2),
    (5, "Wellington", 174.8, -41.3, -64, 2),
    (6, "Liverpool", -3.0, 53.4, -50, -12),
    (7, "Turin", 7.7, 45.1, 8, 8),
    (8, "Las Vegas", -115.1, 36.2, -62, -4),
    (9, "Khartoum", 32.5, 15.5, -48, 2),
    (10, "Riyadh", 46.7, 24.7, 8, 10),
    (11, "Cikande", 106.3, -6.2, 8, 2),
    (12, "Manipur", 93.9, 24.8, 8, -10),
    (13, "Brussels", 4.4, 50.9, 8, -12),
    (14, "Seoul", 127.0, 37.5, 8, -4),
    (15, "Melbourne", 145.0, -37.8, -66, 2),
]


def draw_map(d, y):
    """World map strip with 15 numbered pins keyed to the stories."""
    y += section_head(d, MX, y, "THE WORLD ON SUNDAY \u2014 15 PINNED STORIES")
    map_h = 126
    x0, y0 = MX + 2, y
    x1, y1 = MX + CW - 2, y + map_h
    d.rectangle([x0, y0, x1, y1], fill=(198, 220, 232), outline=INK, width=1)

    def proj(lon, lat):
        px = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
        py = y0 + (78.0 - lat) / 136.0 * (y1 - y0)
        return px, py

    for poly in LAND:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(196, 200, 150), outline=(140, 145, 100))
    f_lab = font(SANSB, 8)
    for num, label, lon, lat, dx, dy in PINS:
        px, py = proj(lon, lat)
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED,
                  outline=WHITE, width=1)
        t = str(num)
        tw = d.textlength(t, font=f_lab)
        d.text((px - tw / 2, py - 4), t, font=f_lab, fill=WHITE)
        d.text((px + dx, py + dy), label, font=f_lab, fill=INK,
               stroke_width=2, stroke_fill=(247, 243, 233))
    return 19 + map_h + 2


TAIL = [
    "Manipur toxic liquor toll reaches 19",
    "Belgium strike notice: 429 Monday flights cancelled",
    "Seoul education minister resigns",
    "Marles: CBO \u201cwrong\u201d on AUKUS subs",
    "Pope\u2019s lunch for 1,300 poor",
    "Nepal PM Shah arrives in Delhi",
    "Estonia to shut 5 Russia crossings 1 Dec",
    "Sparta II still smouldering, flames out",
    "Iran power cuts begin",
    "Bolsonaro stable in ICU",
    "Fukushima village freed as roads reopen",
    "Hamas seeks urgent mediator talks",
    "Poland: Russia tried to kill Kyivstoner in Aug too",
    "Four-nation call for Gaza aid access",
    "M5.3 quake off Balut Island",
    "Myanmar M4.1; Japan M4.9 and M4.1",
    "Taiwan bourse meets brokers on margins",
    "ACLED: 30+ Kordofan towns retaken since early Nov",
    "Sea-Tac protest over ICE arrests",
    "Melbourne 1956 \u2014 70 years ago today",
    "Bar\u00e7a 3\u20132 Villarreal: 3 goals in 10 min",
    "Juventus 4\u20130 Venezia",
    "Atalanta 4\u20134 Inter: Esposito hat-trick",
    "Hull 2\u20130 Brighton: McBurnie double",
    "Crew 3\u20130 Inter Miami: Messi beaten",
    "ATP doubles: Arribage/Olivetti win",
]

TAIL_PINS = {12: 0, 13: 1, 14: 2, 15: 19}  # pin -> tail index (Manipur, Brussels, Seoul, Melbourne)


def draw_tail(d, y):
    """ALSO ON SUNDAY 22 NOVEMBER — one line per story, three columns."""
    y += section_head(d, MX, y, "ALSO ON SUNDAY 22 NOVEMBER")
    f = font(SANS, 9)
    col_w = CW // 3
    rows = 9
    for i, item in enumerate(TAIL):
        cx = MX + (i % 3) * col_w
        cy = y + (i // 3) * 11
        d.text((cx, cy), "\u2022", font=f, fill=REDD)
        pin = None
        for p, idx in TAIL_PINS.items():
            if idx == i:
                pin = p
        tx = cx + 9
        if pin is not None:
            pin_chip(d, tx, cy, pin, r=5)
            tx += 13
        d.text((tx, cy), item, font=f, fill=INK)
    return 19 + rows * 11 + 2


TRAPS = [
    "Wall St rout, S&P \u22123.7% to 6,910 \u2014 Fri 20 Nov",
    "Bitcoin low $55,130 \u2014 Sat 21 Nov",
    "Riemann proof / Lean certification \u2014 Fri 20 / Sat 21 Nov",
    "Bayelsa boat, 24 dead \u2014 Fri 20 Nov",
    "Gaza aid-van strike \u2014 Sat 21 Nov",
    "Denmark expels Russian attach\u00e9 \u2014 Fri 20 Nov",
    "Japan\u2013Korea poll, 62% affinity \u2014 Fri 20 Nov",
    "Cummins keeps captaincy \u2014 Sat 21 Nov",
    "Trump \u201cpermanent\u201d Iran deal \u2014 Sat 21 Nov",
    "EU\u2013Indonesia deal signed \u2014 Sat 21 Nov",
    "England 37\u201312 All Blacks \u2014 Sat 21 Nov",
    "ICJ: Myanmar guilty of Rohingya genocide \u2014 Thu 19 Nov",
]


def draw_datecheck(d, y):
    """Red-bordered DATE CHECK strip: traps with their true dates."""
    h = 84
    d.rectangle([MX, y, MX + CW, y + h], fill=(255, 244, 244),
                outline=RED, width=2)
    f_h = font(SANSB, 11)
    d.text((MX + 8, y + 4), "DATE CHECK \u2014 NOT TODAY", font=f_h, fill=RED)
    f = font(SANS, 9)
    col_w = (CW - 16) // 2
    for i, trap in enumerate(TRAPS):
        cx = MX + 8 + (i % 2) * col_w
        cy = y + 20 + (i // 2) * 11
        d.text((cx, cy), "NOT TODAY \u2014 " + trap, font=f, fill=INK)
    return h + 2


def build():
    sheet = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(sheet)
    y = 6
    y += draw_masthead(d, y)
    y += draw_subhead(d, y)
    y += draw_stats(d, y)
    y += draw_regions(d, y)
    y += draw_lead1(sheet, d, y)
    y += draw_leads_row(sheet, d, y)
    y += draw_timeline(d, y)
    y += draw_mediums(sheet, d, y)
    y += draw_map(d, y)
    y += draw_tail(d, y)
    y += draw_datecheck(d, y)
    print("final y =", y, "(canvas 1024)")
    assert y <= 1024, "sheet overflowed: %d" % y
    out = os.path.join(HERE, "entry.png")
    sheet.save(out, optimize=True)
    data = open(out, "rb").read()
    print("entry.png bytes:", len(data))
    print("sha256:", hashlib.sha256(data).hexdigest())
    # try a palette version; keep it only if it is smaller
    pal = sheet.convert("P", palette=Image.ADAPTIVE, colors=256)
    pal_path = os.path.join(HERE, "entry-pal.png")
    pal.save(pal_path, optimize=True)
    pal_data = open(pal_path, "rb").read()
    print("palette bytes:", len(pal_data))
    if len(pal_data) < len(data):
        os.replace(pal_path, out)
        print("kept palette version")
        data = pal_data
        print("sha256:", hashlib.sha256(data).hexdigest())
    else:
        os.remove(pal_path)
        print("kept RGB version")
    assert len(data) <= 1048576, "over the 1 MiB cap"
    return out


if __name__ == "__main__":
    build()
