# settings.py

# --- Debug Options ---
DEBUG_MODE        = False
DEBUG_GRID_COLOR  = (255, 0, 0)
DEBUG_GRID_RADIUS = 10   # tiles in each direction for debug grid

# --- Screen & Frame Settings ---
FPS = 60
SCREEN_W = 0   # will be set in main()
SCREEN_H = 0

# --- Chunk Settings ---
CHUNK_SIZE  = 16       # tiles per chunk side
LOAD_RADIUS = 2        # chunks to keep loaded around the player

# --- Tile IDs ---
TILE_EMPTY = 0
TILE_DIRT  = 1

# --- Zoom Range (tiles across screen) ---
MIN_TILES_ACROSS     = 50   # extreme zoom out
MAX_TILES_ACROSS     = 16   # extreme zoom in
DEFAULT_TILES_ACROSS = 28   # starting zoom

# --- Movement Speed (tiles/sec) ---
SPEED_TILES_PER_SEC = 8

# --- Asset Filenames & Directory ---
ASSETS_DIR         = "assets"
FLOOR_TILE_FILE    = "tile_floor_dirt.png"
WALL_TILE_FILE     = "tile_wall_dirt.png"
PLAYER_SPRITE_FILE = "sprite_player.png"

# --- Spawn Protection (half-extents in tiles) ---
# Protects all blocks where |x| ≤ WIDTH and |y| ≤ HEIGHT
SPAWN_PROTECT_WIDTH  = 5
SPAWN_PROTECT_HEIGHT = 5
