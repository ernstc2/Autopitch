"""Big 4 visual constants — single source of truth for all chart and deck styling."""
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

# --- python-pptx RGBColor constants (for deck.py shapes and text) ---
NAVY       = RGBColor(0x00, 0x2B, 0x49)   # #002B49 Deloitte navy
TEAL       = RGBColor(0x00, 0x83, 0x8A)   # #00838A accent teal
LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2)   # #F2F2F2 background/secondary
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
DARK_GRAY  = RGBColor(0x40, 0x40, 0x40)   # #404040 body text

# --- Matplotlib hex strings (for charts.py bar/line colors) ---
NAVY_HEX       = "#002B49"
TEAL_HEX       = "#00838A"
LIGHT_GRAY_HEX = "#F2F2F2"
DARK_GRAY_HEX  = "#404040"
POSITIVE_HEX   = TEAL_HEX     # waterfall positive bars
NEGATIVE_HEX   = "#C0392B"    # waterfall negative bars (red-orange)

# --- Font names ---
FONT_HEADING = "Calibri"
FONT_BODY    = "Calibri"

# --- Slide geometry: 16:9 widescreen ---
SLIDE_W = Inches(13.33)   # 12192000 EMU
SLIDE_H = Inches(7.5)     # 6858000 EMU

# --- Layout zones (inches from top-left) ---
HEADER_TOP    = Inches(0)
HEADER_HEIGHT = Inches(1.1)
CONTENT_TOP   = Inches(1.25)
CONTENT_LEFT  = Inches(0.5)
CONTENT_W     = Inches(12.33)
CONTENT_H     = Inches(5.75)
FOOTER_TOP    = Inches(7.0)
FOOTER_HEIGHT = Inches(0.4)

# --- Font sizes ---
SZ_SLIDE_TITLE   = Pt(24)
SZ_SECTION_TITLE = Pt(18)
SZ_BODY          = Pt(12)
SZ_FOOTER        = Pt(9)
SZ_KPI_VALUE     = Pt(28)
SZ_KPI_LABEL     = Pt(10)
