"""Generate 30 Instagram quote images (1080x1350, 4:5) + captions CSV."""
import csv, os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
OUT = os.path.join(os.path.dirname(__file__), "quotes")
HANDLE = "@yourhandle"  # <- replace with your account name
F = "/usr/share/fonts/truetype/liberation/"
QUOTE_FONT = F + "LiberationSerif-BoldItalic.ttf"
AUTH_FONT = F + "LiberationSans-Bold.ttf"
SMALL_FONT = F + "LiberationSans-Regular.ttf"

# (bg_top, bg_bottom, text, accent)
PALETTES = [
    ((14, 16, 28), (34, 40, 70), (245, 240, 230), (232, 190, 110)),   # midnight
    ((244, 238, 226), (226, 214, 192), (38, 34, 30), (166, 86, 52)),  # paper
    ((20, 44, 40), (10, 24, 22), (238, 242, 232), (196, 224, 150)),   # forest
    ((60, 20, 28), (24, 8, 14), (250, 236, 232), (240, 150, 130)),    # wine
    ((18, 18, 18), (42, 42, 42), (250, 250, 250), (255, 214, 10)),    # mono
]

# (quote, author, source)  -- translations of ancient texts vary by edition
QUOTES = [
    ("The journey of a thousand miles begins with a single step.", "Lao Tzu", "Tao Te Ching, ch. 64"),
    ("Waste no more time arguing about what a good man should be. Be one.", "Marcus Aurelius", "Meditations, 10.16"),
    ("We suffer more often in imagination than in reality.", "Seneca", "Letters to Lucilius, 13"),
    ("It is not that we have a short time to live, but that we waste a lot of it.", "Seneca", "On the Shortness of Life, 1"),
    ("Nothing great was ever achieved without enthusiasm.", "Ralph Waldo Emerson", "Essays: Circles"),
    ("Advance confidently in the direction of your dreams, and endeavor to live the life you have imagined.", "Henry David Thoreau", "Walden (paraphrased from ch. 'Conclusion')"),
    ("The only thing we have to fear is fear itself.", "Franklin D. Roosevelt", "First Inaugural Address, 1933"),
    ("Courage was not the absence of fear, but the triumph over it.", "Nelson Mandela", "Long Walk to Freedom (paraphrased)"),
    ("To live is the rarest thing in the world. Most people exist, that is all.", "Oscar Wilde", "The Soul of Man under Socialism"),
    ("Never give in. Never, never, never, never.", "Winston Churchill", "Harrow School speech, 1941"),
    ("He who has a why to live can bear almost any how.", "Friedrich Nietzsche", "Twilight of the Idols"),
    ("People are disturbed not by things, but by the views they take of them.", "Epictetus", "Enchiridion, 5"),
    ("Fortune favors the bold.", "Virgil", "Aeneid, X"),
    ("Knowing yourself is true wisdom.", "Lao Tzu", "Tao Te Ching, ch. 33 (paraphrased)"),
    ("Trust thyself: every heart vibrates to that iron string.", "Ralph Waldo Emerson", "Self-Reliance"),
    ("The price of anything is the amount of life you exchange for it.", "Henry David Thoreau", "Walden, 'Economy'"),
    ("Life is either a daring adventure or nothing at all.", "Helen Keller", "The Open Door, 1957"),
    ("You must do the thing you think you cannot do.", "Eleanor Roosevelt", "You Learn by Living, 1960"),
    ("While we are postponing, life speeds by.", "Seneca", "Letters to Lucilius, 1"),
    ("What stands in the way becomes the way.", "Marcus Aurelius", "Meditations, 5.20 (paraphrased)"),
    ("I exist as I am, that is enough.", "Walt Whitman", "Song of Myself"),
    ("Well done is better than well said.", "Benjamin Franklin", "Poor Richard's Almanack"),
    ("In the midst of winter, I found there was, within me, an invincible summer.", "Albert Camus", "Return to Tipasa, 1952"),
    ("Nobody need wait a single moment before starting to improve the world.", "Anne Frank", "The Diary of a Young Girl (paraphrased)"),
    ("Stay hungry. Stay foolish.", "Steve Jobs", "Stanford commencement, 2005"),
    ("You could leave life right now. Let that determine what you do and say and think.", "Marcus Aurelius", "Meditations, 2.11"),
    ("Seize the day, trusting as little as possible in tomorrow.", "Horace", "Odes, 1.11"),
    ("Nothing can bring you peace but yourself.", "Ralph Waldo Emerson", "Self-Reliance"),
    ("Rather than love, than money, than fame, give me truth.", "Henry David Thoreau", "Walden, 'Where I Lived'"),
    ("Begin at once to live, and count each separate day as a separate life.", "Seneca", "Letters to Lucilius, 101"),
]
assert len(QUOTES) == 30

def gradient(top, bot):
    img = Image.new("RGB", (W, H))
    px = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        px.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return img

def fit(draw, text, max_w, max_h):
    for size in range(96, 38, -2):
        font = ImageFont.truetype(QUOTE_FONT, size)
        chars = max(8, int(max_w / (size * 0.47)))
        lines = textwrap.wrap(text, chars)
        while any(draw.textlength(l, font=font) > max_w for l in lines) and chars > 6:
            chars -= 1
            lines = textwrap.wrap(text, chars)
        lh = int(size * 1.25)
        if lh * len(lines) <= max_h:
            return font, lines, lh
    return font, lines, lh

def render(i, quote, author, pal):
    top, bot, fg, acc = pal
    img = gradient(top, bot)
    d = ImageDraw.Draw(img)
    # frame
    d.rectangle([40, 40, W - 40, H - 40], outline=acc, width=3)
    # big quote mark
    qm = ImageFont.truetype(QUOTE_FONT, 260)
    d.text((W // 2, 170), "“", font=qm, fill=acc, anchor="mm")
    # quote
    font, lines, lh = fit(d, quote, W - 240, 620)
    y = 330 + (620 - lh * len(lines)) // 2
    for l in lines:
        d.text((W // 2, y), l, font=font, fill=fg, anchor="mt")
        y += lh
    # divider + author
    d.line([(W // 2 - 60, 1040), (W // 2 + 60, 1040)], fill=acc, width=4)
    d.text((W // 2, 1085), author.upper(), font=ImageFont.truetype(AUTH_FONT, 38), fill=acc, anchor="mt")
    d.text((W // 2, 1255), HANDLE, font=ImageFont.truetype(SMALL_FONT, 30), fill=fg, anchor="mm")
    path = os.path.join(OUT, f"day{i:02d}.png")
    img.save(path, optimize=True)
    return path

HASH = "#quotes #motivation #inspiration #mindset #stoicism #wisdom #dailyquotes #selfgrowth"
def main():
    rows = []
    for n, (q, a, s) in enumerate(QUOTES, 1):
        render(n, q, a, PALETTES[(n - 1) % len(PALETTES)])
        cap = f"“{q}” — {a}\n\nSave this for when you need it. Share it with someone who does.\n\n{HASH}"
        rows.append([n, f"day{n:02d}.png", q, a, s, cap])
    with open(os.path.join(OUT, "captions.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["day", "image", "quote", "author", "source", "caption"])
        w.writerows(rows)
    print("done", len(rows))


if __name__ == "__main__":
    main()
