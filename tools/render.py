"""Render Instagram carousels (1080x1350 JPEG) from a JSON spec.

Usage: python3 tools/render.py spec.json carousels/
Spec: a list of {"slug", "slides": [...]} where each slide is one of
  ["cover", headline, subline]
  ["stake", sentence, null]
  ["idea", headline, body]
  ["recap", headline, [[label, value], ...]]
  ["cta", small, big, sub]   e.g. ["cta", "Comment", "DEMO", "..."] or ["cta", "Save this", "", "..."]
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H, M = 1080, 1350, 120
BG, FG, MUTED, ACC = "#0F1B2D", "#F5F7FA", "#9FB3C8", "#2EC4B6"
F = "/usr/share/fonts/opentype/inter/"
HANDLE = os.environ.get("IG_HANDLE", "@arsalkamran8086")
def HEAD(s): return ImageFont.truetype(F + "InterDisplay-Bold.otf", s)
def BODY(s): return ImageFont.truetype(F + "Inter-Regular.otf", s)
def SEMI(s): return ImageFont.truetype(F + "Inter-SemiBold.otf", s)

def wrap(d, text, f, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def block(d, y, text, f, color, gap=1.2):
    for line in wrap(d, text, f, W - 2 * M):
        d.text((M, y), line, font=f, fill=color); y += int(f.size * gap)
    return y

def fit(d, text, start, maker):
    s = start
    while d.textlength(text, font=maker(s)) > W - 2 * M and s > 60: s -= 6
    return maker(s)

def base(i, n):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([M, M - 40, M + 90, M - 30], fill=ACC)
    d.text((W - M, M - 52), f"{i}/{n}", font=SEMI(32), fill=MUTED, anchor="ra")
    d.text((M, H - M + 30), HANDLE, font=SEMI(32), fill=MUTED)
    if i < n: d.text((W - M, H - M + 30), "swipe →", font=SEMI(32), fill=ACC, anchor="ra")
    return im, d

def render(c, outdir):
    out = os.path.join(outdir, c["slug"]); os.makedirs(out, exist_ok=True)
    n = len(c["slides"]); files = []
    for i, s in enumerate(c["slides"], 1):
        im, d = base(i, n); kind = s[0]
        if kind == "cover":
            y = block(d, 360, s[1], HEAD(120), FG, 1.08)
            d.rectangle([M, y + 40, M + 160, y + 52], fill=ACC)
            block(d, y + 100, s[2], BODY(46), MUTED)
        elif kind == "stake":
            block(d, 420, s[1], HEAD(84), FG, 1.15)
        elif kind == "idea":
            y = block(d, 380, s[1], HEAD(88), ACC, 1.1)
            block(d, y + 60, s[2], BODY(48), FG, 1.4)
        elif kind == "recap":
            y = block(d, 300, s[1], HEAD(96), FG, 1.1) + 80
            for a, b in s[2]:
                y = block(d, y, a, SEMI(52), FG, 1.25)
                y = block(d, y, "→ " + b, BODY(48), ACC, 1.3) + 50
        elif kind == "cta":
            small, big, sub = s[1], s[2], s[3]
            y = 430
            if big:
                d.text((M, y), small, font=HEAD(110), fill=FG)
                d.text((M, y + 130), big, font=fit(d, big, 190, HEAD), fill=ACC)
                y += 380
            else:
                f = fit(d, small, 170, HEAD)
                d.text((M, y + 60), small, font=f, fill=ACC)
                y += 60 + f.size + 90
            block(d, y, sub, BODY(48), FG, 1.4)
        p = os.path.join(out, f"slide-{i:02d}.jpg"); im.save(p, quality=92); files.append(p)
    return files

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    for c in spec: print(c["slug"], len(render(c, sys.argv[2])))
