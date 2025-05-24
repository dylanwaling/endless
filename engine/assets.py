# assets.py

import os
import pygame
from engine import settings

# ──────────────────────────────────────────────────────────────
# Globals (populated by init_assets/update_zoom)
# ──────────────────────────────────────────────────────────────

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
    _orig_floor  = _load_image(settings.FLOOR_TILE_FILE)
    _orig_wall   = _load_image(settings.WALL_TILE_FILE)
    _orig_player = _load_image(settings.PLAYER_SPRITE_FILE)

def update_zoom(new_size: int) -> None:
    """
    Rescale all sprites & recompute light mask & move_speed.
    Requires that init_assets() has run.
    """
    global TILE_SIZE, floor_img, wall_img, player_img
    global LIGHT_RADIUS, light_mask, move_speed

    TILE_SIZE = max(1, new_size)

    # Rescale from originals
    floor_img  = pygame.transform.scale(_orig_floor,  (TILE_SIZE, TILE_SIZE))
    wall_img   = pygame.transform.scale(_orig_wall,   (TILE_SIZE, TILE_SIZE))
    player_img = pygame.transform.scale(_orig_player, (TILE_SIZE, TILE_SIZE))

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
