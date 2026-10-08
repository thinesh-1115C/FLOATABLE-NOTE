"""
Theme and visual styling definitions for the Book-Shaped Notes & Reminders Application.
"""

# Color Palettes
THEMES = {
    "Classic Leather": {
        "bg_primary": "#1E1A17",
        "bg_secondary": "#2A241F",
        "bg_card": "#382F28",
        "book_cover": "#8B4513",
        "book_spine": "#5C2C16",
        "book_accent": "#D4AF37",  # Gold
        "book_ribbon": "#B22222",  # Crimson Ribbon
        "page_bg": "#FBF5E8",      # Parchment
        "page_lines": "#E3D5C0",
        "text_primary": "#FFFFFF",
        "text_secondary": "#C8B89E",
        "text_page": "#2C221E",
        "accent": "#E69A3B",
        "accent_hover": "#F5AD56",
        "success": "#4CAF50",
        "danger": "#E53935",
        "warning": "#FFA726",
    },
    "Midnight Blue": {
        "bg_primary": "#0F172A",
        "bg_secondary": "#1E293B",
        "bg_card": "#334155",
        "book_cover": "#1E3A8A",
        "book_spine": "#172554",
        "book_accent": "#38BDF8",  # Ice Blue
        "book_ribbon": "#6366F1",  # Indigo Ribbon
        "page_bg": "#F8FAFC",
        "page_lines": "#E2E8F0",
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "text_page": "#0F172A",
        "accent": "#38BDF8",
        "accent_hover": "#7DD3FC",
        "success": "#10B981",
        "danger": "#EF4444",
        "warning": "#F59E0B",
    },
    "Emerald Library": {
        "bg_primary": "#0B1D16",
        "bg_secondary": "#132E24",
        "bg_card": "#1D4335",
        "book_cover": "#0F5132",
        "book_spine": "#083320",
        "book_accent": "#E5C07B",  # Antique Gold
        "book_ribbon": "#DC3545",  # Ruby Ribbon
        "page_bg": "#F7FBF8",
        "page_lines": "#D5E6DC",
        "text_primary": "#FFFFFF",
        "text_secondary": "#A3CFBB",
        "text_page": "#102A1E",
        "accent": "#20C997",
        "accent_hover": "#38D9A9",
        "success": "#28A745",
        "danger": "#DC3545",
        "warning": "#FFC107",
    },
    "Royal Velvet": {
        "bg_primary": "#1A1028",
        "bg_secondary": "#28193D",
        "bg_card": "#3D265C",
        "book_cover": "#4C1D95",
        "book_spine": "#2E1065",
        "book_accent": "#FDE047",  # Bright Gold
        "book_ribbon": "#EC4899",  # Rose Ribbon
        "page_bg": "#FAF5FF",
        "page_lines": "#E9D5FF",
        "text_primary": "#FAF5FF",
        "text_secondary": "#C084FC",
        "text_page": "#1E1B4B",
        "accent": "#A855F7",
        "accent_hover": "#C084FC",
        "success": "#22C55E",
        "danger": "#F43F5E",
        "warning": "#EAB308",
    }
}

NOTE_CATEGORIES = [
    {"name": "General", "color": "#D4AF37", "icon": "📝"},
    {"name": "Ideas", "color": "#A855F7", "icon": "💡"},
    {"name": "Work", "color": "#38BDF8", "icon": "💼"},
    {"name": "Personal", "color": "#10B981", "icon": "🏠"},
    {"name": "Urgent", "color": "#EF4444", "icon": "⚡"},
    {"name": "Study", "color": "#F59E0B", "icon": "🎓"},
]

DEFAULT_THEME = "Classic Leather"
DEFAULT_OPACITY = 0.95
DEFAULT_ICON_SIZE = 72

