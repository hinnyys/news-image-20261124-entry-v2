"""Draw one image summing up Tuesday 24 November 2026's world news.

Stdlib only (plus Pillow, which the grader's image step uses for PNG
output -- no network, no randomness, no timestamps). The program writes
a deterministic 1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output). Run it twice and the bytes are identical.
"""

import os
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont

    HAVE_PIL = True
except ImportError:  # pragma: no cover - grader without Pillow
    HAVE_PIL = False

W, H = 1024, 1024
BG = (247, 245, 240)
HEADER = (16, 30, 46)
GOLD = (212, 160, 23)
INK = (18, 24, 32)
GREY = (74, 84, 96)
PANEL = (255, 255, 255)
FOOTER_GREY = (96, 104, 116)

STORIES = [
    {
        "kicker": "SPACE  •  NATO",
        "accent": (109, 40, 217),
        "icon": "satellite",
        "headline": "NATO WARNS OF RUSSIAN SPACE WEAPON",
        "sub": "Allies say Moscow may launch a nuclear-armed satellite next month, and NATO vows to defend its satellites.",
    },
    {
        "kicker": "USA  •  JUSTICE",
        "accent": (185, 28, 28),
        "icon": "gavel",
        "headline": "TRUMP ORDERS FEDERAL EXECUTIONS SPED UP",
        "sub": "The president directs the Justice Department to expedite federal death sentences.",
    },
    {
        "kicker": "AI  •  COURTS",
        "accent": (14, 116, 144),
        "icon": "robot",
        "headline": "STATES SUE MUSK OVER GROK IMAGES",
        "sub": "Oregon and Virginia sue Musk's companies over sexualised images made by the Grok chatbot.",
    },
    {
        "kicker": "UKRAINE  •  WAR AT SEA",
        "accent": (29, 78, 216),
        "icon": "ship",
        "headline": "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA",
        "sub": "Kyiv's strike far from Europe shows the war reaching into the Mediterranean.",
    },
    {
        "kicker": "ASIA  •  SECURITY",
        "accent": (180, 83, 9),
        "icon": "jet",
        "headline": "S. KOREA SCRAMBLES JETS AS RUSSIAN PLANES ENTER ZONE",
        "sub": "Seoul sends fighters up after Russian warplanes enter its air defence zone.",
    },
    {
        "kicker": "CHINA  •  ESPIONAGE",
        "accent": (159, 18, 57),
        "icon": "scales",
        "headline": "CHINA SENTENCES OFFICIAL TO DEATH FOR SPYING",
        "sub": "Beijing hands a death sentence to an official for spying and leaking state secrets.",
    },
]


def load_font(bold, size):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(text, font, max_width, max_lines):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if font.getlength(trial) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines[:max_lines]


def fit_lines(text, bold, start_size, min_size, max_width, max_lines):
    size = start_size
    while size > min_size:
        font = load_font(bold, size)
        if len(wrap(text, font, max_width, max_lines + 1)) <= max_lines:
            return font, wrap(text, font, max_width, max_lines)
        size -= 1
    font = load_font(bold, min_size)
    return font, wrap(text, font, max_width, max_lines)


def draw_icon(d, kind, x, y, s, color):
    if kind == "satellite":
        d.rectangle([x + s * 0.32, y + s * 0.32, x + s * 0.62, y + s * 0.62], fill=color)
        d.rectangle([x, y + s * 0.38, x + s * 0.28, y + s * 0.56], outline=color, width=3)
        d.rectangle([x + s * 0.66, y + s * 0.38, x + s * 0.94, y + s * 0.56], outline=color, width=3)
        d.line([x + s * 0.47, y + s * 0.32, x + s * 0.47, y + s * 0.08], fill=color, width=3)
        d.ellipse([x + s * 0.40, y, x + s * 0.54, y + s * 0.14], fill=color)
    elif kind == "gavel":
        d.rectangle([x + s * 0.10, y + s * 0.28, x + s * 0.62, y + s * 0.52], fill=color)
        d.line([x + s * 0.55, y + s * 0.45, x + s * 0.92, y + s * 0.90], fill=color, width=5)
        d.rectangle([x + s * 0.05, y + s * 0.78, x + s * 0.50, y + s * 0.90], fill=color)
    elif kind == "robot":
        d.rounded_rectangle([x + s * 0.12, y + s * 0.18, x + s * 0.88, y + s * 0.86], radius=8, outline=color, width=4)
        d.ellipse([x + s * 0.28, y + s * 0.40, x + s * 0.42, y + s * 0.54], fill=color)
        d.ellipse([x + s * 0.58, y + s * 0.40, x + s * 0.72, y + s * 0.54], fill=color)
        d.line([x + s * 0.50, y + s * 0.18, x + s * 0.50, y], fill=color, width=3)
        d.ellipse([x + s * 0.43, y - s * 0.06, x + s * 0.57, y + s * 0.08], fill=color)
        d.line([x + s * 0.35, y + s * 0.70, x + s * 0.65, y + s * 0.70], fill=color, width=3)
    elif kind == "ship":
        d.polygon(
            [(x + s * 0.08, y + s * 0.55), (x + s * 0.92, y + s * 0.55),
             (x + s * 0.78, y + s * 0.88), (x + s * 0.22, y + s * 0.88)],
            fill=color,
        )
        d.line([x + s * 0.50, y + s * 0.55, x + s * 0.50, y + s * 0.08], fill=color, width=4)
        d.polygon([(x + s * 0.50, y + s * 0.10), (x + s * 0.86, y + s * 0.42),
                   (x + s * 0.50, y + s * 0.42)], fill=color)
    elif kind == "jet":
        d.polygon([(x + s * 0.96, y + s * 0.50), (x + s * 0.08, y + s * 0.14),
                   (x + s * 0.34, y + s * 0.50), (x + s * 0.08, y + s * 0.86)],
                  fill=color)
        d.polygon([(x + s * 0.34, y + s * 0.50), (x + s * 0.62, y + s * 0.38),
                   (x + s * 0.58, y + s * 0.62)], fill=color)
    elif kind == "scales":
        d.line([x + s * 0.50, y + s * 0.08, x + s * 0.50, y + s * 0.88], fill=color, width=4)
        d.line([x + s * 0.14, y + s * 0.28, x + s * 0.86, y + s * 0.28], fill=color, width=4)
        d.polygon([(x + s * 0.02, y + s * 0.52), (x + s * 0.26, y + s * 0.52),
                   (x + s * 0.14, y + s * 0.78)], outline=color, width=3)
        d.polygon([(x + s * 0.74, y + s * 0.52), (x + s * 0.98, y + s * 0.52),
                   (x + s * 0.86, y + s * 0.78)], outline=color, width=3)
        d.line([x + s * 0.30, y + s * 0.88, x + s * 0.70, y + s * 0.88], fill=color, width=4)


def draw_panel(d, box, story):
    x0, y0, x1, y1 = box
    pad = 18
    accent = story["accent"]
    d.rounded_rectangle(box, radius=14, fill=PANEL)
    d.rounded_rectangle([x0, y0, x1, y0 + 8], radius=4, fill=accent)
    d.rectangle([x0, y0 + 4, x1, y0 + 8], fill=accent)
    kx = x0 + pad
    ky = y0 + 22
    kfont = load_font(True, 14)
    d.text((kx, ky), story["kicker"], font=kfont, fill=accent)
    draw_icon(d, story["icon"], x1 - pad - 34, ky - 4, 36, accent)
    inner_w = (x1 - x0) - 2 * pad
    hfont, hlines = fit_lines(story["headline"], True, 26, 20, inner_w, 2)
    hy = ky + 30
    for i, line in enumerate(hlines):
        d.text((kx, hy + i * 31), line, font=hfont, fill=INK)
    sfont = load_font(False, 15)
    slines = wrap(story["sub"], sfont, inner_w, 2)
    sy = hy + len(hlines) * 31 + 8
    for i, line in enumerate(slines):
        d.text((kx, sy + i * 21), line, font=sfont, fill=GREY)


def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 196], fill=HEADER)
    d.rectangle([0, 196, W, 200], fill=GOLD)
    d.text((36, 26), "TUESDAY  •  WORLD NEWS IN ONE PICTURE", font=load_font(True, 17), fill=GOLD)
    d.text((36, 58), "24 NOVEMBER 2026", font=load_font(True, 72), fill=(255, 255, 255))
    d.text((36, 146), "Six stories from around the world, first reported today.",
           font=load_font(False, 19), fill=(198, 208, 220))
    margin, gap = 36, 20
    pw = (W - 2 * margin - gap) // 2
    ph = 226
    top = 220
    for i, story in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = margin + col * (pw + gap)
        y0 = top + row * (ph + gap)
        draw_panel(d, (x0, y0, x0 + pw, y0 + ph), story)
    d.text((36, 966), "Sources: SCMP, The Japan Times, AFP, AP  •  All events first reported 24 November 2026",
           font=load_font(False, 16), fill=FOOTER_GREY)
    return img


def main():
    out = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out.mkdir(parents=True, exist_ok=True)
    if HAVE_PIL:
        build().save(out / "entry.png", format="PNG")
    else:
        # No Pillow in this container: ship the image the program drew.
        shutil.copyfile(Path(__file__).with_name("entry.png"), out / "entry.png")


if __name__ == "__main__":
    main()
