# main.py

import pygame
import sys
import os
from noise import pnoise2  # pip install noise

# === Debug Options ===
DEBUG_MODE        = False
DEBUG_GRID_COLOR  = (255, 0, 0)
DEBUG_GRID_RADIUS = 10   # tiles in each direction

# === Tile & Chunk Settings ===
TILE_SIZE    = 32
FPS          = 60
CHUNK_SIZE   = 16   # tiles per chunk side
LOAD_RADIUS  = 2    # chunks out from player to keep loaded

# === Asset Filenames ===
ASSETS_DIR         = "assets"
FLOOR_TILE_FILE    = "tile_floor_dirt.png"
WALL_TILE_FILE     = "tile_wall_dirt.png"
PLAYER_SPRITE_FILE = "sprite_player.png"

# === Tile IDs ===
TILE_EMPTY = 0
TILE_DIRT  = 1

# --- Initialize Pygame & Fullscreen ---
pygame.init()
pygame.key.set_repeat(200, 100)

info = pygame.display.Info()
SCREEN_W = info.current_w
SCREEN_H = info.current_h

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
pygame.display.set_caption("Mini Dig 'n' Build")

clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 18)

# --- Load & Scale Sprites ---
def load_sprite(filename):
    path = os.path.join(ASSETS_DIR, filename)
    img  = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

floor_img  = load_sprite(FLOOR_TILE_FILE)
wall_img   = load_sprite(WALL_TILE_FILE)
player_img = load_sprite(PLAYER_SPRITE_FILE)

# --- Light Mask for Torch Effect ---
def make_light_mask(radius):
    mask = pygame.Surface((radius*2, radius*2), flags=pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        alpha = int(255 * (r / radius))
        pygame.draw.circle(mask, (0,0,0,alpha), (radius, radius), r)
    return mask

LIGHT_RADIUS = TILE_SIZE * 3
light_mask   = make_light_mask(LIGHT_RADIUS)

# === Chunk Storage ===
# Map (chunk_x,chunk_y) → (floor_array, wall_array)
chunks = {}

def gen_chunk(cx, cy):
    """Generate chunk: rock everywhere except Perlin caves as floor."""
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
    """Keep only chunks within LOAD_RADIUS of (px,py). Carve spawn at (0,0)."""
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
    # ensure spawn at world (0,0) is open
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

# Preload initial chunks
load_chunks_around(player_x, player_y)

# === Main Game Loop ===
running = True
while running:
    # --- Input Handling ---
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        # Continuous movement
        elif ev.type == pygame.KEYDOWN:
            nx, ny = player_x, player_y
            if ev.key == pygame.K_LEFT:  nx -= 1
            if ev.key == pygame.K_RIGHT: nx += 1
            if ev.key == pygame.K_UP:    ny -= 1
            if ev.key == pygame.K_DOWN:  ny += 1
            if can_walk(nx, ny):
                player_x, player_y = nx, ny

        # Dig / Build with mouse
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = ev.pos
            # convert screen→world tile
            cx_off = SCREEN_W // 2 - player_x * TILE_SIZE
            cy_off = SCREEN_H // 2 - player_y * TILE_SIZE
            wx = (mx - cx_off) // TILE_SIZE
            wy = (my - cy_off) // TILE_SIZE
            ccx, lx = divmod(wx, CHUNK_SIZE)
            ccy, ly = divmod(wy, CHUNK_SIZE)
            floor, wall = chunks[(ccx, ccy)]
            if ev.button == 1:  # dig
                if wall[ly][lx] != TILE_EMPTY:
                    wall[ly][lx] = TILE_EMPTY
                else:
                    floor[ly][lx] = TILE_EMPTY
            elif ev.button == 3:  # place
                if floor[ly][lx] == TILE_EMPTY:
                    floor[ly][lx] = TILE_DIRT
                else:
                    wall[ly][lx] = TILE_DIRT

    # --- Chunk Generation ---
    load_chunks_around(player_x, player_y)

    # --- Camera Offset ---
    cx_off = SCREEN_W // 2 - player_x * TILE_SIZE
    cy_off = SCREEN_H // 2 - player_y * TILE_SIZE

    # --- Render World ---
    screen.fill((20, 20, 30))
    for (cx, cy), (floor, wall) in chunks.items():
        bx = cx * CHUNK_SIZE * TILE_SIZE + cx_off
        by = cy * CHUNK_SIZE * TILE_SIZE + cy_off
        for ly in range(CHUNK_SIZE):
            for lx in range(CHUNK_SIZE):
                px = bx + lx * TILE_SIZE
                py = by + ly * TILE_SIZE
                if not (-TILE_SIZE < px < SCREEN_W and -TILE_SIZE < py < SCREEN_H):
                    continue
                if floor[ly][lx] == TILE_DIRT:
                    screen.blit(floor_img, (px, py))
                if wall[ly][lx] == TILE_DIRT:
                    screen.blit(wall_img,  (px, py))

    # Draw player at center
    screen.blit(player_img, (SCREEN_W//2, SCREEN_H//2))

    # --- Lighting Overlay ---
    dark = pygame.Surface((SCREEN_W, SCREEN_H), flags=pygame.SRCALPHA)
    dark.fill((0,0,0,200))
    dark.blit(
        light_mask,
        (SCREEN_W//2 - LIGHT_RADIUS, SCREEN_H//2 - LIGHT_RADIUS),
        special_flags=pygame.BLEND_RGBA_SUB
    )
    screen.blit(dark, (0, 0))

    # --- Debug Grid (world-anchored) ---
    if DEBUG_MODE:
        # vertical lines + labels
        for wx in range(player_x - DEBUG_GRID_RADIUS, player_x + DEBUG_GRID_RADIUS + 1):
            sx = wx * TILE_SIZE + cx_off
            pygame.draw.line(screen, DEBUG_GRID_COLOR, (sx,0), (sx,SCREEN_H), 1)
            lab = font.render(str(wx), True, DEBUG_GRID_COLOR)
            screen.blit(lab, (sx + 2, 2))
        # horizontal lines + labels
        for wy in range(player_y - DEBUG_GRID_RADIUS, player_y + DEBUG_GRID_RADIUS + 1):
            sy = wy * TILE_SIZE + cy_off
            pygame.draw.line(screen, DEBUG_GRID_COLOR, (0,sy), (SCREEN_W,sy), 1)
            lab = font.render(str(wy), True, DEBUG_GRID_COLOR)
            screen.blit(lab, (2, sy + 2))

    # --- Coordinate Readout ---
    coord_text = f"({player_x}, {player_y})"
    coord_surf = font.render(coord_text, True, (255,255,255))
    screen.blit(coord_surf, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
