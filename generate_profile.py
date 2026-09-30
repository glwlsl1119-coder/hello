"""Profile pictures (1080x1080, safe inside Instagram's circular crop) for each character.

Output: profile/profile_<name>.png (square upload) and profile/preview_<name>.png (circle crop).
"""
import os

from PIL import Image, ImageDraw

from generate_illustrated import (Cv, W, S, WHITE, mix, sparkle, heart, bear, cat, dog, PLUSH, GRID, BLOCK)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "profile")
SIZE = 1080


def finish(cv, name):
    sq = cv.im.crop((0, 0, W * S, W * S)).resize((SIZE, SIZE), Image.LANCZOS)
    sq.save(os.path.join(OUT, f"profile_{name}.png"), optimize=True)
    # preview how Instagram will crop it (circle) on a white page
    mask = Image.new("L", (SIZE * 2, SIZE * 2), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, SIZE * 2 - 1, SIZE * 2 - 1], fill=255)
    mask = mask.resize((SIZE, SIZE), Image.LANCZOS)
    page = Image.new("RGB", (SIZE, SIZE), WHITE)
    page.paste(sq, (0, 0), mask)
    page.resize((360, 360), Image.LANCZOS).save(os.path.join(OUT, f"preview_{name}.png"))


def backdrop(bg, acc):
    cv = Cv(bg)
    soft = mix(bg, WHITE, .5)
    cv.ell(200, 900, 380, 380, soft)
    cv.ell(900, 220, 300, 300, soft)
    sparkle(cv, 200, 250, 36, acc)
    sparkle(cv, 880, 330, 26, acc)
    heart(cv, 860, 800, 22, acc)
    heart(cv, 190, 640, 16, acc)
    return cv


def momo():
    bg, fur, light, dark, _txt, acc = PLUSH[0]
    cv = backdrop(bg, acc)
    bear(cv, 540, 400, 250, fur, dark, light, hug=mix(fur, WHITE, .4))
    finish(cv, "momo")


def miso():
    bg, _grid, _txt, acc, _auth, fur, _dfur, light = GRID[0]
    cv = backdrop(mix(bg, (255, 236, 205), .5), acc)
    cat(cv, 540, 470, 235, fur, (70, 50, 46), light)
    finish(cv, "miso")


def mochi():
    _bg, _dark, bub, _txt, tile, fur, dfur, light = BLOCK[0]
    cv = backdrop(bub, tile)
    dog(cv, 540, 470, 250, fur, dfur, light)
    finish(cv, "mochi")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    momo()
    miso()
    mochi()
    print("done ->", OUT)
