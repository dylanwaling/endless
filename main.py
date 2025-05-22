# main.py

import pygame
import sys
import os
from noise import pnoise2  # pip install noise

# === Debug Options ===
DEBUG_MODE        = False
DEBUG_GRID_COLOR  = (255, 0, 0)
DEBUG_GRID_RADIUS = 10   # tiles in each direction for debug grid

# === Screen & Frame Settings ===
FPS = 60

# === Chunk Settings ===
CHUNK_SIZE  = 16       # tiles per chunk side
LOAD_RADIUS = 2        # chunks around player to keep loaded

# === Asset Filenames ===
ASSETS_DIR         = "assets"
FLOOR_TILE_FILE    = "tile_floor_dirt.png"
WALL_TILE_FILE     = "tile_wall_dirt.png"
PLAYER_SPRITE_FILE = "sprite_player.png"

# === Tile IDs ===
TILE_EMPTY = 0
TILE_DIRT  = 1

# === Zoom Range Settings (change these!) ===
MIN_TILES_ACROSS     = 50   # max zoom OUT: 50 tiles across
MAX_TILES_ACROSS     = 16   # max zoom IN:  16 tiles across
DEFAULT_TILES_ACROSS = 28   # default zoom:  28 tiles across

# --- Pygame init & fullscreen ---
pygame.init()
pygame.key.set_repeat(200, 100)

info     = pygame.display.Info()
SCREEN_W = info.current_w
SCREEN_H = info.current_h
screen   = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
pygame.display.set_caption("Mini Dig 'n' Build")

clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 18)

# --- Compute tile size bounds from tile counts ---
MIN_TILE_SIZE     = max(1, SCREEN_W // MIN_TILES_ACROSS)
MAX_TILE_SIZE     = max(1, SCREEN_W // MAX_TILES_ACROSS)
DEFAULT_TILE_SIZE = max(1, SCREEN_W // DEFAULT_TILES_ACROSS)

# --- Load original assets ---
def load_original(fn):
    return pygame.image.load(os.path.join(ASSETS_DIR, fn)).convert_alpha()

floor_orig  = load_original(FLOOR_TILE_FILE)
wall_orig   = load_original(WALL_TILE_FILE)
player_orig = load_original(PLAYER_SPRITE_FILE)

# placeholders; set by update_zoom()
TILE_SIZE   = None
floor_img   = wall_img   = player_img = None
LIGHT_RADIUS = None
light_mask   = None

def make_light_mask(r):
    mask = pygame.Surface((r*2, r*2), flags=pygame.SRCALPHA)
    for radius in range(r, 0, -1):
        alpha = int(255 * (radius / r))
        pygame.draw.circle(mask, (0,0,0,alpha), (r, r), radius)
    return mask

def update_zoom(new_size):
    """Clamp TILE_SIZE between MIN_TILE_SIZE and MAX_TILE_SIZE,
       rescale sprites and recompute lighting."""
    global TILE_SIZE, floor_img, wall_img, player_img
    global LIGHT_RADIUS, light_mask

    TILE_SIZE = max(MIN_TILE_SIZE, min(MAX_TILE_SIZE, new_size))

    # rescale sprites
    floor_img  = pygame.transform.scale(floor_orig,  (TILE_SIZE, TILE_SIZE))
    wall_img   = pygame.transform.scale(wall_orig,   (TILE_SIZE, TILE_SIZE))
    player_img = pygame.transform.scale(player_orig, (TILE_SIZE, TILE_SIZE))

    # recompute light mask
    LIGHT_RADIUS = TILE_SIZE * 3
    light_mask   = make_light_mask(LIGHT_RADIUS)

# initialize zoom to default
update_zoom(DEFAULT_TILE_SIZE)

# === Chunk storage: (cx,cy) → (floor_array, wall_array) ===
chunks = {}

def gen_chunk(cx, cy):
    """Generate rock everywhere, open floor where Perlin > 0."""
    floor = [[TILE_EMPTY]*CHUNK_SIZE for _ in range(CHUNK_SIZE)]
    wall  = [[TILE_EMPTY]*CHUNK_SIZE for _ in range(CHUNK_SIZE)]
    for ly in range(CHUNK_SIZE):
        for lx in range(CHUNK_SIZE):
            wx = cx*CHUNK_SIZE + lx
            wy = cy*CHUNK_SIZE + ly
            n  = pnoise2(wx*0.1, wy*0.1, octaves=2)
            if n > 0.0:
                floor[ly][lx] = TILE_DIRT
            else:
                wall[ly][lx]  = TILE_DIRT
    return floor, wall

def load_chunks_around(px, py):
    """Keep only chunks within LOAD_RADIUS; carve spawn at (0,0)."""
    pcx, _ = divmod(px, CHUNK_SIZE)
    pcy, _ = divmod(py, CHUNK_SIZE)
    needed = {
        (pcx+dx, pcy+dy)
        for dx in range(-LOAD_RADIUS, LOAD_RADIUS+1)
        for dy in range(-LOAD_RADIUS, LOAD_RADIUS+1)
    }
    # generate missing
    for coord in needed:
        if coord not in chunks:
            chunks[coord] = gen_chunk(*coord)
    # unload distant
    for coord in list(chunks):
        if coord not in needed:
            del chunks[coord]
    # ensure world (0,0) spawn is open
    if (0,0) in chunks:
        f, w = chunks[(0,0)]
        f[0][0] = TILE_DIRT
        w[0][0] = TILE_EMPTY

# === Player State (world tile coords) ===
player_x = 0
player_y = 0

def can_walk(x, y):
    cx, lx = divmod(x, CHUNK_SIZE)
    cy, ly = divmod(y, CHUNK_SIZE)
    floor, wall = chunks.get((cx, cy), (None, None))
    if floor is None:
        return False
    return floor[ly][lx] == TILE_DIRT and wall[ly][lx] == TILE_EMPTY

# preload initial chunks
load_chunks_around(player_x, player_y)

# === Main Loop ===
running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        # movement keys
        elif ev.type == pygame.KEYDOWN:
            nx, ny = player_x, player_y
            if ev.key == pygame.K_LEFT:  nx -= 1
            if ev.key == pygame.K_RIGHT: nx += 1
            if ev.key == pygame.K_UP:    ny -= 1
            if ev.key == pygame.K_DOWN:  ny += 1
            if can_walk(nx, ny):
                player_x, player_y = nx, ny

        # zoom via mouse wheel
        elif ev.type == pygame.MOUSEWHEEL:
            if ev.y > 0:
                # zoom in (fewer tiles across)
                update_zoom(TILE_SIZE + 4)
            elif ev.y < 0:
                # zoom out (more tiles across)
                update_zoom(TILE_SIZE - 4)
            load_chunks_around(player_x, player_y)

        # reset zoom on middle-click
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 2:
            update_zoom(DEFAULT_TILE_SIZE)
            load_chunks_around(player_x, player_y)

        # digging/building
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3):
            mx, my = ev.pos
            cam_x = SCREEN_W//2 - player_x*TILE_SIZE
            cam_y = SCREEN_H//2 - player_y*TILE_SIZE
            wx = (mx - cam_x)//TILE_SIZE
            wy = (my - cam_y)//TILE_SIZE
            ccx, lx = divmod(wx, CHUNK_SIZE)
            ccy, ly = divmod(wy, CHUNK_SIZE)
            floor, wall = chunks[(ccx, ccy)]
            if ev.button == 1:  # dig
                if wall[ly][lx] != TILE_EMPTY:
                    wall[ly][lx] = TILE_EMPTY
                else:
                    floor[ly][lx] = TILE_EMPTY
            else:  # right-click build
                if floor[ly][lx] == TILE_EMPTY:
                    floor[ly][lx] = TILE_DIRT
                else:
                    wall[ly][lx] = TILE_DIRT

    # refresh chunks
    load_chunks_around(player_x, player_y)

    # compute camera offset
    cam_x = SCREEN_W//2 - player_x*TILE_SIZE
    cam_y = SCREEN_H//2 - player_y*TILE_SIZE

    # render world
    screen.fill((20,20,30))
    for (cx, cy), (floor, wall) in chunks.items():
        bx = cx*CHUNK_SIZE*TILE_SIZE + cam_x
        by = cy*CHUNK_SIZE*TILE_SIZE + cam_y
        for ly in range(CHUNK_SIZE):
            for lx in range(CHUNK_SIZE):
                px = bx + lx*TILE_SIZE
                py = by + ly*TILE_SIZE
                if not (-TILE_SIZE < px < SCREEN_W and -TILE_SIZE < py < SCREEN_H):
                    continue
                if floor[ly][lx] == TILE_DIRT:
                    screen.blit(floor_img, (px, py))
                if wall[ly][lx] == TILE_DIRT:
                    screen.blit(wall_img,  (px, py))

    # draw player at screen center
    screen.blit(player_img, (SCREEN_W//2, SCREEN_H//2))

    # lighting overlay
    dark = pygame.Surface((SCREEN_W, SCREEN_H), flags=pygame.SRCALPHA)
    dark.fill((0,0,0,200))
    dark.blit(light_mask,
              (SCREEN_W//2 - LIGHT_RADIUS, SCREEN_H//2 - LIGHT_RADIUS),
              special_flags=pygame.BLEND_RGBA_SUB)
    screen.blit(dark, (0,0))

    # debug grid
    if DEBUG_MODE:
        for wx in range(player_x-DEBUG_GRID_RADIUS, player_x+DEBUG_GRID_RADIUS+1):
            sx = wx*TILE_SIZE + cam_x
            pygame.draw.line(screen, DEBUG_GRID_COLOR, (sx,0), (sx,SCREEN_H), 1)
            lab = font.render(str(wx), True, DEBUG_GRID_COLOR)
            screen.blit(lab, (sx+2, 2))
        for wy in range(player_y-DEBUG_GRID_RADIUS, player_y+DEBUG_GRID_RADIUS+1):
            sy = wy*TILE_SIZE + cam_y
            pygame.draw.line(screen, DEBUG_GRID_COLOR, (0,sy), (SCREEN_W,sy), 1)
            lab = font.render(str(wy), True, DEBUG_GRID_COLOR)
            screen.blit(lab, (2, sy+2))

    # coordinate readout
    coord_surf = font.render(f"({player_x}, {player_y})", True, (255,255,255))
    screen.blit(coord_surf, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
