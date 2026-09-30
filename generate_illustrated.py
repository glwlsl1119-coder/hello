"""Illustrated Instagram quote images (1080x1350, 4:5) in three cute flat styles.

A  plush     - soft pastel background + fluffy teddy bear hugging a mini bear
B  grid      - grid-paper background, handwriting quote, doodles, peeking animal
C  block     - colour blocks, speech bubble, dog / cat / bear mascot

All characters are drawn from scratch with Pillow (no external artwork).
Optional handwriting fonts (Caveat, Patrick Hand) are used if present in ./fonts,
otherwise the script falls back to fonts installed on the system.
"""
import csv
import math
import os

from PIL import Image, ImageDraw, ImageFont

from generate import QUOTES, HANDLE, HASH

W, H, S = 1080, 1350, 2  # S = supersampling factor
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "quotes")
FONTDIR = os.path.join(HERE, "fonts")
SYS = "/usr/share/fonts/truetype/"


def first(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(paths)


HAND = first(os.path.join(FONTDIR, "Caveat.ttf"), os.path.join(FONTDIR, "PatrickHand.ttf"),
             SYS + "freefont/FreeSerifBoldItalic.ttf")
ROUND = first(os.path.join(FONTDIR, "PatrickHand.ttf"), SYS + "freefont/FreeSansBold.ttf")
BOLD = SYS + "freefont/FreeSansBold.ttf"
REAL_HAND = HAND.startswith(FONTDIR)
REAL_ROUND = ROUND.startswith(FONTDIR)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


WHITE = (255, 255, 255)

# Series cast (see PLAN.md). Plush style always features the bear with its baby.
NAMES = {"bear": "Momo", "cat": "Miso", "dog": "Mochi"}
GRID_ANIMALS = ["cat", "dog", "bear"]
BLOCK_ANIMALS = ["dog", "cat", "bear"]


def animal_for(i):
    """Which character appears on day i+1 (i is 0-based)."""
    style, v = i % 3, i // 3
    return ["bear", GRID_ANIMALS[v % 3], BLOCK_ANIMALS[v % 3]][style]


class Cv:
    """Canvas that takes 1080x1350 coordinates and draws at S x resolution."""

    def __init__(self, bg):
        self.im = Image.new("RGB", (W * S, H * S), bg)
        self.d = ImageDraw.Draw(self.im)

    @staticmethod
    def _b(cx, cy, rx, ry):
        return [(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S]

    def ell(self, cx, cy, rx, ry, fill, fuzz=False):
        if fuzz:  # ring of small circles -> fluffy plush edge
            r = max(3, min(rx, ry) * 0.09)
            n = int(2 * math.pi * max(rx, ry) / (r * 1.3))
            for i in range(n):
                a = 2 * math.pi * i / n
                x = cx + math.cos(a) * (rx - r * 0.4)
                y = cy + math.sin(a) * (ry - r * 0.4)
                self.d.ellipse(self._b(x, y, r, r), fill=fill)
        self.d.ellipse(self._b(cx, cy, rx, ry), fill=fill)

    def rr(self, x0, y0, x1, y1, r, fill):
        self.d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=int(r * S), fill=fill)

    def poly(self, pts, fill):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill)

    def line(self, pts, fill, width):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=max(1, int(width * S)), joint="curve")
        r = width / 2  # round caps
        for x, y in (pts[0], pts[-1]):
            self.ell(x, y, r, r, fill)

    def arc(self, cx, cy, rx, ry, a0, a1, fill, width):
        self.d.arc(self._b(cx, cy, rx, ry), a0, a1, fill=fill, width=max(1, int(width * S)))

    def text(self, x, y, s, font, fill, anchor="mt", stroke=0):
        self.d.text((x * S, y * S), s, font=font, fill=fill, anchor=anchor,
                    stroke_width=int(stroke * S), stroke_fill=fill)

    def length(self, s, font):
        return self.d.textlength(s, font=font) / S

    def save(self, path):
        self.im.resize((W, H), Image.LANCZOS).save(path, optimize=True)


def font(path, size):
    return ImageFont.truetype(path, int(size * S))


def wrap(cv, text, fpath, size, max_w):
    f = font(fpath, size)
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if cv.length(trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def fit(cv, text, fpath, max_w, max_h, hi, lo, lh=1.2):
    for size in range(hi, lo - 1, -2):
        lines = wrap(cv, text, fpath, size, max_w)
        f = font(fpath, size)
        if len(lines) * size * lh <= max_h and all(cv.length(l, f) <= max_w for l in lines):
            return size, lines
    return lo, wrap(cv, text, fpath, lo, max_w)


def draw_block(cv, lines, fpath, size, cx, y, fill, lh=1.2, stroke=0):
    f = font(fpath, size)
    for l in lines:
        cv.text(cx, y, l, f, fill, "mt", stroke)
        y += size * lh
    return y


# ---------------------------------------------------------------- decorations
def sparkle(cv, cx, cy, r, col):
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.28
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    cv.poly(pts, col)


def heart(cv, cx, cy, s, col):
    cv.ell(cx - s * .5, cy - s * .3, s * .55, s * .55, col)
    cv.ell(cx + s * .5, cy - s * .3, s * .55, s * .55, col)
    cv.poly([(cx - s * 1.02, cy - s * .05), (cx + s * 1.02, cy - s * .05), (cx, cy + s * 1.05)], col)


def bone(cv, cx, cy, length, col, ang):
    c, s = math.cos(ang), math.sin(ang)
    r = length * 0.13
    for sign in (-1, 1):
        ex, ey = cx + c * length / 2 * sign, cy + s * length / 2 * sign
        for off in (-1, 1):
            cv.ell(ex - s * r * off * .9, ey + c * r * off * .9, r, r, col)
    cv.line([(cx - c * length / 2, cy - s * length / 2), (cx + c * length / 2, cy + s * length / 2)], col, r * 1.9)


def swoosh(cv, x0, x1, y, amp, col, width):
    pts = []
    n = 40
    for i in range(n + 1):
        t = i / n
        pts.append((x0 + (x1 - x0) * t, y + math.sin(t * math.pi * 1.5) * amp * (1 - t * .6)))
    cv.line(pts, col, width)


def dashes(cv, cx, cy, r, col, width=5):
    for a in (-1.1, -0.5, 0.1):
        cv.line([(cx + math.cos(a - 1.57) * r * .6, cy + math.sin(a - 1.57) * r * .6),
                 (cx + math.cos(a - 1.57) * r, cy + math.sin(a - 1.57) * r)], col, width)


# ----------------------------------------------------------------- characters
def bear(cv, cx, cy, s, fur, dark, light, cheek=(255, 170, 180), fuzz=True, arms=True, hug=None):
    """cy = head centre; whole figure spans roughly cy-0.94s .. cy+2.9s."""
    by = cy + s * 1.75
    for sx in (-1, 1):  # legs
        cv.ell(cx + sx * s * .82, by + s * .72, s * .48, s * .42, fur, fuzz)
        cv.ell(cx + sx * s * .82, by + s * .78, s * .24, s * .2, light)
    cv.ell(cx, by, s * 1.08, s * 1.02, fur, fuzz)
    if not hug:
        cv.ell(cx, by + s * .1, s * .62, s * .62, light)
    for sx in (-1, 1):  # ears
        cv.ell(cx + sx * s * .78, cy - s * .78, s * .4, s * .4, fur, fuzz)
        cv.ell(cx + sx * s * .78, cy - s * .76, s * .22, s * .22, light)
    if hug:
        bear(cv, cx, by - s * .12, s * .36, hug, dark, light, cheek, fuzz=False, arms=False)
    if arms:
        for sx in (-1, 1):
            cv.ell(cx + sx * s * .66, by + s * .02, s * .3, s * .58, fur, fuzz)
    cv.ell(cx, cy, s, s * .94, fur, fuzz)  # head
    cv.ell(cx, cy + s * .3, s * .44, s * .34, light)
    cv.ell(cx, cy + s * .2, s * .16, s * .11, dark)
    cv.line([(cx, cy + s * .3), (cx, cy + s * .4)], dark, max(2, s * .03))
    cv.arc(cx - s * .12, cy + s * .38, s * .12, s * .09, 0, 180, dark, max(2, s * .03))
    cv.arc(cx + s * .12, cy + s * .38, s * .12, s * .09, 0, 180, dark, max(2, s * .03))
    for sx in (-1, 1):
        cv.ell(cx + sx * s * .38, cy - s * .08, s * .075, s * .09, dark)
        cv.ell(cx + sx * s * .365, cy - s * .11, s * .025, s * .03, WHITE)
        cv.ell(cx + sx * s * .6, cy + s * .22, s * .13, s * .09, cheek)


def cat(cv, cx, cy, s, fur, dark, light, cheek=(255, 170, 180), body=True):
    by = cy + s * 1.7
    stripe = mix(fur, dark, .3)
    if body:
        cv.line([(cx + s * .8, by + s * .6), (cx + s * 1.55, by + s * .3), (cx + s * 1.6, by - s * .6)], fur, s * .3)
        cv.ell(cx, by, s * .95, s * 1.0, fur)
        for sx in (-1, 1):
            cv.ell(cx + sx * s * .4, by + s * .88, s * .3, s * .2, light)
    for sx in (-1, 1):  # ears
        cv.poly([(cx + sx * s * 1.05, cy - s * .3), (cx + sx * s * .9, cy - s * 1.3), (cx + sx * s * .3, cy - s * .8)], fur)
        cv.poly([(cx + sx * s * .9, cy - s * .5), (cx + sx * s * .82, cy - s * 1.05), (cx + sx * s * .5, cy - s * .75)], cheek)
    cv.ell(cx, cy, s * 1.15, s * .95, fur)
    for k, dx in enumerate((-.22, 0, .22)):  # forehead stripes
        cv.line([(cx + dx * s, cy - s * .88), (cx + dx * s * 1.05, cy - s * (.62 if k == 1 else .68))], stripe, s * .07)
    cv.ell(cx, cy + s * .35, s * .5, s * .36, light)
    for sx in (-1, 1):
        cv.arc(cx + sx * s * .46, cy + s * .02, s * .17, s * .14, 200, 340, dark, s * .055)
        cv.ell(cx + sx * s * .72, cy + s * .3, s * .13, s * .09, cheek)
        for k in (-1, 0, 1):  # whiskers
            cv.line([(cx + sx * s * .55, cy + s * (.32 + k * .07)), (cx + sx * s * 1.12, cy + s * (.27 + k * .16))], mix(dark, fur, .4), max(2, s * .02))
    cv.poly([(cx - s * .1, cy + s * .2), (cx + s * .1, cy + s * .2), (cx, cy + s * .31)], cheek)
    cv.arc(cx - s * .1, cy + s * .36, s * .1, s * .08, 0, 180, dark, max(2, s * .03))
    cv.arc(cx + s * .1, cy + s * .36, s * .1, s * .08, 0, 180, dark, max(2, s * .03))


def dog(cv, cx, cy, s, fur, ear, light, dark=(66, 44, 40), collar=(232, 84, 72), body=True):
    by = cy + s * 1.65
    pink = (245, 140, 150)
    if body:
        cv.ell(cx, by, s * .9, s * 1.0, fur)
        for sx in (-1, 1):
            cv.ell(cx + sx * s * .42, by + s * .9, s * .3, s * .2, light)
    for sx in (-1, 1):  # floppy ears
        cv.ell(cx + sx * s * 1.0, cy + s * .08, s * .36, s * .78, ear)
    cv.ell(cx, cy, s * .98, s * .92, fur)
    cv.ell(cx - s * .48, cy - s * .18, s * .3, s * .3, ear)  # eye patch
    cv.ell(cx, cy + s * .32, s * .56, s * .42, light)
    cv.line([(cx, cy + s * .2), (cx, cy + s * .46)], dark, max(2, s * .03))
    cv.arc(cx - s * .14, cy + s * .46, s * .14, s * .1, 0, 180, dark, max(2, s * .03))
    cv.arc(cx + s * .14, cy + s * .46, s * .14, s * .1, 0, 180, dark, max(2, s * .03))
    cv.rr(cx - s * .11, cy + s * .52, cx + s * .11, cy + s * .82, s * .1, pink)  # tongue
    cv.ell(cx, cy + s * .16, s * .2, s * .14, dark)
    cv.ell(cx - s * .04, cy + s * .12, s * .05, s * .03, WHITE)
    for sx in (-1, 1):
        cv.ell(cx + sx * s * .38, cy - s * .12, s * .08, s * .1, dark)
        cv.ell(cx + sx * s * .365, cy - s * .15, s * .026, s * .03, WHITE)
    if body:
        cv.rr(cx - s * .6, cy + s * .88, cx + s * .6, cy + s * 1.1, s * .1, collar)
        cv.ell(cx, cy + s * 1.2, s * .12, s * .12, (255, 210, 70))


# --------------------------------------------------------------------- styles
PLUSH = [  # bg, fur, light, dark, text, accent
    ((222, 236, 250), (168, 204, 240), (214, 232, 250), (56, 68, 104), (52, 70, 108), (130, 170, 225)),
    ((252, 232, 237), (244, 188, 204), (253, 222, 230), (98, 60, 74), (110, 64, 84), (240, 140, 170)),
    ((251, 242, 224), (222, 184, 140), (244, 226, 200), (86, 58, 44), (96, 66, 48), (226, 160, 96)),
    ((224, 243, 233), (168, 220, 194), (214, 240, 226), (46, 84, 70), (48, 92, 76), (112, 196, 160)),
    ((237, 231, 250), (198, 184, 236), (226, 218, 248), (70, 56, 110), (78, 62, 124), (168, 148, 224)),
]


def style_plush(q, a, v):
    bg, fur, light, dark, txt, acc = PLUSH[v % len(PLUSH)]
    cv = Cv(bg)
    soft = mix(bg, WHITE, .55)
    cv.ell(120, 1180, 420, 420, soft)
    cv.ell(980, 260, 300, 300, soft)
    for (x, y, r) in ((130, 200, 30), (930, 150, 22), (960, 560, 18), (100, 620, 16)):
        sparkle(cv, x, y, r, acc)
    heart(cv, 890, 700, 20, acc)
    heart(cv, 170, 760, 14, acc)
    cv.text(W / 2, 62, HANDLE, font(ROUND, 28), mix(txt, bg, .35), "mt", 1 if REAL_ROUND else 0)
    stroke = 1.2 if REAL_ROUND else 0
    cv.text(W / 2, 108, "Momo & Pip say", font(BOLD, 32), acc, "mt")
    size, lines = fit(cv, q, ROUND, 820, 470, 90, 44, 1.22)
    y0 = 150 + (470 - size * 1.22 * len(lines)) / 2
    y = draw_block(cv, lines, ROUND, size, W / 2, y0, txt, 1.22, stroke)
    cv.text(W / 2, y + 14, "- " + a, font(ROUND, 38), acc, "mt", stroke)
    bear(cv, W / 2, 900, 135, fur, dark, light, hug=mix(fur, WHITE, .4))
    return cv


GRID = [  # bg, grid, text, accent, author, animal fur, ear/dark fur, light
    ((248, 250, 253), (222, 232, 245), (236, 168, 36), (250, 120, 110), (150, 120, 70), (240, 166, 84), (196, 110, 52), (255, 236, 205)),
    ((250, 249, 245), (232, 228, 214), (240, 132, 96), (120, 190, 170), (140, 100, 84), (196, 172, 150), (140, 108, 84), (245, 232, 218)),
    ((246, 250, 250), (214, 234, 236), (70, 150, 200), (255, 190, 90), (90, 120, 140), (176, 204, 240), (120, 150, 200), (232, 242, 252)),
]
def style_grid(q, a, v):
    bg, grid, txt, acc, auth, fur, dfur, light = GRID[v % len(GRID)]
    cv = Cv(bg)
    for x in range(0, W + 1, 40):
        cv.d.line([(x * S, 0), (x * S, H * S)], fill=grid, width=S * 2)
    for y in range(0, H + 1, 40):
        cv.d.line([(0, y * S), (W * S, y * S)], fill=grid, width=S * 2)
    cv.text(W / 2, 62, HANDLE, font(HAND, 40), mix(auth, bg, .3), "mt", 1 if REAL_HAND else 0)
    stroke = 1.6 if REAL_HAND else 0
    cv.text(W / 2, 118, NAMES[GRID_ANIMALS[v % 3]] + " says", font(HAND, 50), acc, "mt", stroke)
    hi = 120 if REAL_HAND else 84
    size, lines = fit(cv, q, HAND, 800, 600, hi, 46, 1.12)
    y0 = 190 + (600 - size * 1.12 * len(lines)) / 2
    y = draw_block(cv, lines, HAND, size, W / 2, y0, txt, 1.12, stroke)
    swoosh(cv, W * .28, W * .72, y + 26, 10, txt, 7)
    cv.text(W / 2, y + 64, "- " + a, font(HAND, 50), auth, "mt", 1 if REAL_HAND else 0)
    sparkle(cv, 70, 230, 30, acc)
    sparkle(cv, 1012, 470, 24, acc)
    sparkle(cv, 90, 930, 20, txt)
    heart(cv, 1000, 190, 16, acc)
    heart(cv, 62, 640, 14, acc)
    dashes(cv, 190, 130, 40, acc)
    dashes(cv, 960, 880, 36, txt)
    animal = GRID_ANIMALS[v % 3]
    cy = 1300
    if animal == "cat":
        cat(cv, W / 2, cy, 190, fur, (70, 50, 46), light, body=False)
    elif animal == "dog":
        dog(cv, W / 2, cy, 190, fur, dfur, light, body=False)
    else:
        bear(cv, W / 2, cy, 190, fur, (70, 50, 46), light, fuzz=True, arms=False)
    # paws on the bottom edge
    for sx in (-1, 1):
        cv.ell(W / 2 + sx * 190, H + 6, 78, 58, fur)
        cv.ell(W / 2 + sx * 190, H - 6, 34, 22, light)
    return cv


BLOCK = [  # bg, dark block, bubble, text, accent tile, animal fur, ear, light
    ((248, 235, 208), (92, 64, 54), (255, 208, 64), (86, 56, 44), (238, 96, 40), (240, 142, 62), (176, 96, 44), (255, 232, 200)),
    ((236, 244, 250), (48, 74, 112), (255, 214, 120), (44, 62, 98), (250, 140, 90), (230, 200, 160), (170, 130, 90), (252, 240, 220)),
    ((250, 232, 236), (110, 56, 78), (255, 224, 140), (100, 50, 64), (240, 110, 120), (196, 176, 240), (140, 120, 200), (240, 234, 252)),
]
def style_block(q, a, v):
    bg, dark, bub, txt, tile, fur, dfur, light = BLOCK[v % len(BLOCK)]
    cv = Cv(bg)
    cv.poly([(0, 800), (W, 560), (W, H), (0, H)], dark)
    cv.rr(880, -60, 1160, 220, 50, tile)  # corner tile
    cv.rr(-80, 300, 140, 520, 40, mix(bg, dark, .12))
    cv.text(W / 2, 46, HANDLE, font(BOLD, 26), mix(txt, bg, .3), "mt")
    cv.rr(84, 116, W - 84, 716, 64, bub)
    cv.poly([(440, 712), (560, 712), (500, 800)], bub)
    tag = NAMES[BLOCK_ANIMALS[v % 3]] + " says"
    tf = font(BOLD, 30)
    tw = cv.length(tag, tf) + 56
    cv.rr(120, 92, 120 + tw, 144, 26, dark)
    cv.text(120 + tw / 2, 118, tag, tf, bg, "mm")
    size, lines = fit(cv, q, BOLD, 780, 420, 80, 40, 1.22)
    y0 = 150 + (420 - size * 1.22 * len(lines)) / 2
    y = draw_block(cv, lines, BOLD, size, W / 2, y0, txt, 1.22)
    cv.text(W / 2, y + 14, "- " + a, font(BOLD, 34), mix(txt, bub, .25), "mt")
    bone(cv, 170, 900, 150, light, -.5)
    bone(cv, 930, 1060, 130, light, .6)
    heart(cv, 120, 1120, 18, tile)
    sparkle(cv, 900, 900, 24, bub)
    sparkle(cv, 210, 1000, 18, bub)
    animal = BLOCK_ANIMALS[v % 3]
    cy = 930
    if animal == "dog":
        dog(cv, W / 2, cy, 145, fur, dfur, light)
    elif animal == "cat":
        cat(cv, W / 2, cy, 145, fur, (70, 50, 46), light)
    else:
        bear(cv, W / 2, cy, 130, fur, (70, 50, 46), light)
    return cv


STYLES = [style_plush, style_grid, style_block]


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for n, (q, a, src) in enumerate(QUOTES, 1):
        i = n - 1
        STYLES[i % 3](q, a, i // 3).save(os.path.join(OUT, f"day{n:02d}.png"))
        who = "Momo & Pip" if animal_for(i) == "bear" else NAMES[animal_for(i)]
        who_tag = "Momo" if animal_for(i) == "bear" else NAMES[animal_for(i)]
        cap = (f"{who} say{'' if ' & ' in who else 's'}: “{q}” — {a}\n\n"
               f"Save this for when you need it. Share it with someone who does.\n\n"
               f"{HASH} #{who_tag}AndFriends")
        rows.append([n, f"day{n:02d}.png", who, q, a, src, cap])
    with open(os.path.join(OUT, "captions.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["day", "image", "character", "quote", "author", "source", "caption"])
        w.writerows(rows)
    print("done", len(QUOTES), "| handwriting font:", os.path.basename(HAND))


if __name__ == "__main__":
    main()
