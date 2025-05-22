# render.py

import pygame
import settings
import assets

# font will be set in init_render()
font = None

def init_render():
    """Call once after pygame.init() to initialize the font."""
    global font
    font = pygame.font.SysFont(None, 18)

def draw_world(screen, player, chunks):
    """
    Draw world layers, player, lighting, debug grid, and coords.
    Requires init_render() was called first.
    """
    ts = assets.TILE_SIZE
    cam_x = settings.SCREEN_W//2 - player['px']
    cam_y = settings.SCREEN_H//2 - player['py']

    # background
    screen.fill((20,20,30))

    # terrain
    for (cx, cy), (floor, wall) in chunks.items():
        bx = cx * settings.CHUNK_SIZE * ts + cam_x
        by = cy * settings.CHUNK_SIZE * ts + cam_y

        for y in range(settings.CHUNK_SIZE):
            for x in range(settings.CHUNK_SIZE):
                px = bx + x*ts
                py = by + y*ts
                if not (-ts < px < settings.SCREEN_W and
                        -ts < py < settings.SCREEN_H):
                    continue
                if floor[y][x] == settings.TILE_DIRT:
                    screen.blit(assets.floor_img, (px, py))
                if wall[y][x] == settings.TILE_DIRT:
                    screen.blit(assets.wall_img, (px, py))

    # player
    screen.blit(assets.player_img,
                (settings.SCREEN_W//2, settings.SCREEN_H//2))

    # lighting
    dark = pygame.Surface((settings.SCREEN_W, settings.SCREEN_H),
                          flags=pygame.SRCALPHA)
    dark.fill((0,0,0,200))
    lm = assets.light_mask
    center = (settings.SCREEN_W//2 - lm.get_width()//2,
              settings.SCREEN_H//2 - lm.get_height()//2)
    dark.blit(lm, center, special_flags=pygame.BLEND_RGBA_SUB)
    screen.blit(dark, (0,0))

    # debug grid
    if settings.DEBUG_MODE:
        r = settings.DEBUG_GRID_RADIUS
        color = settings.DEBUG_GRID_COLOR
        for wx in range(player['tx']-r, player['tx']+r+1):
            sx = wx * ts + cam_x
            pygame.draw.line(screen, color, (sx,0),
                             (sx, settings.SCREEN_H), 1)
        for wy in range(player['ty']-r, player['ty']+r+1):
            sy = wy * ts + cam_y
            pygame.draw.line(screen, color, (0,sy),
                             (settings.SCREEN_W,sy), 1)

    # coordinate readout
    coord_surf = font.render(f"({player['tx']}, {player['ty']})",
                             True, (255,255,255))
    screen.blit(coord_surf, (10,10))
