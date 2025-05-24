# assets.py

import os
import pygame
from engine import settings

# ──────────────────────────────────────────────────────────────
# Globals (populated by init_assets/update_zoom)
# ──────────────────────────────────────────────────────────────

WALL_HEIGHT = 72  # Tall wall sprite for 2.5D

TILE_SIZE: int = None
floor_img: pygame.Surface = None
wall_img: pygame.Surface = None
player_img: pygame.Surface = None
LIGHT_RADIUS: int = None
light_mask: pygame.Surface = None
move_speed: float = None

# Private originals (used for rescaling)
_orig_floor: pygame.Surface = None
_orig_wall: pygame.Surface = None
_orig_player: pygame.Surface = None

# Add these globals at the top (after the originals)
rim_north_img: pygame.Surface = None
rim_south_img: pygame.Surface = None
rim_east_img: pygame.Surface = None
rim_west_img: pygame.Surface = None

rim_nw_img: pygame.Surface = None
rim_ne_img: pygame.Surface = None
rim_sw_img: pygame.Surface = None
rim_se_img: pygame.Surface = None

# Add originals for rim overlays
_orig_rim_north: pygame.Surface = None
_orig_rim_south: pygame.Surface = None
_orig_rim_east: pygame.Surface = None
_orig_rim_west: pygame.Surface = None

_orig_rim_nw: pygame.Surface = None
_orig_rim_ne: pygame.Surface = None
_orig_rim_sw: pygame.Surface = None
_orig_rim_se: pygame.Surface = None

# ──────────────────────────────────────────────────────────────
# Asset Initialization & Scaling
# ──────────────────────────────────────────────────────────────

def _load_image(filename: str) -> pygame.Surface:
    """Load an image from the assets directory with alpha support."""
    path = os.path.join(settings.ASSETS_DIR, filename)
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        raise RuntimeError(f"Failed to load asset '{filename}': {e}")

def init_assets() -> None:
    """
    Loads original images into memory.
    Call once after pygame.init() and display.set_mode().
    """
    global _orig_floor, _orig_wall, _orig_player
    global _orig_rim_north, _orig_rim_south, _orig_rim_east, _orig_rim_west
    global _orig_rim_nw, _orig_rim_ne, _orig_rim_sw, _orig_rim_se

    _orig_floor  = _load_image(settings.FLOOR_TILE_FILE)
    _orig_wall   = _load_image(settings.WALL_TILE_FILE)
    _orig_player = _load_image(settings.PLAYER_SPRITE_FILE)

    # Load all rim overlays using _load_image for consistent paths
    _orig_rim_north = _load_image("rim_north.png")
    _orig_rim_south = _load_image("rim_south.png")
    _orig_rim_east  = _load_image("rim_east.png")
    _orig_rim_west  = _load_image("rim_west.png")
    _orig_rim_nw    = _load_image("rim_nw.png")
    _orig_rim_ne    = _load_image("rim_ne.png")
    _orig_rim_sw    = _load_image("rim_sw.png")
    _orig_rim_se    = _load_image("rim_se.png")

def update_zoom(new_size: int) -> None:
    """
    Rescale all sprites & recompute light mask & move_speed.
    Requires that init_assets() has run.
    """
    global TILE_SIZE, floor_img, wall_img, player_img
    global WALL_HEIGHT
    global LIGHT_RADIUS, light_mask, move_speed
    global rim_north_img, rim_south_img, rim_east_img, rim_west_img
    global rim_nw_img, rim_ne_img, rim_sw_img, rim_se_img

    TILE_SIZE = max(1, new_size)
    WALL_HEIGHT = int(TILE_SIZE * 1.5)  # 1.5x tile size for tall wall

    # Rescale from originals
    floor_img  = pygame.transform.scale(_orig_floor,  (TILE_SIZE, TILE_SIZE))
    wall_img   = pygame.transform.scale(_orig_wall,   (TILE_SIZE, WALL_HEIGHT))
    player_img = pygame.transform.scale(_orig_player, (TILE_SIZE, TILE_SIZE))

    # Rescale rim overlays to match TILE_SIZE
    rim_north_img = pygame.transform.scale(_orig_rim_north, (TILE_SIZE, WALL_HEIGHT))
    rim_south_img = pygame.transform.scale(_orig_rim_south, (TILE_SIZE, WALL_HEIGHT))
    rim_east_img  = pygame.transform.scale(_orig_rim_east,  (TILE_SIZE, WALL_HEIGHT))
    rim_west_img  = pygame.transform.scale(_orig_rim_west,  (TILE_SIZE, WALL_HEIGHT))

    rim_nw_img = pygame.transform.scale(_orig_rim_nw, (TILE_SIZE, WALL_HEIGHT))
    rim_ne_img = pygame.transform.scale(_orig_rim_ne, (TILE_SIZE, WALL_HEIGHT))
    rim_sw_img = pygame.transform.scale(_orig_rim_sw, (TILE_SIZE, WALL_HEIGHT))
    rim_se_img = pygame.transform.scale(_orig_rim_se, (TILE_SIZE, WALL_HEIGHT))

    # Lighting and movement
    LIGHT_RADIUS = TILE_SIZE * settings.LIGHT_RADIUS_TILES
    light_mask   = make_light_mask(LIGHT_RADIUS)
    move_speed   = settings.SPEED_TILES_PER_SEC * TILE_SIZE

# ──────────────────────────────────────────────────────────────
# Lighting
# ──────────────────────────────────────────────────────────────

def make_light_mask(radius: int) -> pygame.Surface:
    """
    Create a radial light mask surface with a smooth gradient.
    """
    mask = pygame.Surface((radius * 2, radius * 2), flags=pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        # Use quadratic falloff for a smoother gradient
        alpha = int(255 * ((r / radius) ** 2))
        pygame.draw.circle(mask, (0, 0, 0, alpha), (radius, radius), r)
    return mask

# ──────────────────────────────────────────────────────────────
# Utility (optional: for reloading assets at runtime)
# ──────────────────────────────────────────────────────────────

def reload_assets(new_tile_size: int) -> None:
    """
    Reload and rescale all assets. Useful if assets or settings change at runtime.
    """
    init_assets()
    update_zoom(new_tile_size)
