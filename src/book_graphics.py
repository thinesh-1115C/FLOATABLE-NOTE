"""
Dynamic vector-like PIL renderer for Book-shaped icons, floating widgets, and UI badges.
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
    # Supersampling factor for ultra-sharp anti-aliased rendering
    scale = 4
    canvas_size = size * scale
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    
    cover_rgb = hex_to_rgb(theme["book_cover"])
    spine_rgb = hex_to_rgb(theme["book_spine"])
    accent_rgb = hex_to_rgb(theme["book_accent"])
    ribbon_rgb = hex_to_rgb(theme["book_ribbon"])

    # Base image with transparency
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = int(canvas_size * 0.08)
    w = canvas_size - 2 * margin
    h = canvas_size - 2 * margin

    # Draw soft drop shadow or hover glow
    shadow_img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_img)

    shadow_box = [margin + 6, margin + 10, margin + w + 6, margin + h + 10]
    if is_hovered:
        # Golden / Accent aura glow on hover
        glow_color = (*accent_rgb, 140)
        s_draw.rounded_rectangle([margin - 8, margin - 8, margin + w + 8, margin + h + 8], radius=24, fill=glow_color)
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=16))
    else:
        # Ambient drop shadow
        s_draw.rounded_rectangle(shadow_box, radius=20, fill=(0, 0, 0, 100))
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=12))

    img = Image.alpha_composite(img, shadow_img)
    draw = ImageDraw.Draw(img)

    # Book Dimensions
    bx0, by0 = margin, margin
    bx1, by1 = margin + w, margin + h

    # 1. Right & Bottom Page Edges (Paper block)
    page_inset_x = int(w * 0.12)
    page_inset_y = int(h * 0.06)
    
    # Paper stack background
    draw.rounded_rectangle(
        [bx0 + page_inset_x, by0 + page_inset_y, bx1 - 2, by1 - 4],
        radius=14,
        fill=(245, 240, 228, 255),
        outline=(200, 190, 175, 255),
        width=2 * scale
    )
    # Page lines simulation
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

    # 3. Book Spine (Dark left band with stitching)
    spine_width = int(w * 0.22)
    spine_box = [bx0, by0, bx0 + spine_width, by1]
    draw.rounded_rectangle(
        spine_box,
        radius=18,
        fill=(*spine_rgb, 255)
    )
    # Mask right edge of spine radius so it blends into cover
    draw.rectangle(
        [bx0 + int(spine_width * 0.6), by0, bx0 + spine_width, by1],
        fill=(*spine_rgb, 255)
    )

    # Golden ribs / embossed bands across the spine
    num_ribs = 3
    for r in range(1, num_ribs + 1):
        ry = by0 + int(h * (r / (num_ribs + 1)))
        draw.line([(bx0 + 4, ry), (bx0 + spine_width - 2, ry)], fill=(*accent_rgb, 220), width=2 * scale)
        draw.line([(bx0 + 4, ry + 2 * scale), (bx0 + spine_width - 2, ry + 2 * scale)], fill=(0, 0, 0, 90), width=scale)

    # 4. Gold Corner Filigree / Accents
    corner_size = int(w * 0.18)
    cx_right = bx1 - int(w * 0.08)
    
    # Top-right gold bracket
    draw.polygon([
        (cx_right - corner_size, by0),
        (cx_right, by0),
        (cx_right, by0 + corner_size)
    ], fill=(*accent_rgb, 240))
    
    # Bottom-right gold bracket
    draw.polygon([
        (cx_right - corner_size, by1),
        (cx_right, by1),
        (cx_right, by1 - corner_size)
    ], fill=(*accent_rgb, 240))

    # 5. Hanging Bookmark Ribbon (Crimson / Accent)
    ribbon_x = bx0 + int(w * 0.52)
    ribbon_w = int(w * 0.16)
    ribbon_top = by0 - int(h * 0.04)
    ribbon_bottom = by1 + int(h * 0.14)
    
    # Ribbon body
    ribbon_points = [
        (ribbon_x, ribbon_top),
        (ribbon_x + ribbon_w, ribbon_top),
        (ribbon_x + ribbon_w, ribbon_bottom),
        (ribbon_x + ribbon_w // 2, ribbon_bottom - int(h * 0.06)),  # V-notch tail
        (ribbon_x, ribbon_bottom)
    ]
    draw.polygon(ribbon_points, fill=(*ribbon_rgb, 255))
    # Ribbon gold edge highlight
    draw.line([(ribbon_x + 2, ribbon_top), (ribbon_x + 2, ribbon_bottom)], fill=(255, 255, 255, 120), width=scale)

    # 6. Embossed Central Emblem (Book Title / Quill / Star)
    emblem_cx = bx0 + spine_width + int((cx_right - (bx0 + spine_width)) / 2)
    emblem_cy = by0 + h // 2
    emblem_rad = int(w * 0.18)

    # Emblem outer circle
    draw.ellipse(
        [emblem_cx - emblem_rad, emblem_cy - emblem_rad, emblem_cx + emblem_rad, emblem_cy + emblem_rad],
        outline=(*accent_rgb, 230),
        width=2 * scale
    )
    # Inner star / diamond
    draw.polygon([
        (emblem_cx, emblem_cy - int(emblem_rad * 0.7)),
        (emblem_cx + int(emblem_rad * 0.6), emblem_cy),
        (emblem_cx, emblem_cy + int(emblem_rad * 0.7)),
        (emblem_cx - int(emblem_rad * 0.6), emblem_cy)
    ], fill=(*accent_rgb, 220))

    # Downscale for smooth anti-aliasing
    final_img = img.resize((size, size), Image.Resampling.LANCZOS)
    return final_img


def generate_app_icon(size: int = 256) -> Image.Image:
    """Generates the master application icon."""
    return generate_book_image(size=size, theme_name=DEFAULT_THEME, is_hovered=False)

