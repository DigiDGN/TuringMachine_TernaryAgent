"""Theme constants for the renderer."""

WINDOW_SIZE = (1280, 720)
MIN_WINDOW_SIZE = (960, 600)
COMPACT_BREAKPOINT = (1180, 680)

FONT_STACK = ("Cascadia Mono", "JetBrains Mono", "IBM Plex Mono", "Consolas")

BACKGROUND = (5, 12, 9)
BACKGROUND_GLOW = (10, 28, 19)
TEXT = (154, 248, 174)
MUTED_TEXT = (88, 145, 101)
DIM_TEXT = (58, 102, 71)
CYAN = (92, 235, 255)
CYAN_SOFT = (22, 67, 71)
AMBER = (255, 195, 84)
RED = (255, 96, 96)
TRACK = (14, 34, 23)
GRID = (24, 58, 39)
SCANLINE = (12, 33, 20, 36)
NOISE = (44, 92, 58, 18)
SURFACE_TINT = (10, 27, 18, 180)
SURFACE_EDGE = (34, 87, 57)
ACTIVE_GLOW = (87, 255, 196, 82)
HEAD_FILL = (9, 44, 38)
HEAD_OUTLINE = (93, 235, 255)

# ── Semantic overlay: ternary symbol colors ──────────────────────────

TERNARY_POS = (92, 255, 160)     # +1  bright green
TERNARY_ZERO = (180, 200, 188)   # 0   neutral grey-green
TERNARY_NEG = (255, 110, 110)    # -1  soft red
TERNARY_BLANK = (58, 102, 71)    # _   dim

TERNARY_POS_FILL = (14, 58, 32, 180)
TERNARY_NEG_FILL = (58, 14, 14, 180)

# ── Semantic overlay: integrity mode colors ──────────────────────────

INTEGRITY_LIFE = (60, 230, 120)   # healthy / productive
INTEGRITY_SEED = (230, 200, 60)   # latent / unresolved
INTEGRITY_DEATH = (230, 70, 70)   # corrupt / trapped

# ── Semantic overlay: office role indicators ─────────────────────────

OFFICE_GENERATOR = (92, 200, 255)  # blue-cyan
OFFICE_ARBITER = (180, 160, 255)   # soft purple
OFFICE_CRITIC = (255, 180, 90)     # warm amber

