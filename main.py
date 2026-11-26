#!/usr/bin/env python3
"""news-image-20261126: sum up Thursday 26 November 2026's world news in one image.

Pure standard library. Draws a newspaper front page (1024x1024 PNG) with a
hand-built 5x7 bitmap font and writes it to /output/entry.png
(MAKEFUN_OUTPUT_DIR stands in for /output outside the grader).

Stories (all first reported on 26 Nov 2026, from the day's news wires):
  1. Ukraine war: Russia's own figures put its military dead near 500,000.
  2. Cairo: a fuel-tanker fire by the Warraq tunnel in Giza kills at least 30.
  3. Markets: Nasdaq slides nearly 4% in an AI sell-off; Nvidia tumbles.
  4. Space: BepiColombo reaches Mercury orbit after an eight-year journey.
  5. US midterms: Democrats retake Congress.
  6. Colombia: police free 20 hostages after a 17-hour supermarket siege.
Ticker: Pakistan's first astronaut joins China's space station; Norway's
supreme court voids disputed oil licences; Gukesh draws game 2 of the
World Chess Championship.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font -----
# 5x7 bitmap glyphs, written out by hand. '#' is an on pixel.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
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
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    "'": ("00100", "00100", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01110", "10001", "10001", "01000", "10101", "10010", "01101"),
    '%': ("10001", "10010", "00010", "00100", "01000", "01001", "10001"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}

# -------------------------------------------------------------- canvas -----
PAPER = (247, 243, 234)
INK = (20, 20, 20)
RED = (178, 38, 30)
NAVY = (22, 35, 63)
NAVY2 = (14, 24, 48)
GOLD = (255, 209, 102)
CREAM = (232, 236, 244)
ORANGE = (249, 115, 22)
SKY = (219, 234, 254)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Canvas:
    def __init__(self, w=W, h=H, bg=PAPER):
        self.w, self.h = w, h
        self.px = bytearray(bg[0] for _ in range(w * h * 3))
        # fill properly (bytearray trick above only fills first channel)
        for i in range(w * h):
            self.px[i * 3:i * 3 + 3] = bytes(bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def vgrad(self, x, y, w, h, top, bottom):
        for yy in range(h):
            self.rect(x, y + yy, w, 1, _lerp(top, bottom, yy / max(1, h - 1)))

    def line(self, x0, y0, x1, y1, c, th=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            for a in range(th):
                for b in range(th):
                    self.set(x + a - th // 2, y + b - th // 2, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else -1
            if dx >= 0:
                self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            t = 1 - ((yy - cy) / ry) ** 2
            dx = int(rx * (t ** 0.5)) if t >= 0 else -1
            if dx >= 0:
                self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def poly(self, pts, c):
        # scanline fill for a simple polygon
        ys = [p[1] for p in pts]
        for yy in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), yy, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)

    def tri(self, a, b, cc, c):
        self.poly([a, b, cc], c)

    # ---- text ----
    def text(self, x, y, s, scale, c, align="left"):
        s = s.upper()
        adv = 6 * scale
        if align == "center":
            x -= len(s) * adv // 2
        elif align == "right":
            x -= len(s) * adv
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        self.rect(x + col * scale, y + r * scale, scale, scale, c)
            x += adv

    def text_w(self, s, scale):
        return len(s.upper()) * 6 * scale

    def wrap(self, s, max_w, scale):
        words, lines, cur = s.upper().split(), [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if self.text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


# ------------------------------------------------------------------ png -----
def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
           _chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# -------------------------------------------------------------- scenes -----
def panel_frame(cv, x, y, w, h):
    cv.rect(x, y, w, 3, INK)
    cv.rect(x, y + h - 3, w, 3, INK)
    cv.rect(x, y, 3, h, INK)
    cv.rect(x + w - 3, y, 3, h, INK)


def masthead(cv):
    cv.text(W // 2, 26, "THE WORLD TODAY", 6, INK, align="center")
    cv.rect(24, 96, W - 48, 4, INK)
    cv.text(W // 2, 108, "THURSDAY, 26 NOVEMBER 2026", 2, RED, align="center")
    cv.rect(24, 130, W - 48, 3, INK)


def draw_cross(cv, x, y, s, c):
    cv.rect(x - s // 2, y - s, s, 2 * s + 1, c)
    cv.rect(x - s, y - s // 2, 2 * s + 1, s, c)


def hero(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, NAVY, NAVY2)
    cv.rect(x, y, w, 3, GOLD)
    cv.text(x + 24, y + 18, "UKRAINE WAR  -  THE TOLL", 2, (255, 107, 94))
    # giant number, left
    cv.text(x + 24, y + 62, "500,000", 9, GOLD)
    cv.text(x + 24, y + 132, "RUSSIAN WAR DEAD", 3, (255, 255, 255))
    cv.text(x + 24, y + 158, "IN UKRAINE", 3, (255, 255, 255))
    # rows of small crosses: a war cemetery under the number
    for r in range(3):
        for i in range(9):
            cx = x + 40 + i * 30 + (r % 2) * 12
            cy = y + 218 + r * 22
            draw_cross(cv, cx, cy, 5, (180, 190, 210))
    # right column: the story
    tx = x + 560
    cv.rect(tx - 16, y + 20, 3, h - 40, (90, 105, 140))
    body = cv.wrap("RUSSIA'S OWN FIGURES PUT ITS MILITARY DEAD AT NEARLY "
                   "HALF A MILLION - THE GRIMMEST MILESTONE OF THE WAR.",
                   w - 600, 2)
    yy = y + 66
    for ln in body:
        cv.text(tx, yy, ln, 2, CREAM)
        yy += 20
    # three candles with flames, bottom right
    for i, cx in enumerate((tx + 30, tx + 90, tx + 150)):
        cv.rect(cx - 7, y + h - 70, 14, 40, (240, 235, 220))
        cv.rect(cx - 7, y + h - 74, 14, 4, (200, 190, 170))
        cv.tri((cx - 6, y + h - 76), (cx + 6, y + h - 76), (cx, y + h - 100),
               (255, 170, 40) if i != 1 else (255, 210, 80))
    cv.text(tx, y + h - 18, "KYIV  -  MOSCOW", 1, (150, 165, 195))


def cairo_art(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (60, 20, 8), ORANGE)
    # smoke plumes
    for cx, r in ((x + 60, 26), (x + 130, 34), (x + 210, 24), (x + 270, 30)):
        cv.circle(cx, y + 34, r, (35, 25, 20))
        cv.circle(cx - 12, y + 52, r - 8, (45, 32, 24))
    # highway
    cv.rect(x, y + h - 26, w, 26, (40, 40, 44))
    cv.rect(x, y + h - 14, w, 3, (230, 200, 60))
    # tanker truck
    bx, by = x + 55, y + h - 62
    cv.rect(bx, by, 120, 26, (150, 30, 25))          # tank
    cv.ellipse(bx + 60, by + 13, 60, 13, (190, 45, 35))
    cv.rect(bx + 122, by + 4, 42, 22, (120, 25, 20))  # cab
    cv.rect(bx + 138, by + 8, 20, 10, (180, 220, 240))  # window
    for wx in (bx + 22, bx + 92, bx + 142):
        cv.circle(wx, y + h - 26, 11, (15, 15, 15))
        cv.circle(wx, y + h - 26, 4, (160, 160, 160))
    # flames licking the tank
    for fx in (bx + 18, bx + 58, bx + 98):
        cv.tri((fx - 12, by), (fx + 12, by), (fx, by - 34), (255, 200, 40))
        cv.tri((fx - 6, by), (fx + 6, by), (fx, by - 20), (255, 240, 120))


def markets_art(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (30, 41, 59), (12, 16, 28))
    # grid
    for gx in range(x + 30, x + w - 10, 34):
        cv.line(gx, y + 12, gx, y + h - 12, (60, 70, 95))
    for gy in range(y + 16, y + h - 8, 26):
        cv.line(x + 12, gy, x + w - 12, gy, (60, 70, 95))
    # falling chart
    pts = [(x + 20, y + 26), (x + 70, y + 40), (x + 115, y + 34),
           (x + 165, y + 62), (x + 215, y + 58), (x + 265, y + 92),
           (x + w - 22, y + h - 18)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], (255, 70, 60), 4)
    cv.circle(pts[-1][0], pts[-1][1], 6, (255, 70, 60))
    # microchip
    cx, cy = x + w - 66, y + 30
    cv.rect(cx - 24, cy - 24, 48, 48, (15, 23, 42))
    cv.rect(cx - 18, cy - 18, 36, 36, (30, 58, 95))
    cv.rect(cx - 8, cy - 8, 16, 16, GOLD)
    for k in range(5):
        xx = cx - 20 + k * 10
        cv.rect(xx, cy - 30, 3, 6, (180, 190, 210))
        cv.rect(xx, cy + 24, 3, 6, (180, 190, 210))
        cv.rect(cx - 30, cy - 20 + k * 10, 6, 3, (180, 190, 210))
        cv.rect(cx + 24, cy - 20 + k * 10, 6, 3, (180, 190, 210))


def space_art(cv, x, y, w, h):
    cv.rect(x, y, w, h, (5, 8, 18))
    for sx, sy in ((x + 30, y + 18), (x + 90, y + 40), (x + 150, y + 14),
                   (x + 210, y + 52), (x + 260, y + 22), (x + 60, y + 70),
                   (x + 180, y + 84), (x + 240, y + 96), (x + 120, y + 100)):
        cv.circle(sx, sy, 2, (255, 255, 255))
    # Mercury
    mx, my, mr = x + w - 78, y + h - 52, 42
    cv.circle(mx, my, mr, (196, 130, 70))
    cv.circle(mx - 12, my - 8, 9, (160, 100, 50))
    cv.circle(mx + 14, my + 10, 12, (160, 100, 50))
    cv.circle(mx + 4, my - 18, 6, (160, 100, 50))
    cv.circle(mx - 20, my + 16, 5, (170, 108, 55))
    # probe with solar panels and dish
    px, py = x + 92, y + 44
    cv.rect(px - 26, py - 5, 52, 10, (40, 90, 160))
    cv.rect(px - 26, py - 5, 52, 3, (120, 170, 230))
    cv.rect(px - 8, py - 8, 16, 16, (220, 225, 235))
    cv.rect(px - 30, py - 8, 4, 16, (180, 190, 210))
    cv.tri((px + 8, py - 8), (px + 8, py + 8), (px + 26, py), (200, 205, 215))
    cv.line(px - 60, py + 26, px + 120, py + 60, (120, 140, 180))
    cv.line(px + 60, py + 44, px + 118, py + 66, (120, 140, 180))


def capitol_art(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, SKY, (190, 210, 235))
    # stars row
    for i in range(7):
        draw_cross(cv, x + 16 + i * 14, y + 14, 3, (40, 60, 110))
    # capitol: base, columns, dome
    bx = x + 30
    cv.rect(bx, y + h - 34, w - 60, 12, (245, 245, 240))
    cv.rect(bx + 10, y + h - 52, w - 80, 18, (250, 250, 245))
    for i in range(6):
        cv.rect(bx + 18 + i * 24, y + h - 78, 8, 26, (250, 250, 245))
    cx = x + w // 2
    cv.rect(cx - 34, y + h - 84, 68, 8, (250, 250, 245))
    cv.ellipse(cx, y + h - 88, 30, 26, (250, 250, 245))
    cv.rect(cx - 3, y + h - 122, 6, 14, (250, 250, 245))
    cv.circle(cx, y + h - 124, 4, GOLD)
    # ballot box + tick
    qx, qy = x + w - 52, y + 22
    cv.rect(qx - 18, qy, 36, 26, (178, 38, 30))
    cv.rect(qx - 22, qy - 8, 44, 8, (140, 25, 20))
    cv.rect(qx - 8, qy - 8, 16, 4, (247, 243, 234))
    cv.line(qx - 12, qy + 12, qx - 4, qy + 20, (255, 255, 255), 3)
    cv.line(qx - 4, qy + 20, qx + 12, qy + 2, (255, 255, 255), 3)


def colombia_art(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (254, 243, 199), (240, 220, 160))
    # storefront
    sx = x + 26
    cv.rect(sx, y + 34, w - 52, h - 60, (250, 248, 240))
    # striped awning
    for i in range(8):
        col = (34, 120, 70) if i % 2 == 0 else (250, 248, 240)
        cv.rect(sx + i * ((w - 52) // 8), y + 34, (w - 52) // 8 + 1, 22, col)
    cv.rect(sx, y + 56, w - 52, 4, INK)
    # door + window
    cv.rect(sx + 18, y + 78, 52, h - 104, (90, 60, 40))
    cv.rect(sx + 26, y + 86, 36, 30, (180, 220, 240))
    cv.rect(sx + 88, y + 78, w - 52 - 106, 44, (180, 220, 240))
    cv.line(sx + 88, y + 100, sx + w - 70, y + 100, INK)
    cv.line(sx + 88 + (w - 158) // 2, y + 78, sx + 88 + (w - 158) // 2,
            y + 122, INK)
    # police shield
    qx, qy = x + w - 46, y + 26
    cv.poly([(qx, qy), (qx + 26, qy), (qx + 26, qy + 22),
             (qx + 13, qy + 38), (qx, qy + 22)], (30, 64, 175))
    cv.text(qx + 5, qy + 10, "20", 1, (255, 255, 255))


def story_panel(cv, x, y, w, h, art, kicker, headline, body, hscale=2):
    panel_frame(cv, x, y, w, h)
    art(cv, x + 3, y + 3, w - 6, 118)
    cv.rect(x, y + 121, w, 2, INK)
    yy = y + 132
    cv.text(x + 12, yy, kicker, 1, RED)
    yy += 14
    for ln in cv.wrap(headline, w - 24, hscale):
        cv.text(x + 12, yy, ln, hscale, INK)
        yy += 7 * hscale + 4
    yy += 2
    for ln in cv.wrap(body, w - 24, 1):
        cv.text(x + 12, yy, ln, 1, (60, 60, 60))
        yy += 11


def wide_panel(cv, x, y, w, h, art, kicker, headline, body):
    panel_frame(cv, x, y, w, h)
    aw = 200
    art(cv, x + 3, y + 3, aw - 6, h - 6)
    cv.rect(x + aw, y, 2, h, INK)
    tx = x + aw + 16
    yy = y + 18
    cv.text(tx, yy, kicker, 1, RED)
    yy += 16
    for ln in cv.wrap(headline, w - aw - 32, 3):
        cv.text(tx, yy, ln, 3, INK)
        yy += 25
    yy += 4
    for ln in cv.wrap(body, w - aw - 32, 2):
        cv.text(tx, yy, ln, 2, (60, 60, 60))
        yy += 20


def ticker(cv, y, h):
    cv.rect(24, y, W - 48, h, INK)
    items = ("ALSO TODAY:  PAKISTAN'S FIRST ASTRONAUT JOINS CHINA'S SPACE "
             "STATION  |  NORWAY COURT VOIDS DISPUTED OIL LICENCES  |  "
             "GUKESH DRAWS GAME 2 OF WORLD CHESS FINAL")
    lines = cv.wrap(items, W - 48 - 32, 1)
    yy = y + 8
    for ln in lines:
        cv.text(W // 2, yy, ln, 1, (240, 240, 235), align="center")
        yy += 11

# ------------------------------------------------------------------ main -----
def build():
    cv = Canvas()
    # outer border
    cv.rect(0, 0, W, 6, INK)
    cv.rect(0, H - 6, W, 6, INK)
    cv.rect(0, 0, 6, H, INK)
    cv.rect(W - 6, 0, 6, H, INK)

    masthead(cv)
    hero(cv, 24, 140, W - 48, 290)

    y1, h1 = 446, 240
    pw = (W - 48 - 24) // 3
    story_panel(cv, 24, y1, pw, h1, cairo_art, "EGYPT",
                "TANKER FIRE KILLS 30 NEAR CAIRO",
                "Fuel tanker blaze by the Warraq tunnel in Giza; 15 more hurt.")
    story_panel(cv, 24 + pw + 12, y1, pw, h1, markets_art, "MARKETS",
                "AI SELL-OFF HITS WALL ST",
                "Nasdaq slides nearly 4% as Nvidia tumbles on AI fears.")
    story_panel(cv, 24 + 2 * (pw + 12), y1, pw, h1, space_art, "SPACE",
                "BEPICOLOMBO REACHES MERCURY",
                "Probe enters orbit after an eight-year journey.")

    y2, h2 = 702, 230
    ww = (W - 48 - 12) // 2
    wide_panel(cv, 24, y2, ww, h2, capitol_art, "USA - MIDTERMS",
               "DEMOCRATS RETAKE CONGRESS",
               "Midterm victory flips control in Washington.")
    wide_panel(cv, 24 + ww + 12, y2, ww, h2, colombia_art, "COLOMBIA",
               "20 HOSTAGES FREED",
               "Police storm supermarket after a 17-hour siege.")

    ticker(cv, 948, 56)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(build(), path)
    print(f"Wrote {path}: {size} bytes, {W}x{H}")


if __name__ == "__main__":
    main()
