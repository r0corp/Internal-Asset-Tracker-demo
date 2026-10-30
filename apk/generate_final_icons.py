from PIL import Image, ImageDraw, ImageFont
import os

SRC = "apk/app-icon-source.png"
logo = Image.open(SRC).convert("RGBA")


def clean_transparent_noise(img, alpha_threshold=8):
    # Source file has near-zero-alpha pixels carrying random leftover
    # RGB noise (classic un-premultiplied-alpha export artifact) - on
    # its own it's invisible, but resizing interpolates those stray
    # colors into visible speckle near the artwork's edges. Flatten
    # anything below the threshold to clean transparent white so any
    # residual blending fringes white (invisible on our white bg)
    # instead of random noise.
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a <= alpha_threshold:
                px[x, y] = (255, 255, 255, 0)
    return img


logo = clean_transparent_noise(logo)

VERSION_TEXT = "v4"
RES_DIR = "apk/android/app/src/main/res"

# (folder, legacy icon px, adaptive foreground px)
DENSITIES = [
    ("mipmap-mdpi", 48, 108),
    ("mipmap-hdpi", 72, 162),
    ("mipmap-xhdpi", 96, 216),
    ("mipmap-xxhdpi", 144, 324),
    ("mipmap-xxxhdpi", 192, 432),
]

BG_COLOR = (255, 255, 255, 255)
CHIP_COLOR = (11, 18, 32, 235)
CHIP_TEXT_COLOR = (255, 255, 255, 255)


def try_font(px):
    try:
        return ImageFont.truetype("arialbd.ttf", px)
    except Exception:
        return ImageFont.load_default()


def draw_logo_on(canvas, logo_scale):
    size = int(canvas.width * logo_scale)
    resized = logo.resize((size, size), Image.LANCZOS)
    pos = ((canvas.width - size) // 2, (canvas.height - size) // 2)
    canvas.paste(resized, pos, resized)


def draw_chip(canvas):
    w, h = canvas.size
    chip_w = int(w * 0.1875)   # matches 96/512 ratio chosen ("R")
    chip_h = int(h * 0.140625)  # matches 72/512 ratio
    radius = int(w * 0.035)     # matches 18/512 ratio

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    margin = max(4, int(w * 0.035))
    x1, y1 = w - chip_w, h - chip_h
    x0, y0 = w + margin, h + margin
    draw.rounded_rectangle((x1, y1, x0, y0), radius=radius, fill=CHIP_COLOR)
    out = Image.alpha_composite(canvas, overlay)

    draw2 = ImageDraw.Draw(out)
    font_px = max(10, int(chip_h * 0.52))
    font = try_font(font_px)
    bbox = draw2.textbbox((0, 0), VERSION_TEXT, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = w - chip_w / 2 - tw / 2 - bbox[0]
    ty = h - chip_h / 2 - th / 2 - bbox[1]
    draw2.text((tx, ty), VERSION_TEXT, font=font, fill=CHIP_TEXT_COLOR)
    return out


def rounded_mask(size, radius_ratio=0.22):
    w, h = size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    radius = int(min(w, h) * radius_ratio)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    return mask


def make_legacy(px):
    canvas = Image.new("RGBA", (px, px), BG_COLOR)
    draw_logo_on(canvas, 0.58)
    canvas = draw_chip(canvas)
    mask = rounded_mask((px, px))
    out = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask)
    return out


def make_round(px):
    canvas = Image.new("RGBA", (px, px), BG_COLOR)
    draw_logo_on(canvas, 0.52)
    canvas = draw_chip(canvas)
    mask = Image.new("L", (px, px), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, px - 1, px - 1), fill=255)
    out = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask)
    return out


def make_foreground(px):
    # Mirrors the legacy icon's content (white bg + logo + version chip)
    # exactly, so the chip is still visible on the adaptive-icon path
    # that most modern Android launchers actually use. Corner content
    # can get clipped on strictly-circular icon themes - accepted
    # trade-off per explicit user decision.
    canvas = Image.new("RGBA", (px, px), BG_COLOR)
    draw_logo_on(canvas, 0.58)
    canvas = draw_chip(canvas)
    return canvas


for folder, legacy_px, fg_px in DENSITIES:
    out_dir = os.path.join(RES_DIR, folder)
    os.makedirs(out_dir, exist_ok=True)

    make_legacy(legacy_px).save(os.path.join(out_dir, "ic_launcher.png"))
    make_round(legacy_px).save(os.path.join(out_dir, "ic_launcher_round.png"))
    make_foreground(fg_px).save(os.path.join(out_dir, "ic_launcher_foreground.png"))

    print(f"{folder}: ic_launcher {legacy_px}px, foreground {fg_px}px")

print("done")
