#!/usr/bin/env python3
"""news-image-20261118 entry: draws a one-page newspaper front page summing up
the world news of Wednesday 18 November 2026 and writes it to entry.png.

Pure Python 3 standard library (struct, zlib, os). No network, no randomness,
no clock: the same input always produces the same bytes. The image is drawn
pixel by pixel with a small built-in 5x7 bitmap font, then encoded as PNG.
Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   (or writes /output/entry.png)
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
PAPER = (247, 243, 234)
INK = (26, 34, 54)
NAVY = (24, 42, 74)
NAVY_LT = (43, 66, 110)
RED = (178, 38, 30)
RED_LT = (214, 90, 80)
SKY = (186, 214, 230)
SKY_DK = (140, 180, 205)
SEA = (46, 111, 142)
SEA_DK = (28, 84, 112)
STEEL = (96, 104, 116)
STEEL_DK = (58, 64, 76)
SMOKE = (120, 122, 126)
SMOKE_LT = (158, 160, 163)
SUN = (232, 178, 74)
GREEN = (46, 125, 70)
GREEN_LT = (120, 190, 130)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
CREAM = (238, 231, 214)
ORANGE = (214, 110, 44)
TEAL = (32, 140, 130)

# ------------------------------------------------------------- 5x7 font -----
# Each glyph: 7 rows of 5 pixels, '#' = on. Uppercase only; text is uppercased
# before drawing. Characters not in the table draw as a blank.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}

# ---------------------------------------------------------------- canvas ----
buf = bytearray(W * H * 3)


def _set(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def fill_rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i], buf[i + 1], buf[i + 2] = c


def hline(x, y, w, c, t=1):
    fill_rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    fill_rect(x, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        for a in range(t):
            for b in range(t):
                _set(x0 + a, y0 + b, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c, filled=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if filled:
                if d <= r * r:
                    _set(xx, yy, c)
            else:
                if r * r - 2 * r <= d <= r * r:
                    _set(xx, yy, c)


def arc(cx, cy, r, a0, a1, c, t=2):
    # Angles in degrees, 0 = east, going clockwise (screen coords, y down).
    import math
    steps = max(8, int(abs(a1 - a0) * r / 12))
    for s in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * s / steps)
        x = int(round(cx + r * math.cos(a)))
        y = int(round(cy + r * math.sin(a)))
        for dx in range(t):
            for dy in range(t):
                _set(x + dx, y + dy, c)


def poly(points, c):
    # Filled polygon via scanline fill.
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                _set(x, y, c)


# ------------------------------------------------------------------ text ----
def char_w(scale):
    return 5 * scale + scale  # glyph + 1 unit gap


def text_w(s, scale):
    s = s.upper()
    if not s:
        return 0
    return len(s) * char_w(scale) - scale


def draw_text(x, y, s, scale, color):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch)
        if g:
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        fill_rect(cx + col * scale, y + r * scale, scale, scale, color)
        cx += char_w(scale)
    return cx


def draw_text_center(x, y, w, s, scale, color):
    draw_text(x + (w - text_w(s, scale)) // 2, y, s, scale, color)


def wrap(s, scale, max_w):
    """Greedy word wrap; returns list of lines."""
    words = s.upper().split(' ')
    lines, cur = [], ''
    for word in words:
        cand = word if not cur else cur + ' ' + word
        if text_w(cand, scale) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, scale, color, max_w, line_gap=4):
    lines = wrap(s, scale, max_w)
    yy = y
    for ln in lines:
        draw_text(x, yy, ln, scale, color)
        yy += 7 * scale + line_gap
    return yy


# -------------------------------------------------------------- pictures ----
def draw_bridge_scene(x, y, w, h):
    """Lead illustration: the Kerch/Crimea bridge with its road arch broken
    and fallen into the strait, smoke rising from the gap."""
    fill_rect(x, y, w, h, SKY)
    circle(x + w - 70, y + 42, 26, SUN)
    circle(x + w - 70, y + 42, 18, (240, 198, 110))
    # distant shore
    fill_rect(x, y + h - 108, w, 14, (120, 150, 140))
    # sea
    fill_rect(x, y + h - 94, w, 94, SEA)
    fill_rect(x, y + h - 94, w, 4, SEA_DK)
    for wy in (y + h - 70, y + h - 46, y + h - 22):
        for wx in range(x + 12, x + w - 12, 46):
            hline(wx, wy, 26, SEA_DK, 2)
    # bridge deck: left span, gap, right span
    deck_y = y + h - 150
    fill_rect(x + 10, deck_y, 150, 14, STEEL_DK)
    fill_rect(x + w - 160, deck_y, 150, 14, STEEL_DK)
    # pylons
    fill_rect(x + 34, deck_y - 62, 10, 62, STEEL_DK)
    fill_rect(x + w - 44, deck_y - 62, 10, 62, STEEL_DK)
    # arch stubs on both sides of the gap
    arc(x + 160, deck_y + 14, 62, 200, 340, STEEL, 5)
    arc(x + w - 160, deck_y + 14, 62, 200, 340, STEEL, 5)
    # collapsed span: tilted wreckage sliding into the water
    poly([(x + 168, deck_y + 2), (x + 196, deck_y + 2),
          (x + 226, deck_y + 78), (x + 198, deck_y + 78)], STEEL_DK)
    poly([(x + 168, deck_y + 2), (x + 176, deck_y + 14),
          (x + 206, deck_y + 78), (x + 198, deck_y + 78)], STEEL)
    # support legs in the water
    vline(x + 60, deck_y + 14, 66, STEEL_DK, 6)
    vline(x + w - 66, deck_y + 14, 66, STEEL_DK, 6)
    # smoke over the gap
    circle(x + w // 2 - 14, deck_y - 26, 16, SMOKE)
    circle(x + w // 2 + 12, deck_y - 40, 20, SMOKE_LT)
    circle(x + w // 2 + 34, deck_y - 18, 12, SMOKE)
    circle(x + w // 2 - 34, deck_y - 48, 12, SMOKE_LT)


def draw_radar(x, y, w, h):
    """Gulf story: a radar dish sweeping, drones intercepted above it."""
    cx, cy = x + w // 2, y + h // 2 + 12
    # sky dots = intercepted drones
    for dx, dy in ((-52, -36), (44, -42), (8, -50)):
        _set(cx + dx, cy + dy, INK)
        line(cx + dx - 7, cy + dy, cx + dx + 7, cy + dy, INK, 2)
        line(cx + dx, cy + dy - 7, cx + dx, cy + dy + 7, INK, 2)
    # radar dish
    arc(cx, cy - 6, 34, 180, 360, NAVY, 4)
    line(cx - 34, cy - 6, cx + 34, cy - 6, NAVY, 4)
    line(cx, cy - 6, cx + 26, cy - 30, RED, 3)
    # mast + base (base kept clear of the headline below the drawing area)
    vline(cx, cy - 6, 30, NAVY, 6)
    poly([(cx - 26, cy + 24), (cx + 26, cy + 24), (cx + 8, cy + 2),
          (cx - 8, cy + 2)], NAVY)
    hline(x + 16, cy + 24, w - 32, NAVY, 3)


def draw_quad(x, y, w, h):
    """Asia diplomacy: four flag poles for the four Quad nations."""
    base = y + h - 26
    cols = [RED, (255, 153, 51), (188, 0, 45), (0, 47, 108)]
    labels = ['US', 'IN', 'JP', 'AU']
    step = (w - 40) // 4
    for i in range(4):
        px = x + 24 + i * step
        vline(px, y + 22, base - y - 22, INK, 3)
        fill_rect(px + 3, y + 22, 34, 22, cols[i])
        if i == 1:
            circle(px + 20, y + 33, 6, NAVY, filled=False)
        draw_text(px - 2, base + 6, labels[i], 2, INK)
    hline(x + 14, base, w - 28, INK, 3)


def draw_chip(x, y, w, h):
    """Tech story: a chip with a rising chart arrow."""
    cx, cy = x + w // 2 - 10, y + h // 2 + 2
    # chip body
    fill_rect(cx - 28, cy - 28, 56, 56, NAVY)
    fill_rect(cx - 18, cy - 18, 36, 36, NAVY_LT)
    fill_rect(cx - 10, cy - 10, 20, 20, GREEN)
    for i in range(5):
        fill_rect(cx - 28 + i * 11, cy - 37, 5, 9, STEEL_DK)
        fill_rect(cx - 28 + i * 11, cy + 28, 5, 9, STEEL_DK)
        fill_rect(cx - 37, cy - 28 + i * 11, 9, 5, STEEL_DK)
        fill_rect(cx + 28, cy - 28 + i * 11, 9, 5, STEEL_DK)
    # rising arrow
    line(cx + 22, cy + 20, cx + 44, cy - 2, GREEN, 4)
    line(cx + 44, cy - 2, cx + 62, cy - 22, GREEN, 4)
    line(cx + 62, cy - 22, cx + 51, cy - 22, GREEN, 4)
    line(cx + 62, cy - 22, cx + 62, cy - 11, GREEN, 4)


def draw_cyclone(x, y, w, h):
    """Weather story: a spiral storm seen from above."""
    cx, cy = x + w // 2, y + h // 2
    for r, a0, a1 in ((34, 20, 300), (26, 110, 390), (18, 200, 470), (11, 290, 540)):
        arc(cx, cy, r, a0, a1, TEAL, 4)
    circle(cx, cy, 6, TEAL)
    # rain streaks (kept short so they clear the headline below)
    for dx, dy in ((-50, 24), (50, 26), (-54, -16), (54, -12)):
        line(cx + dx, cy + dy, cx + dx - 7, cy + dy + 11, SKY_DK, 3)


def draw_football(x, y, w, h):
    """Sport story: a football and the 2-1 scoreline."""
    cx, cy = x + w // 2 - 46, y + h // 2 + 4
    circle(cx, cy, 34, WHITE)
    circle(cx, cy, 34, INK, filled=False)
    poly([(cx, cy - 12), (cx + 11, cy - 4), (cx + 7, cy + 10),
          (cx - 7, cy + 10), (cx - 11, cy - 4)], INK)
    for dx, dy in ((0, -34), (-30, -12), (30, -12), (-19, 28), (19, 28)):
        line(cx + (dx * 12) // 34, cy + (dy * 12) // 34, cx + dx, cy + dy, INK, 2)
    draw_text(cx + 52, cy - 22, '2-1', 4, RED)


# -------------------------------------------------------------- layout ------
def panel(x, y, w, h, kicker, kcolor, headline, body, draw_fn):
    fill_rect(x, y, w, h, WHITE)
    # border
    hline(x, y, w, INK, 2)
    hline(x, y + h - 2, w, INK, 2)
    vline(x, y, h, INK, 2)
    vline(x + w - 2, y, h, INK, 2)
    # kicker strip
    fill_rect(x + 2, y + 2, w - 4, 26, kcolor)
    draw_text(x + 12, y + 8, kicker, 2, WHITE)
    pad = 14
    ix, iy, iw, ih = x + pad, y + 34, w - 2 * pad, 78
    draw_fn(ix, iy, iw, ih)
    ty = y + 34 + 82
    draw_para(x + pad, ty, headline, 3, INK, w - 2 * pad, line_gap=3)
    n_head = len(wrap(headline, 3, w - 2 * pad))
    by = ty + n_head * (21 + 3) + 6
    draw_para(x + pad, by, body, 2, (74, 80, 96), w - 2 * pad, line_gap=3)


def build():
    fill_rect(0, 0, W, H, PAPER)
    m = 24
    cw = W - 2 * m  # 976

    # masthead
    draw_text_center(m, 30, cw, 'THE WORLD IN ONE DAY', 6, NAVY)
    draw_text_center(m, 84, cw, 'WEDNESDAY - 18 NOVEMBER 2026', 3, RED)
    hline(m, 122, cw, INK, 3)
    hline(m, 128, cw, INK, 1)

    # lead story
    ly, lh = 142, 318
    fill_rect(m, ly, cw, lh, WHITE)
    hline(m, ly, cw, INK, 2)
    hline(m, ly + lh - 2, cw, INK, 2)
    vline(m, ly, lh, INK, 2)
    vline(m + cw - 2, ly, lh, INK, 2)
    draw_bridge_scene(m + 14, ly + 14, 420, lh - 28)
    vline(m + 448, ly + 14, lh - 28, INK, 2)
    tx = m + 470
    tw = cw - 470 - 16
    fill_rect(tx, ly + 16, tw, 26, RED)
    draw_text(tx + 10, ly + 22, 'WAR IN EUROPE - TOP STORY', 2, WHITE)
    draw_para(tx, ly + 56, 'CRIMEA BRIDGE CRIPPLED', 4, INK, tw, line_gap=4)
    draw_para(tx, ly + 56 + 2 * 32 + 10,
              "UKRAINE HITS THE 19-KM LINK TO CRIMEA FOR A SECOND DAY. "
              "THE ROAD ARCH FALLS INTO THE SEA AS RUSSIA POUNDS KYIV "
              "BRIDGES IN REPLY.", 2, (74, 80, 96), tw, line_gap=4)
    draw_text(tx, ly + lh - 40, '1,441 DRONES - THE BIGGEST', 2, RED)
    draw_text(tx, ly + lh - 22, 'UKRAINIAN STRIKE OF THE WAR', 2, RED)

    # row 1: three panels
    ry, rh = 480, 248
    pw = (cw - 2 * 16) // 3
    panel(m, ry, pw, rh, 'GULF TENSIONS', NAVY, 'DRONES OVER BAHRAIN',
          'IRAN CLAIMS A HIT ON A US RADAR IN BAHRAIN. BAHRAIN AND THE US '
          'SAY ALL WERE SHOT DOWN.', draw_radar)
    panel(m + pw + 16, ry, pw, rh, 'ASIA DIPLOMACY', NAVY, 'TRUMP LANDS IN MANILA',
          'THE US PRESIDENT OPENS AN ASIA TOUR FOR QUAD TALKS, AHEAD OF A '
          'CHINA VISIT.', draw_quad)
    panel(m + 2 * (pw + 16), ry, pw, rh, 'TECH & MARKETS', NAVY, 'NVIDIA DOUBLES SALES',
          'REVENUE HITS $115.8BN IN ITS FIRST RESULTS SINCE HUANG WAS '
          'OUSTED AS CHIEF.', draw_chip)

    # row 2: two wide panels
    ry2, rh2 = 744, 232
    pw2 = (cw - 16) // 2
    panel(m, ry2, pw2, rh2, 'WEATHER', TEAL, 'CYCLONE AKVAN GROWS',
          'THE STORM STRENGTHENS OVER THE BAY OF BENGAL AS INDIA\'S EAST '
          'COAST BRACES FOR LANDFALL.', draw_cyclone)
    panel(m + pw2 + 16, ry2, pw2, rh2, 'SPORT', GREEN, 'INDIA BEAT PAKISTAN 2-1',
          'INDIA WIN A RECORD 10TH SAFF TITLE IN DHAKA. MS DHONI RETIRES '
          'FROM THE IPL.', draw_football)

    # footer
    draw_text_center(m, 992, cw,
                     'FIRST REPORTED 18 NOV 2026 - SOURCES: REUTERS, AP, AL JAZEERA',
                     2, (120, 118, 112))


# -------------------------------------------------------------- PNG out ------
def chunk(typ, data):
    c = struct.pack('>I', len(data)) + typ + data
    return c + struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)


def encode_png():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))


def main():
    build()
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'entry.png'), 'wb') as f:
        f.write(encode_png())


if __name__ == '__main__':
    main()
