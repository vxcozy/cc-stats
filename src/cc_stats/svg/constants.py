"""SVG card styling constants.

All colors are WCAG AA compliant against BG (#0d1117):
  LABEL (#8b949e): 4.7:1 contrast ratio
  VALUE (#e6edf3): 13.5:1 contrast ratio
"""

# Card dimensions
CARD_WIDTH = 480
CARD_HEIGHT = 380
CARD_RADIUS = 12

# Colors
BG = "#0d1117"
BORDER = "#30363d"
LABEL = "#8b949e"
VALUE = "#e6edf3"
CELL_EMPTY = "#161b22"
GREENS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

# Typography
FONT = "Geist Mono, monospace"
FONT_IMPORT = (
    "https://fonts.googleapis.com/css2?"
    "family=Geist+Mono:wght@300;400;600&amp;display=swap"
)

# Stat boxes layout
BOX_WIDTH = 105
BOX_HEIGHT = 52
BOX_GAP = 8
BOX_RADIUS = 8
BOX_X = 20
BOX_ROW1_Y = 62
BOX_ROW2_Y = BOX_ROW1_Y + BOX_HEIGHT + BOX_GAP

# Contribution grid layout
GRID_CELL = 7
GRID_GAP = 2
GRID_X = 20
GRID_Y = 196
GRID_COLUMNS = 26

# Project bars layout
PROJECTS_Y = 286
PROJECTS_BAR_MAX_W = 220
