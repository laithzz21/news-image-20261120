#!/usr/bin/env python3
"""make.fun bounty: Sum up 20 November's world news in one image.

Writes one 1024x1024 PNG to /output/entry.png (or $MAKEFUN_OUTPUT).

Stdlib only (struct, zlib, os). No network, no randomness, no clock:
two runs produce byte-identical output. Text is rendered with a built-in
5x7 bitmap font, scaled; all artwork is drawn from fixed shapes.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font. '#' = on, '.' = off. Lowercase is folded to uppercase.
FONT = {
    ' ': [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    'A': [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'B': ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    'C': [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    'D': ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    'E': ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    'F': ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    'G': [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    'H': ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'I': [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    'J': ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    'K': ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    'L': ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    'N': ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    'O': [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    'Q': [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    'S': [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    'U': ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'V': ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    'W': ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    'X': ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    'Z': ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    '0': [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    '1': ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    '2': [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    '3': ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    '6': [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    '7': ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    '8': [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    '9': [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    '.': [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ',': [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    ':': [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ';': [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."],
    '-': [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    '/': ["....#", "....#", "...#.", "...#.", "..#..", "..#..", ".#..."],
    '(': ["...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"],
    ')': ["##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."],
    '%': ["##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"],
    '$': ["..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."],
    '+': [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    '=': [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    '*': [".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."],
    '!': ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    '?': [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    '&': [".##..", "#..#.", "#..#.", ".#...", "#.##.", "#...#", ".##.#"],
    '|': ["..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    '_': [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    '#': [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
}

NAVY = (15, 35, 64)
NAVY2 = (20, 53, 94)
GOLD = (232, 197, 71)
PAPER = (245, 240, 225)
WHITE = (255, 255, 255)
INK = (17, 17, 17)
BODY = (51, 51, 51)
MUTED = (110, 110, 100)
BORDER = (213, 207, 192)
LIGHTGRAY = (176, 184, 197)


def text_width(s, scale):
    if not s:
        return 0
    return len(s) * 6 * scale - scale


def wrap_text(text, max_chars):
    """Greedy word wrap; returns a list of lines."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        while len(word) > max_chars:
            if cur:
                lines.append(cur)
                cur = ""
            lines.append(word[:max_chars])
            word = word[max_chars:]
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Img:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = c
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = r
                self.px[i + 1] = g
                self.px[i + 2] = b

    def rect_border(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, c, t=2):
        for ox in range(t):
            for oy in range(t):
                self.line(x0 + ox, y0 + oy, x1 + ox, y1 + oy, c)

    def fill_circle(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                    self.set(x, y, c)

    def circle_outline(self, cx, cy, r, c, t=2):
        for y in range(cy - r - 1, cy + r + 2):
            for x in range(cx - r - 1, cx + r + 2):
                d2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if (r - t) * (r - t) <= d2 <= r * r:
                    self.set(x, y, c)

    def fill_ellipse(self, cx, cy, rx, ry, c):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) * (x - cx)) * (ry * ry) + ((y - cy) * (y - cy)) * (rx * rx) <= rx * rx * ry * ry:
                    self.set(x, y, c)

    def fill_triangle(self, p1, p2, p3, c):
        minx = max(0, min(p1[0], p2[0], p3[0]))
        maxx = min(self.w - 1, max(p1[0], p2[0], p3[0]))
        miny = max(0, min(p1[1], p2[1], p3[1]))
        maxy = min(self.h - 1, max(p1[1], p2[1], p3[1]))

        def edge(ax, ay, bx, by, x, y):
            return (bx - ax) * (y - ay) - (by - ay) * (x - ax)

        area = edge(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
        if area == 0:
            return
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                w0 = edge(p2[0], p2[1], p3[0], p3[1], x, y)
                w1 = edge(p3[0], p3[1], p1[0], p1[1], x, y)
                w2 = edge(p1[0], p1[1], p2[0], p2[1], x, y)
                if (area > 0 and w0 >= 0 and w1 >= 0 and w2 >= 0) or \
                   (area < 0 and w0 <= 0 and w1 <= 0 and w2 <= 0):
                    self.set(x, y, c)

    def fill_poly(self, pts, c):
        """Scanline polygon fill (convex or concave, integer coords)."""
        if len(pts) < 3:
            return
        miny = max(0, min(p[1] for p in pts))
        maxy = min(self.h - 1, max(p[1] for p in pts))
        n = len(pts)
        for y in range(miny, maxy + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    xs.append(x)
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.set(x, y, c)

    # ------------------------------------------------------------ text --
    def draw_char(self, x, y, ch, c, scale):
        glyph = FONT.get(ch.upper(), FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '#':
                    self.fill_rect(x + col * scale, y + row * scale, scale, scale, c)

    def draw_text(self, x, y, text, c, scale, bold=False):
        text = text.upper()
        dx = max(1, scale // 2) if bold else 0
        cx = x
        for ch in text:
            self.draw_char(cx, y, ch, c, scale)
            if bold:
                self.draw_char(cx + dx, y, ch, c, scale)
            cx += 6 * scale
        return cx

    def draw_centered(self, cx, y, text, c, scale, bold=False):
        w = text_width(text, scale) + (max(1, scale // 2) if bold else 0)
        self.draw_text(cx - w // 2, y, text, c, scale, bold)

    def draw_wrapped(self, x, y, text, c, scale, max_chars, line_h, bold=False, max_lines=None):
        lines = wrap_text(text, max_chars)
        if max_lines is not None:
            lines = lines[:max_lines]
        for i, ln in enumerate(lines):
            self.draw_text(x, y + i * line_h, ln, c, scale, bold)
        return y + len(lines) * line_h


# -------------------------------------------------------------- icons ----
def starburst(img, cx, cy, r1, r2, c):
    """8-point star: lines + centre disc."""
    import math
    for k in range(8):
        a = k * math.pi / 4.0
        x1 = int(cx + r1 * math.cos(a))
        y1 = int(cy + r1 * math.sin(a))
        img.thick_line(cx, cy, x1, y1, c, 2)
    img.fill_circle(cx, cy, r2, c)


def icon_summit(img, cx, cy):
    # Three flags: USA, China, Russia.
    # Poles
    for fx in (cx - 46, cx - 13, cx + 20):
        img.fill_rect(fx, cy - 30, 2, 52, (90, 90, 90))
    # USA flag
    fx, fy = cx - 44, cy - 28
    for s in range(4):
        img.fill_rect(fx, fy + s * 5, 28, 5, (178, 34, 52) if s % 2 == 0 else WHITE)
    img.fill_rect(fx, fy, 12, 10, (30, 60, 120))
    img.fill_rect(fx + 3, fy + 3, 2, 2, WHITE)
    img.fill_rect(fx + 7, fy + 6, 2, 2, WHITE)
    # China flag
    fx = cx - 11
    img.fill_rect(fx, fy, 28, 20, (222, 41, 16))
    img.fill_circle(fx + 7, fy + 6, 3, GOLD)
    img.fill_circle(fx + 15, fy + 4, 1, GOLD)
    img.fill_circle(fx + 18, fy + 8, 1, GOLD)
    img.fill_circle(fx + 15, fy + 12, 1, GOLD)
    img.fill_circle(fx + 11, fy + 13, 1, GOLD)
    # Russia flag
    fx = cx + 22
    img.fill_rect(fx, fy, 28, 7, WHITE)
    img.fill_rect(fx, fy + 7, 28, 6, (0, 91, 172))
    img.fill_rect(fx, fy + 13, 28, 7, (213, 0, 50))
    # Round table below
    img.fill_ellipse(cx, cy + 30, 40, 9, (120, 85, 50))
    img.fill_rect(cx - 3, cy + 30, 6, 14, (120, 85, 50))
    img.fill_circle(cx - 26, cy + 20, 5, (27, 79, 114))
    img.fill_circle(cx, cy + 16, 5, (178, 34, 52))
    img.fill_circle(cx + 26, cy + 20, 5, (0, 91, 172))
    # Gold star above
    starburst(img, cx + 2, cy - 40, 7, 3, GOLD)


def icon_scales(img, cx, cy):
    dark = (70, 40, 30)
    img.fill_rect(cx - 26, cy + 32, 52, 6, dark)
    img.fill_rect(cx - 3, cy - 26, 6, 58, dark)
    img.fill_circle(cx, cy - 32, 5, dark)
    img.fill_rect(cx - 42, cy - 26, 84, 5, dark)
    for sx in (-38, 38):
        img.line(cx + sx, cy - 21, cx + sx - 12, cy + 4, dark)
        img.line(cx + sx, cy - 21, cx + sx + 12, cy + 4, dark)
        img.fill_triangle((cx + sx - 14, cy + 4), (cx + sx + 14, cy + 4), (cx + sx, cy + 18), (180, 140, 60))
    img.fill_rect(cx - 3, cy + 18, 6, 14, dark)


def icon_bridge(img, cx, cy):
    # Ukraine flag tag
    img.fill_rect(cx - 50, cy - 38, 24, 7, (0, 91, 172))
    img.fill_rect(cx - 50, cy - 31, 24, 7, (255, 213, 0))
    # Towers + deck
    slate = (60, 70, 85)
    img.fill_rect(cx - 44, cy - 8, 10, 48, slate)
    img.fill_rect(cx + 34, cy - 8, 10, 48, slate)
    img.fill_rect(cx - 52, cy + 30, 104, 7, slate)
    img.line(cx - 39, cy - 8, cx - 10, cy + 30, slate)
    img.line(cx + 39, cy - 8, cx + 10, cy + 30, slate)
    img.line(cx - 39, cy - 8, cx + 39, cy - 8, slate)
    # Water
    img.fill_rect(cx - 52, cy + 42, 104, 3, (70, 130, 180))
    # Smoke + explosion
    img.fill_circle(cx - 22, cy - 28, 8, (150, 150, 150))
    img.fill_circle(cx + 30, cy - 32, 6, (170, 170, 170))
    starburst(img, cx + 8, cy - 14, 14, 6, (230, 120, 20))
    img.fill_circle(cx + 8, cy - 14, 4, (255, 220, 60))


def icon_chart(img, cx, cy):
    # Grid + axes
    for gy in (cy - 20, cy, cy + 20):
        for x in range(cx - 46, cx + 46, 6):
            img.fill_rect(x, gy, 3, 1, (210, 210, 210))
    img.thick_line(cx - 46, cy - 32, cx - 46, cy + 32, (80, 80, 80), 2)
    img.thick_line(cx - 46, cy + 32, cx + 48, cy + 32, (80, 80, 80), 2)
    # Falling line
    pts = [(cx - 40, cy - 22), (cx - 20, cy - 12), (cx, cy - 2), (cx + 20, cy + 12), (cx + 40, cy + 24)]
    red = (192, 30, 30)
    for a, b in zip(pts, pts[1:]):
        img.thick_line(a[0], a[1], b[0], b[1], red, 3)
    for p in pts:
        img.fill_circle(p[0], p[1], 3, red)
    # Arrowhead
    img.fill_triangle((cx + 40, cy + 24), (cx + 30, cy + 20), (cx + 38, cy + 12), red)
    # Small green up-tick (Anthropic debut)
    img.thick_line(cx + 28, cy - 26, cx + 44, cy - 34, (30, 132, 73), 2)
    img.fill_triangle((cx + 44, cy - 34), (cx + 36, cy - 32), (cx + 42, cy - 26), (30, 132, 73))


def icon_tower(img, cx, cy):
    # Riyadh tower (tapered) + missile burst
    img.fill_poly([(cx - 18, cy + 42), (cx - 11, cy - 28), (cx + 11, cy - 28), (cx + 18, cy + 42)], (45, 90, 110))
    img.fill_poly([(cx - 11, cy - 28), (cx + 11, cy - 28), (cx + 4, cy - 36), (cx - 4, cy - 36)], (45, 90, 110))
    for row in range(6):
        for col in range(3):
            img.fill_rect(cx - 12 + col * 8, cy - 20 + row * 9, 5, 5, (180, 220, 235))
    img.fill_rect(cx - 52, cy + 42, 104, 4, (90, 90, 90))
    # Missile trail + burst
    img.line(cx + 48, cy - 44, cx + 14, cy - 18, (120, 120, 120))
    img.line(cx + 44, cy - 38, cx + 14, cy - 16, (180, 180, 180))
    img.fill_rect(cx + 44, cy - 46, 8, 3, (60, 60, 60))
    starburst(img, cx + 10, cy - 14, 15, 6, (230, 120, 20))
    img.fill_circle(cx + 10, cy - 14, 4, (255, 220, 60))


def icon_health(img, cx, cy):
    img.fill_circle(cx, cy, 36, WHITE)
    img.circle_outline(cx, cy, 36, (30, 132, 73), 3)
    img.fill_rect(cx - 9, cy - 24, 18, 48, (30, 132, 73))
    img.fill_rect(cx - 24, cy - 9, 48, 18, (30, 132, 73))
    # Check badge
    img.fill_circle(cx + 28, cy + 26, 13, GOLD)
    img.circle_outline(cx + 28, cy + 26, 13, (120, 95, 20), 2)
    img.thick_line(cx + 21, cy + 26, cx + 26, cy + 31, NAVY, 2)
    img.thick_line(cx + 26, cy + 31, cx + 36, cy + 19, NAVY, 2)


ICONS = {
    "summit": icon_summit,
    "scales": icon_scales,
    "bridge": icon_bridge,
    "chart": icon_chart,
    "tower": icon_tower,
    "health": icon_health,
}

# ------------------------------------------------------------ stories ----
STORIES = [
    {
        "num": "1", "icon": "summit",
        "tag": "DIPLOMACY | SHENZHEN, CHINA",
        "headline": "TRUMP, XI AND PUTIN MEET, SIGN PEACE PACT",
        "body": "First three-way summit ends with a 4-point declaration on nuclear risk, the UN, energy and the ICC. Ukraine and Iran not mentioned.",
        "fact": "70-MINUTE TALKS ON APEC SIDELINES",
        "accent": (27, 79, 114), "light": (235, 245, 251),
        "stat_big": "3", "stat_l1": "LEADERS", "stat_l2": "4-POINT PACT",
    },
    {
        "num": "2", "icon": "scales",
        "tag": "JUSTICE | THE HAGUE",
        "headline": "WORLD COURT: MYANMAR GUILTY OF GENOCIDE",
        "body": "ICJ rules 9-6 that Myanmar committed genocide against the Rohingya in 2017. A first: a state held responsible.",
        "fact": "CASE BROUGHT BY THE GAMBIA IN 2019",
        "accent": (123, 36, 28), "light": (253, 237, 236),
        "stat_big": "9-6", "stat_l1": "VOTE", "stat_l2": "1.3M DISPLACED",
    },
    {
        "num": "3", "icon": "bridge",
        "tag": "WAR IN UKRAINE | KYIV",
        "headline": "RUSSIAN STRIKES HIT KYIV BRIDGES, 8 KILLED",
        "body": "Missiles strike three Dnipro bridges, a cathedral and the Austrian and Dutch embassies. Fires burn.",
        "fact": "POLAND REPORTS AIRSPACE VIOLATION",
        "accent": (192, 57, 43), "light": (253, 242, 233),
        "stat_big": "8", "stat_l1": "KILLED", "stat_l2": "3 BRIDGES HIT",
    },
    {
        "num": "4", "icon": "chart",
        "tag": "MARKETS | NEW YORK / TOKYO",
        "headline": "STOCKS FALL AGAIN AS AI RALLY FADES",
        "body": "S&P 500 drops about 2%, its fifth straight loss. Nikkei falls 4.8%. Anthropic closes up 17% on debut.",
        "fact": "GOLD -4.2% | BRENT OIL $90.05",
        "accent": (146, 43, 33), "light": (249, 235, 234),
        "stat_big": "-4.8%", "stat_l1": "NIKKEI", "stat_l2": "S&P -2%",
    },
    {
        "num": "5", "icon": "tower",
        "tag": "MIDDLE EAST | RIYADH",
        "headline": "HOUTHI MISSILE HITS RIYADH TOWER",
        "body": "Missile damages the PIF tower in the financial district, blowing out windows on eight floors. No injuries.",
        "fact": "COALITION INTERCEPTS MISSILE, DRONES",
        "accent": (17, 122, 101), "light": (234, 250, 247),
        "stat_big": "8", "stat_l1": "FLOORS HIT", "stat_l2": "0 INJURED",
    },
    {
        "num": "6", "icon": "health",
        "tag": "HEALTH | NAIROBI, KENYA",
        "headline": "KENYA BEATS EBOLA, LAST PATIENT GOES HOME",
        "body": "Kenya discharges its last Ebola patient, 37 days after the first case. Officials credit fast tracing and preparation.",
        "fact": "PREPARATION, NOT LUCK, CREDITED",
        "accent": (30, 132, 73), "light": (234, 250, 241),
        "stat_big": "37", "stat_l1": "DAYS", "stat_l2": "LAST CASE OUT",
    },
]

FOOTER_BRIEFS = [
    ("IRAN WAR", "TRUMP: NO IRAN DECISION UNTIL 2027",
     "Senate blocks war limits 51-48. War cost put at $48.3bn."),
    ("EUROPE", "EU-UK SUMMIT IN BRUSSELS",
     "Youth mobility deal expected. Denmark approves Greenland pact."),
    ("CULTURE", "GTA 6 TOPS $2.3BN IN SALES",
     "Biggest entertainment launch ever, 13 years after GTA 5."),
    ("CLIMATE | COP31", "DRAFT DROPS FOSSIL FUELS",
     "No phase-out, no net-zero dates as talks enter final day."),
]


def draw_card(img, x0, y0, w, h, s):
    accent, light = s["accent"], s["light"]
    # Card body
    img.fill_rect(x0, y0, w, h, WHITE)
    img.rect_border(x0, y0, w, h, BORDER, 2)
    img.fill_rect(x0, y0, w, 10, accent)
    # Left icon panel
    px0, pw = x0, 120
    img.fill_rect(px0, y0 + 10, pw, h - 10, light)
    img.fill_rect(px0 + pw - 2, y0 + 10, 2, h - 10, accent)
    # Number badge
    img.fill_circle(px0 + 60, y0 + 30, 12, accent)
    img.draw_centered(px0 + 60, y0 + 23, s["num"], WHITE, 2, bold=True)
    # Icon
    ICONS[s["icon"]](img, px0 + 60, y0 + 84)
    # Stat block
    img.draw_centered(px0 + 60, y0 + 128, s["stat_big"], accent, 3, bold=True)
    img.draw_centered(px0 + 60, y0 + 156, s["stat_l1"], INK, 1, bold=True)
    img.draw_centered(px0 + 60, y0 + 168, s["stat_l2"], BODY, 1, bold=False)
    # Text column
    tx = x0 + 132
    tw = x0 + w - 12 - tx
    max2 = tw // 12  # chars per line at scale 2
    img.draw_text(tx, y0 + 20, s["tag"], accent, 1, bold=True)
    y = img.draw_wrapped(tx, y0 + 38, s["headline"], INK, 2, max2, 19, bold=True, max_lines=2)
    img.fill_rect(tx, y + 8, 48, 4, accent)
    img.draw_wrapped(tx, y + 20, s["body"], BODY, 2, max2, 18, bold=False, max_lines=5)
    # Fact bar
    img.fill_rect(tx, y0 + h - 36, tw, 24, light)
    img.draw_text(tx + 8, y0 + h - 29, s["fact"], accent, 1, bold=True)


def build():
    img = Img(W, H, PAPER)

    # ---- Masthead ----
    img.fill_rect(0, 0, W, 118, NAVY)
    # Globe (left)
    img.fill_circle(62, 59, 30, NAVY2)
    img.circle_outline(62, 59, 30, GOLD, 3)
    img.circle_outline(62, 59, 20, GOLD, 1)
    img.line(32, 59, 92, 59, GOLD)
    img.line(62, 29, 62, 89, GOLD)
    img.fill_ellipse(62, 59, 10, 30, NAVY2)
    img.circle_outline(62, 59, 30, GOLD, 2)
    # Title + date
    img.draw_centered(512, 24, "THE WORLD IN ONE DAY", WHITE, 4, bold=True)
    img.draw_centered(512, 62, "FRIDAY, 20 NOVEMBER 2026", GOLD, 3, bold=True)
    img.draw_centered(512, 94, "SIX LEAD STORIES FROM AROUND THE WORLD", (200, 210, 225), 1, bold=False)
    # Date badge (right)
    img.rect_border(920, 22, 80, 74, GOLD, 2)
    img.draw_centered(960, 28, "20", WHITE, 4, bold=True)
    img.draw_centered(960, 60, "NOV", GOLD, 2, bold=True)
    img.draw_centered(960, 80, "2026", WHITE, 1, bold=False)

    # ---- Ticker ----
    img.fill_rect(0, 118, W, 32, GOLD)
    img.draw_centered(512, 126, "SHENZHEN SUMMIT | ICJ RULING | KYIV | MARKETS | RIYADH | KENYA",
                      NAVY, 2, bold=True)

    # ---- Story grid: 2 cols x 3 rows ----
    cols_x = [16, 520]
    rows_y = [158, 402, 646]
    for i, s in enumerate(STORIES):
        draw_card(img, cols_x[i % 2], rows_y[i // 2], 488, 232, s)

    # ---- Footer: also today ----
    img.fill_rect(0, 892, W, 116, NAVY)
    img.fill_rect(0, 892, W, 4, GOLD)
    img.draw_text(16, 902, "ALSO TODAY", GOLD, 2, bold=True)
    col_w, gap = 236, 16
    for i, (tag, head, body) in enumerate(FOOTER_BRIEFS):
        cx = 16 + i * (col_w + gap)
        img.draw_text(cx, 926, tag, GOLD, 1, bold=True)
        y = img.draw_wrapped(cx, 938, head, WHITE, 1, col_w // 6, 10, bold=True, max_lines=2)
        img.draw_wrapped(cx, y + 2, body, LIGHTGRAY, 1, col_w // 6, 10, bold=False, max_lines=2)
    img.draw_centered(
        512, 992,
        "SOURCES: BBC, REUTERS, PBS, UN NEWS, CNBC, SKY NEWS, SCMP, JUST SECURITY, ONETURN",
        (150, 165, 190), 1, bold=False)
    return img


# ------------------------------------------------------------------ png ----
def _chunk(typ, data):
    return struct.pack(">I", len(data)) + typ + data + struct.pack(
        ">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def encode_png(img):
    ihdr = struct.pack(">IIBBBBB", img.w, img.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = img.w * 3
    for y in range(img.h):
        raw.append(0)  # filter: none
        raw += img.px[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", idat) + _chunk(b"IEND", b""))


def main():
    out = os.environ.get("MAKEFUN_OUTPUT", "/output/entry.png")
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    data = encode_png(build())
    with open(out, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (out, len(data)))


if __name__ == "__main__":
    main()
