# settings.py

# --- Debug Options ---
DEBUG_MODE        = False
DEBUG_GRID_COLOR  = (255, 0, 0)
DEBUG_GRID_RADIUS = 10

# --- Screen & Frame Settings ---
FPS      = 60
SCREEN_W = 0   # will be set in main()
SCREEN_H = 0

# --- Chunk Settings ---
CHUNK_SIZE  = 16
LOAD_RADIUS = 2

# --- Tile IDs ---
TILE_EMPTY = 0
TILE_DIRT  = 1

# --- Zoom Range (tiles across) ---
MIN_TILES_ACROSS     = 50
MAX_TILES_ACROSS     = 16
DEFAULT_TILES_ACROSS = 28

# --- Movement Speed (tiles/sec) ---
SPEED_TILES_PER_SEC = 8

# --- Asset Filenames & Directory ---
ASSETS_DIR         = "assets"
FLOOR_TILE_FILE    = "tile_floor_dirt.png"
WALL_TILE_FILE     = "tile_wall_dirt.png"
PLAYER_SPRITE_FILE = "sprite_player.png"

# --- Hotbar ---
HOTBAR_SLOTS     = 10
HOTBAR_SLOT_SIZE = 40
HOTBAR_PADDING   = 4

# --- Spawn Protection (tiles) ---
SPAWN_PROTECT_WIDTH  = 5
SPAWN_PROTECT_HEIGHT = 5

# --- Lighting Settings ---
# how many tiles out the player's light reaches
LIGHT_RADIUS_TILES = 6

# maximum darkness alpha (0 = no dark, 255 = pitch black)
MAX_DARKNESS       = 200

# --- Core Shading Depth (tiles) ---
# number of tiles from a lit edge before you reach full black.
# 2–3: tight, quick darkening; 6–8: long gentle fade.
MAX_CORE_DEPTH     = 4
