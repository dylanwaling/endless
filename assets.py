# assets.py

import os
import pygame
import settings

# — Raw surfaces, loaded once after display init —
_floor = None
_wall  = None
_player = None

# — Scaled assets & lighting placeholders —
TILE_SIZE    = None
floor_img    = None
wall_img     = None
player_img   = None
LIGHT_RADIUS = None
light_mask   = None

def init_assets():
    """Load the raw images. Call once after pygame.display.set_mode."""
    global _floor, _wall, _player
    _floor  = pygame.image.load(
        os.path.join(settings.ASSETS_DIR, settings.FLOOR_TILE_FILE)
    ).convert_alpha()
    _wall   = pygame.image.load(
        os.path.join(settings.ASSETS_DIR, settings.WALL_TILE_FILE)
    ).convert_alpha()
    _player = pygame.image.load(
        os.path.join(settings.ASSETS_DIR, settings.PLAYER_SPRITE_FILE)
    ).convert_alpha()

def make_light_mask(r):
    mask = pygame.Surface((r*2, r*2), flags=pygame.SRCALPHA)
    for radius in range(r, 0, -1):
        alpha = int(255 * (radius / r))
        pygame.draw.circle(mask, (0,0,0,alpha), (r, r), radius)
    return mask

def update_zoom(new_size):
    """
    Clamp TILE_SIZE between the min/max based on tiles-across,
    lazy-load raw images if needed, then rescale all.
    """
    global TILE_SIZE, floor_img, wall_img, player_img
    global LIGHT_RADIUS, light_mask

    # First call: load raw PNGs
    if _floor is None:
        init_assets()

    # Clamp to settings
    min_px = settings.SCREEN_W // settings.MIN_TILES_ACROSS
    max_px = settings.SCREEN_W // settings.MAX_TILES_ACROSS
    size = max(min_px, min(max_px, new_size))

    TILE_SIZE = size

    # Rescale for this zoom
    floor_img  = pygame.transform.scale(_floor,  (size, size))
    wall_img   = pygame.transform.scale(_wall,   (size, size))
    player_img = pygame.transform.scale(_player, (size, size))

    # Recompute light mask
    LIGHT_RADIUS = size * 3
    light_mask   = make_light_mask(LIGHT_RADIUS)
