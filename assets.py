import os
import pygame
import settings

# Raw surfaces, loaded once after display init:
_floor = _wall = _player = None

# Scaled assets & lighting placeholders:
TILE_SIZE    = None
floor_img    = None
wall_img     = None
player_img   = None
LIGHT_RADIUS = None
light_mask   = None

def init_assets():
    global _floor, _wall, _player
    _floor  = pygame.image.load(os.path.join(settings.ASSETS_DIR, settings.FLOOR_TILE_FILE)).convert_alpha()
    _wall   = pygame.image.load(os.path.join(settings.ASSETS_DIR, settings.WALL_TILE_FILE )).convert_alpha()
    _player = pygame.image.load(os.path.join(settings.ASSETS_DIR, settings.PLAYER_SPRITE_FILE)).convert_alpha()

def make_light_mask(r):
    mask = pygame.Surface((r*2, r*2), flags=pygame.SRCALPHA)
    for rad in range(r, 0, -1):
        a = int(255 * (rad / r))
        pygame.draw.circle(mask, (0,0,0,a), (r, r), rad)
    return mask

def update_zoom(new_size):
    global TILE_SIZE, floor_img, wall_img, player_img, LIGHT_RADIUS, light_mask

    if _floor is None:
        init_assets()

    # clamp to min/max tiles-across converted to pixels
    min_px = settings.SCREEN_W // settings.MIN_TILES_ACROSS
    max_px = settings.SCREEN_W // settings.MAX_TILES_ACROSS
    size = max(min_px, min(max_px, new_size))
    TILE_SIZE = size

    floor_img  = pygame.transform.scale(_floor,  (size, size))
    wall_img   = pygame.transform.scale(_wall,   (size, size))
    player_img = pygame.transform.scale(_player, (size, size))

    LIGHT_RADIUS = size * 3
    light_mask   = make_light_mask(LIGHT_RADIUS)
