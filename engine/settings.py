# settings.py

# ──────────────────────────────────────────────────────────────
# Debug Options
# ──────────────────────────────────────────────────────────────

DEBUG_MODE        = False
DEBUG_GRID_COLOR  = (255, 0, 0)
DEBUG_GRID_RADIUS = 10

# ──────────────────────────────────────────────────────────────
# Screen & Frame Settings
# ──────────────────────────────────────────────────────────────

FPS       = 60
SCREEN_W  = 0   # Set in main()
SCREEN_H  = 0

# ──────────────────────────────────────────────────────────────
# Chunk & Tile Settings
# ──────────────────────────────────────────────────────────────

CHUNK_SIZE   = 16    # Tiles per chunk (width/height)
LOAD_RADIUS  = 2     # Chunks to load around player

TILE_EMPTY   = 0
TILE_DIRT    = 1

# ──────────────────────────────────────────────────────────────
# Zoom & Tile Size Settings
# ──────────────────────────────────────────────────────────────

MIN_TILES_ACROSS     = 16   # Most zoomed-in (largest tiles)
MAX_TILES_ACROSS     = 50   # Most zoomed-out (smallest tiles)
DEFAULT_TILES_ACROSS = 28   # Default zoom level

# ──────────────────────────────────────────────────────────────
# Movement & Player Settings
# ──────────────────────────────────────────────────────────────

SPEED_TILES_PER_SEC = 8

# ──────────────────────────────────────────────────────────────
# Asset Filenames & Directory
# ──────────────────────────────────────────────────────────────

ASSETS_DIR          = "assets"
FLOOR_TILE_FILE     = "dirt_floor.png"
WALL_TILE_FILE      = "dirt_wall.png"
PLAYER_SPRITE_FILE  = "sprite_player.png"

# ──────────────────────────────────────────────────────────────
# Hotbar Settings
# ──────────────────────────────────────────────────────────────

HOTBAR_SLOTS      = 10
HOTBAR_SLOT_SIZE  = 40
HOTBAR_PADDING    = 4

# ──────────────────────────────────────────────────────────────
# Spawn Protection (tiles)
# ──────────────────────────────────────────────────────────────

SPAWN_PROTECT_WIDTH   = 5
SPAWN_PROTECT_HEIGHT  = 5

# ──────────────────────────────────────────────────────────────
# Lighting & Shading Settings
# ──────────────────────────────────────────────────────────────

LIGHT_RADIUS_TILES = 6
MAX_DARKNESS       = 245

# ──────────────────────────────────────────────────────────────
# Core Shading Depth (tiles)
# ──────────────────────────────────────────────────────────────

MAX_CORE_DEPTH = 2
