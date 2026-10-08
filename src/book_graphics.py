"""
Dynamic vector-like PIL renderer for Book-shaped icons, floating widgets, and UI Option Logo badges.
"""

from PIL import Image, ImageDraw, ImageFilter
from src.theme import THEMES, DEFAULT_THEME


def hex_to_rgb(hex_str: str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def generate_book_image(
    size: int = 80,
    theme_name: str = DEFAULT_THEME,
    is_hovered: bool = False,
    is_open: bool = False
) -> Image.Image:
    """
    Renders a high-resolution book icon with 3D bevels, spine, page edges,
    gold-leaf corners, and a bookmark ribbon.
    """
    scale = 4
    canvas_size = size * scale
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    
    cover_rgb = hex_to_rgb(theme["book_cover"])
    spine_rgb = hex_to_rgb(theme["book_spine"])
    accent_rgb = hex_to_rgb(theme["book_accent"])
    ribbon_rgb = hex_to_rgb(theme["book_ribbon"])

    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    margin = int(canvas_size * 0.08)
    w = canvas_size - 2 * margin
    h = canvas_size - 2 * margin

    # Draw soft drop shadow or hover glow
    shadow_img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_img)
    shadow_box = [margin + 6, margin + 10, margin + w + 6, margin + h + 10]
    
    if is_hovered:
        glow_color = (*accent_rgb, 150)
        s_draw.rounded_rectangle([margin - 8, margin - 8, margin + w + 8, margin + h + 8], radius=24, fill=glow_color)
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=16))
    else:
        s_draw.rounded_rectangle(shadow_box, radius=20, fill=(0, 0, 0, 100))
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=12))

    img = Image.alpha_composite(img, shadow_img)
    draw = ImageDraw.Draw(img)

    bx0, by0 = margin, margin
    bx1, by1 = margin + w, margin + h

    # 1. Page Edges
    page_inset_x = int(w * 0.12)
    page_inset_y = int(h * 0.06)
    draw.rounded_rectangle(
        [bx0 + page_inset_x, by0 + page_inset_y, bx1 - 2, by1 - 4],
        radius=14,
        fill=(245, 240, 228, 255),
        outline=(200, 190, 175, 255),
        width=2 * scale
    )
    for i in range(1, 4):
        offset = i * (3 * scale)
        draw.line(
            [(bx1 - 4 - offset, by0 + page_inset_y + 8), (bx1 - 4 - offset, by1 - 8)],
            fill=(220, 210, 195, 200),
            width=scale
        )

    # 2. Main Book Cover
    cover_box = [bx0, by0, bx1 - int(w * 0.08), by1]
    draw.rounded_rectangle(
        cover_box,
        radius=18,
        fill=(*cover_rgb, 255),
        outline=(*spine_rgb, 255),
        width=2 * scale
    )

    # 3. Book Spine
    spine_width = int(w * 0.22)
    spine_box = [bx0, by0, bx0 + spine_width, by1]
    draw.rounded_rectangle(spine_box, radius=18, fill=(*spine_rgb, 255))
    draw.rectangle([bx0 + int(spine_width * 0.6), by0, bx0 + spine_width, by1], fill=(*spine_rgb, 255))

    num_ribs = 3
    for r in range(1, num_ribs + 1):
        ry = by0 + int(h * (r / (num_ribs + 1)))
        draw.line([(bx0 + 4, ry), (bx0 + spine_width - 2, ry)], fill=(*accent_rgb, 220), width=2 * scale)
        draw.line([(bx0 + 4, ry + 2 * scale), (bx0 + spine_width - 2, ry + 2 * scale)], fill=(0, 0, 0, 90), width=scale)

    # 4. Gold Corners
    corner_size = int(w * 0.18)
    cx_right = bx1 - int(w * 0.08)
    draw.polygon([(cx_right - corner_size, by0), (cx_right, by0), (cx_right, by0 + corner_size)], fill=(*accent_rgb, 240))
    draw.polygon([(cx_right - corner_size, by1), (cx_right, by1), (cx_right, by1 - corner_size)], fill=(*accent_rgb, 240))

    # 5. Hanging Bookmark Ribbon
    ribbon_x = bx0 + int(w * 0.52)
    ribbon_w = int(w * 0.16)
    ribbon_top = by0 - int(h * 0.04)
    ribbon_bottom = by1 + int(h * 0.14)
    ribbon_points = [
        (ribbon_x, ribbon_top),
        (ribbon_x + ribbon_w, ribbon_top),
        (ribbon_x + ribbon_w, ribbon_bottom),
        (ribbon_x + ribbon_w // 2, ribbon_bottom - int(h * 0.06)),
        (ribbon_x, ribbon_bottom)
    ]
    draw.polygon(ribbon_points, fill=(*ribbon_rgb, 255))
    draw.line([(ribbon_x + 2, ribbon_top), (ribbon_x + 2, ribbon_bottom)], fill=(255, 255, 255, 120), width=scale)

    # 6. Embossed Central Emblem
    emblem_cx = bx0 + spine_width + int((cx_right - (bx0 + spine_width)) / 2)
    emblem_cy = by0 + h // 2
    emblem_rad = int(w * 0.18)
    draw.ellipse(
        [emblem_cx - emblem_rad, emblem_cy - emblem_rad, emblem_cx + emblem_rad, emblem_cy + emblem_rad],
        outline=(*accent_rgb, 230),
        width=2 * scale
    )
    draw.polygon([
        (emblem_cx, emblem_cy - int(emblem_rad * 0.7)),
        (emblem_cx + int(emblem_rad * 0.6), emblem_cy),
        (emblem_cx, emblem_cy + int(emblem_rad * 0.7)),
        (emblem_cx - int(emblem_rad * 0.6), emblem_cy)
    ], fill=(*accent_rgb, 220))

    return img.resize((size, size), Image.Resampling.LANCZOS)


def _create_badge_base(size: int, theme_name: str, is_hovered: bool, badge_color_rgb):
    """Base circular logo badge with gold bezel and soft drop shadow/glow."""
    scale = 4
    canvas_size = size * scale
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    accent_rgb = hex_to_rgb(theme["book_accent"])
    
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    margin = int(canvas_size * 0.1)
    d = canvas_size - 2 * margin
    
    # Shadow/Glow
    shadow = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    if is_hovered:
        s_draw.ellipse([margin - 4, margin - 4, margin + d + 4, margin + d + 4], fill=(*accent_rgb, 170))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=14))
    else:
        s_draw.ellipse([margin + 4, margin + 6, margin + d + 4, margin + d + 6], fill=(0, 0, 0, 90))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=10))
        
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)
    
    # Outer Gold Bezel
    draw.ellipse([margin, margin, margin + d, margin + d], fill=(*accent_rgb, 255))
    
    # Inner Badge Disc
    inset = int(d * 0.08)
    draw.ellipse(
        [margin + inset, margin + inset, margin + d - inset, margin + d - inset],
        fill=(*badge_color_rgb, 255)
    )
    
    # Top highlight curve
    draw.arc(
        [margin + inset + 2, margin + inset + 2, margin + d - inset - 2, margin + d - inset - 2],
        start=200, end=340, fill=(255, 255, 255, 130), width=2 * scale
    )
    
    return img, draw, canvas_size, scale, margin, d, accent_rgb


def generate_note_logo(size: int = 56, theme_name: str = DEFAULT_THEME, is_hovered: bool = False) -> Image.Image:
    """Logo badge for 'Take Notes' (Parchment Journal & Quill)."""
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    badge_bg = hex_to_rgb(theme["book_cover"])
    img, draw, canvas_size, scale, margin, d, accent_rgb = _create_badge_base(size, theme_name, is_hovered, badge_bg)
    
    cx = canvas_size // 2
    cy = canvas_size // 2
    
    # Draw Notepad / Paper Sheet
    pw = int(d * 0.42)
    ph = int(d * 0.52)
    px0, py0 = cx - pw // 2 - int(d * 0.04), cy - ph // 2
    draw.rounded_rectangle([px0, py0, px0 + pw, py0 + ph], radius=6 * scale, fill=(250, 246, 235, 255), outline=(*accent_rgb, 240), width=scale)
    
    # Lines on note
    for i in range(3):
        ly = py0 + int(ph * (0.3 + i * 0.22))
        draw.line([(px0 + int(pw * 0.2), ly), (px0 + int(pw * 0.8), ly)], fill=(*badge_bg, 180), width=scale)
        
    # Draw Quill / Pen
    qx0 = px0 + int(pw * 0.65)
    qy0 = py0 - int(ph * 0.1)
    draw.polygon([
        (qx0, qy0),
        (qx0 + int(d * 0.25), qy0 + int(d * 0.35)),
        (qx0 + int(d * 0.2), qy0 + int(d * 0.38)),
        (qx0 - int(d * 0.05), qy0 + int(d * 0.1))
    ], fill=(*accent_rgb, 255))
    # Nib
    draw.polygon([
        (qx0 + int(d * 0.25), qy0 + int(d * 0.35)),
        (qx0 + int(d * 0.30), qy0 + int(d * 0.42)),
        (qx0 + int(d * 0.2), qy0 + int(d * 0.38))
    ], fill=(255, 255, 255, 240))

    return img.resize((size, size), Image.Resampling.LANCZOS)


def generate_reminder_logo(size: int = 56, theme_name: str = DEFAULT_THEME, is_hovered: bool = False) -> Image.Image:
    """Logo badge for 'Set Reminder' (Golden Alarm Clock)."""
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    badge_bg = hex_to_rgb(theme["book_spine"])
    img, draw, canvas_size, scale, margin, d, accent_rgb = _create_badge_base(size, theme_name, is_hovered, badge_bg)
    
    cx = canvas_size // 2
    cy = canvas_size // 2
    clock_rad = int(d * 0.24)
    
    # Clock Bells (top left & right)
    bell_r = int(clock_rad * 0.38)
    draw.ellipse([cx - clock_rad - bell_r // 2, cy - clock_rad - bell_r // 2, cx - clock_rad + bell_r // 2, cy - clock_rad + bell_r // 2], fill=(*accent_rgb, 255))
    draw.ellipse([cx + clock_rad - bell_r // 2, cy - clock_rad - bell_r // 2, cx + clock_rad + bell_r // 2, cy - clock_rad + bell_r // 2], fill=(*accent_rgb, 255))
    
    # Clock Feet
    draw.line([(cx - clock_rad + 4, cy + clock_rad - 2), (cx - clock_rad - 6, cy + clock_rad + 10)], fill=(*accent_rgb, 255), width=2 * scale)
    draw.line([(cx + clock_rad - 4, cy + clock_rad - 2), (cx + clock_rad + 6, cy + clock_rad + 10)], fill=(*accent_rgb, 255), width=2 * scale)
    
    # Clock Face
    draw.ellipse([cx - clock_rad, cy - clock_rad, cx + clock_rad, cy + clock_rad], fill=(255, 250, 240, 255), outline=(*accent_rgb, 255), width=2 * scale)
    
    # Clock Hands (10:10 position)
    draw.line([(cx, cy), (cx - int(clock_rad * 0.45), cy - int(clock_rad * 0.45))], fill=(*badge_bg, 255), width=2 * scale)
    draw.line([(cx, cy), (cx + int(clock_rad * 0.6), cy - int(clock_rad * 0.2))], fill=(*hex_to_rgb(theme["book_ribbon"]), 255), width=int(1.5 * scale))
    draw.ellipse([cx - 3 * scale, cy - 3 * scale, cx + 3 * scale, cy + 3 * scale], fill=(*accent_rgb, 255))

    return img.resize((size, size), Image.Resampling.LANCZOS)


def generate_library_logo(size: int = 56, theme_name: str = DEFAULT_THEME, is_hovered: bool = False) -> Image.Image:
    """Logo badge for 'Library Dashboard' (Grand Bookshelf & Grimoire)."""
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    badge_bg = hex_to_rgb(theme["bg_card"])
    img, draw, canvas_size, scale, margin, d, accent_rgb = _create_badge_base(size, theme_name, is_hovered, badge_bg)
    
    cx = canvas_size // 2
    cy = canvas_size // 2
    
    # Open Book Silhouette
    bw = int(d * 0.56)
    bh = int(d * 0.36)
    
    # Left page
    draw.polygon([
        (cx, cy + int(bh * 0.4)),
        (cx - int(bw * 0.5), cy + int(bh * 0.2)),
        (cx - int(bw * 0.5), cy - int(bh * 0.4)),
        (cx, cy - int(bh * 0.2))
    ], fill=(245, 240, 228, 255), outline=(*accent_rgb, 240))
    
    # Right page
    draw.polygon([
        (cx, cy + int(bh * 0.4)),
        (cx + int(bw * 0.5), cy + int(bh * 0.2)),
        (cx + int(bw * 0.5), cy - int(bh * 0.4)),
        (cx, cy - int(bh * 0.2))
    ], fill=(255, 250, 238, 255), outline=(*accent_rgb, 240))
    
    # Center binding
    draw.line([(cx, cy - int(bh * 0.25)), (cx, cy + int(bh * 0.45))], fill=(*hex_to_rgb(theme["book_ribbon"]), 255), width=2 * scale)
    
    # Bookshelf row underneath
    draw.rectangle([cx - int(bw * 0.45), cy + int(bh * 0.55), cx + int(bw * 0.45), cy + int(bh * 0.65)], fill=(*accent_rgb, 255))

    return img.resize((size, size), Image.Resampling.LANCZOS)


def generate_settings_logo(size: int = 56, theme_name: str = DEFAULT_THEME, is_hovered: bool = False) -> Image.Image:
    """Logo badge for 'Settings & Theme' (Golden Gear & Palette)."""
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    badge_bg = hex_to_rgb(theme["bg_secondary"])
    img, draw, canvas_size, scale, margin, d, accent_rgb = _create_badge_base(size, theme_name, is_hovered, badge_bg)
    
    cx = canvas_size // 2
    cy = canvas_size // 2
    gear_r = int(d * 0.24)
    
    # Gear Teeth
    import math
    num_teeth = 8
    for i in range(num_teeth):
        angle = i * (2 * math.pi / num_teeth)
        tx = cx + int((gear_r + 4 * scale) * math.cos(angle))
        ty = cy + int((gear_r + 4 * scale) * math.sin(angle))
        draw.ellipse([tx - 4 * scale, ty - 4 * scale, tx + 4 * scale, ty + 4 * scale], fill=(*accent_rgb, 255))
        
    # Gear Disc
    draw.ellipse([cx - gear_r, cy - gear_r, cx + gear_r, cy + gear_r], fill=(*accent_rgb, 255))
    # Gear Center Hole
    draw.ellipse([cx - int(gear_r * 0.45), cy - int(gear_r * 0.45), cx + int(gear_r * 0.45), cy + int(gear_r * 0.45)], fill=(*badge_bg, 255))

    return img.resize((size, size), Image.Resampling.LANCZOS)


def generate_tray_logo(size: int = 56, theme_name: str = DEFAULT_THEME, is_hovered: bool = False) -> Image.Image:
    """Logo badge for 'Minimize to Tray' (Bookmark Ribbon Pin)."""
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    badge_bg = hex_to_rgb(theme["bg_primary"])
    img, draw, canvas_size, scale, margin, d, accent_rgb = _create_badge_base(size, theme_name, is_hovered, badge_bg)
    
    cx = canvas_size // 2
    cy = canvas_size // 2
    rw = int(d * 0.26)
    rh = int(d * 0.46)
    
    rx0 = cx - rw // 2
    ry0 = cy - rh // 2
    
    ribbon_rgb = hex_to_rgb(theme["book_ribbon"])
    points = [
        (rx0, ry0),
        (rx0 + rw, ry0),
        (rx0 + rw, ry0 + rh),
        (cx, ry0 + int(rh * 0.75)),
        (rx0, ry0 + rh)
    ]
    draw.polygon(points, fill=(*ribbon_rgb, 255))
    draw.line([(rx0 + 2, ry0), (rx0 + 2, ry0 + rh)], fill=(255, 255, 255, 140), width=scale)
    # Gold head
    draw.rectangle([rx0 - 2 * scale, ry0, rx0 + rw + 2 * scale, ry0 + 4 * scale], fill=(*accent_rgb, 255))

    return img.resize((size, size), Image.Resampling.LANCZOS)


def generate_app_icon(size: int = 256) -> Image.Image:
    """Generates the master application icon."""
    return generate_book_image(size=size, theme_name=DEFAULT_THEME, is_hovered=False)
