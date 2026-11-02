"""Generate procedural coffee images for the Kaffora Coffee demo site.

The originals are intentionally heavy (4K hero, 2400 px cards, JPEG q95, grain)
so Lighthouse's image-delivery and LCP insights have something real to flag.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(OUT, exist_ok=True)


def wood(w, h, base, seed):
    rnd = random.Random(seed)
    img = Image.new("RGB", (w, h), base)
    d = ImageDraw.Draw(img)
    for y in range(0, h, 3):
        wave = math.sin(y / h * 18 + rnd.random()) * 12
        shade = int(wave + rnd.randint(-10, 10))
        col = tuple(max(0, min(255, c + shade)) for c in base)
        d.line([(0, y), (w, y + rnd.randint(-4, 4))], fill=col, width=3)
    return img.filter(ImageFilter.GaussianBlur(1.2))


def bean(d, cx, cy, s, angle, col):
    pts = []
    for i in range(40):
        t = i / 40 * 2 * math.pi
        x, y = math.cos(t) * s, math.sin(t) * s * 0.68
        pts.append((cx + x * math.cos(angle) - y * math.sin(angle), cy + x * math.sin(angle) + y * math.cos(angle)))
    d.polygon(pts, fill=col)
    dark = tuple(max(0, c - 45) for c in col)
    x1, y1 = cx - s * 0.8 * math.cos(angle), cy - s * 0.8 * math.sin(angle)
    x2, y2 = cx + s * 0.8 * math.cos(angle), cy + s * 0.8 * math.sin(angle)
    d.line([(x1, y1), (cx + s * 0.1 * math.sin(angle), cy - s * 0.1 * math.cos(angle)), (x2, y2)], fill=dark, width=max(2, int(s / 7)))


def grain(img):
    noise = Image.effect_noise(img.size, 90).convert("RGB")
    return Image.blend(img, noise, 0.07)


def scatter_beans(d, w, h, n, seed, scale):
    rnd = random.Random(seed)
    for _ in range(n):
        bean(d, rnd.randint(0, w), rnd.randint(0, h), rnd.randint(int(28 * scale), int(44 * scale)),
             rnd.random() * math.pi, (rnd.randint(70, 105), rnd.randint(42, 60), rnd.randint(28, 40)))


def hero(name, w, h):
    img = wood(w, h, (150, 104, 70), 3)
    d = ImageDraw.Draw(img)
    scatter_beans(d, w, h, 160, 5, w / 2000)
    cx, cy, r = int(w * 0.6), int(h * 0.5), int(h * 0.36)
    d.ellipse([cx - r * 1.45 + 40, cy - r * 1.45 + 60, cx + r * 1.45 + 40, cy + r * 1.45 + 60], fill=(90, 60, 42))
    d.ellipse([cx - r * 1.45, cy - r * 1.45, cx + r * 1.45, cy + r * 1.45], fill=(242, 238, 230))
    d.ellipse([cx - r * 1.08, cy - r * 1.08, cx + r * 1.08, cy + r * 1.08], fill=(250, 248, 244))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 72, 40))
    d.ellipse([cx - r * 0.9, cy - r * 0.9, cx + r * 0.9, cy + r * 0.9], fill=(170, 110, 64))
    for i in range(6):  # latte-art heart rings
        rr = r * (0.62 - i * 0.09)
        d.ellipse([cx - rr, cy - rr * 0.85 - i * 12, cx + rr, cy + rr * 0.85 - i * 12],
                  fill=(236, 214, 186) if i % 2 == 0 else (178, 116, 68))
    d.rounded_rectangle([cx + r * 1.4, cy - r * 0.18, cx + r * 1.95, cy + r * 0.18], radius=int(r * 0.18), fill=(242, 238, 230))
    img = grain(img.filter(ImageFilter.GaussianBlur(0.8)))
    img.save(os.path.join(OUT, name), "JPEG", quality=95, subsampling=0)


def bag(name, w, h, bg, label, seed):
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(c * (1.05 - 0.25 * t)) for c in bg))
    scatter_beans(d, w, h, 70, seed, w / 1600)
    bw, bh = int(w * 0.34), int(h * 0.72)
    x0, y0 = (w - bw) // 2, int(h * 0.16)
    d.rounded_rectangle([x0 + 30, y0 + 40, x0 + bw + 30, y0 + bh + 40], radius=40, fill=(40, 30, 24))
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=40, fill=(34, 34, 38))
    d.rectangle([x0, y0, x0 + bw, y0 + 60], fill=(55, 55, 60))
    d.rounded_rectangle([x0 + bw * 0.12, y0 + bh * 0.32, x0 + bw * 0.88, y0 + bh * 0.78], radius=24, fill=label)
    for i in range(3):
        d.rectangle([x0 + bw * 0.2, y0 + bh * (0.42 + i * 0.1), x0 + bw * (0.8 - i * 0.12), y0 + bh * (0.45 + i * 0.1)], fill=(250, 246, 238))
    img = grain(img.filter(ImageFilter.GaussianBlur(0.7)))
    img.save(os.path.join(OUT, name), "JPEG", quality=95, subsampling=0)


if __name__ == "__main__":
    hero("hero-coffee-4k.jpg", 4000, 2667)
    bag("coffee-cerrado.jpg", 2400, 1600, (214, 170, 120), (196, 92, 44), 11)
    bag("coffee-yirgacheffe.jpg", 2400, 1600, (232, 212, 170), (218, 168, 48), 12)
    bag("coffee-huila.jpg", 2400, 1600, (190, 142, 118), (150, 44, 52), 13)
    # Wordmark, deliberately exported at 4x the size it is displayed (160x40).
    from PIL import ImageFont
    logo = Image.new("RGBA", (640, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(logo)
    d.ellipse([8, 16, 136, 144], fill=(228, 22, 155, 255))
    bean(d, 72, 80, 42, math.pi / 4, (255, 236, 250))
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 84)
    d.text((160, 30), "KAFFORA", font=font, fill=(255, 255, 255, 255))
    logo.save(os.path.join(OUT, "kaffora-logo.png"))
    for f in sorted(os.listdir(OUT)):
        print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, "KB")
