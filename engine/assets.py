# assets.py

import os
import pygame
from engine import settings

# ──────────────────────────────────────────────────────────────
# Globals
# ──────────────────────────────────────────────────────────────

TILE_SIZE    = None
floor_img    = None
wall_img     = None
player_img   = None
LIGHT_RADIUS = None
light_mask   = None
move_speed   = None

# Private originals (populated in init_assets)
_orig_floor  = None
_orig_wall   = None
_orig_player = None

# ──────────────────────────────────────────────────────────────
# Asset Initialization & Scaling
# ──────────────────────────────────────────────────────────────

def init_assets():
    """
    Call once after pygame.init() and display.set_mode().
    Loads original images into memory so update_zoom can rescale them.
    """
    global _orig_floor, _orig_wall, _orig_player

    _orig_floor  = pygame.image.load(
        os.path.join(settings.ASSETS_DIR, settings.FLOOR_TILE_FILE)
    ).convert_alpha()
    _orig_wall   = pygame.image.load(
        os.path.join(settings.ASSETS_DIR, settings.WALL_TILE_FILE)
    ).convert_alpha()
    _orig_player = pygame.image.load(
        os.path.join(settings.ASSETS_DIR, settings.PLAYER_SPRITE_FILE)
    ).convert_alpha()

def update_zoom(new_size):
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

    # Light mask
    LIGHT_RADIUS = TILE_SIZE * settings.LIGHT_RADIUS_TILES
    light_mask   = make_light_mask(LIGHT_RADIUS)

    # Movement speed (pixels/sec)
    move_speed = settings.SPEED_TILES_PER_SEC * TILE_SIZE

# ──────────────────────────────────────────────────────────────
# Lighting
# ──────────────────────────────────────────────────────────────

def make_light_mask(radius):
    """
    Create a radial light mask surface.
    """
    mask = pygame.Surface((radius * 2, radius * 2), flags=pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        alpha = int(255 * (r / radius))
        pygame.draw.circle(mask, (0, 0, 0, alpha), (radius, radius), r)
    return mask
