# main.py

import pygame
import sys
import os
from noise import pnoise2  # pip install noise

# === Debug Options ===
DEBUG_MODE        = False
DEBUG_GRID_COLOR  = (255, 0, 0)
DEBUG_GRID_RADIUS = 10   # how many tiles out from the player

# === Screen & Tile Settings ===
SCREEN_W, SCREEN_H = 640, 480
TILE_SIZE         = 32
FPS               = 60

# === Chunk Settings ===
CHUNK_SIZE  = 16       # tiles per chunk side
LOAD_RADIUS = 2        # chunks out from player to load

# === Assets ===
ASSETS_DIR         = "assets"
FLOOR_TILE_FILE    = "tile_floor_dirt.png"
WALL_TILE_FILE     = "tile_wall_dirt.png"
PLAYER_SPRITE_FILE = "sprite_player.png"

# === Tile IDs ===
TILE_EMPTY = 0
TILE_DIRT  = 1

# --- Pygame Initialization ---
pygame.init()
pygame.key.set_repeat(200, 100)  # enable holding arrow keys
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock  = pygame.time.Clock()
font   = pygame.font.SysFont(None, 18)

# --- Load & scale sprites ---
def load_sprite(filename):
    path = os.path.join(ASSETS_DIR, filename)
    img  = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

floor_img  = load_sprite(FLOOR_TILE_FILE)
wall_img   = load_sprite(WALL_TILE_FILE)
player_img = load_sprite(PLAYER_SPRITE_FILE)

# --- Light mask for torch effect ---
def make_light_mask(radius):
    mask = pygame.Surface((radius*2, radius*2), flags=pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        alpha = int(255 * (r / radius))
        pygame.draw.circle(mask, (0,0,0,alpha), (radius, radius), r)
    return mask

LIGHT_RADIUS = TILE_SIZE * 3
light_mask   = make_light_mask(LIGHT_RADIUS)

# === Chunk storage: (cx,cy) → (floor, wall) arrays ===
chunks = {}

def gen_chunk(cx, cy):
    """Procedurally generate a chunk's floor & wall using Perlin noise."""
    floor = [[TILE_EMPTY]*CHUNK_SIZE for _ in range(CHUNK_SIZE)]
    wall  = [[TILE_EMPTY]*CHUNK_SIZE for _ in range(CHUNK_SIZE)]
    for ly in range(CHUNK_SIZE):
        for lx in range(CHUNK_SIZE):
            wx = cx*CHUNK_SIZE + lx
            wy = cy*CHUNK_SIZE + ly
            n  = pnoise2(wx*0.1, wy*0.1, octaves=2)
            if n > 0.0:
                floor[ly][lx] = TILE_DIRT
    return floor, wall

def load_chunks_around(px, py):
    """Ensure all chunks within LOAD_RADIUS of player exist; unload others."""
    pcx, _ = divmod(px, CHUNK_SIZE)
    pcy, _ = divmod(py, CHUNK_SIZE)
    needed = {
        (pcx + dx, pcy + dy)
        for dx in range(-LOAD_RADIUS, LOAD_RADIUS+1)
        for dy in range(-LOAD_RADIUS, LOAD_RADIUS+1)
    }
    for coord in needed:
        if coord not in chunks:
            chunks[coord] = gen_chunk(*coord)
    for coord in list(chunks):
        if coord not in needed:
            del chunks[coord]

# === Player State (in world tile coords) ===
player_x = 0
player_y = 0

# Force spawn tile to be dirt
load_chunks_around(player_x, player_y)
# spawn is in chunk (0,0) at local (0,0)
if (0,0) in chunks:
    spawn_floor, _ = chunks[(0,0)]
    spawn_floor[0][0] = TILE_DIRT

def can_walk(x, y):
    cx, lx = divmod(x, CHUNK_SIZE)
    cy, ly = divmod(y, CHUNK_SIZE)
    floor, wall = chunks.get((cx, cy), (None, None))
    if floor is None:
        return False
    return floor[ly][lx] == TILE_DIRT and wall[ly][lx] == TILE_EMPTY

# === Main Game Loop ===
running = True
while running:
    # --- Event Handling ---
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

        # Digging / Building
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = ev.pos
            center_x = SCREEN_W // 2
            center_y = SCREEN_H // 2
            world_x = (mx - center_x) // TILE_SIZE + player_x
            world_y = (my - center_y) // TILE_SIZE + player_y
            cx, lx = divmod(world_x, CHUNK_SIZE)
            cy, ly = divmod(world_y, CHUNK_SIZE)
            floor, wall = chunks[(cx, cy)]
            if ev.button == 1:  # Left click: dig
                if wall[ly][lx] != TILE_EMPTY:
                    wall[ly][lx] = TILE_EMPTY
                else:
                    floor[ly][lx] = TILE_EMPTY
            elif ev.button == 3:  # Right click: build
                if floor[ly][lx] == TILE_EMPTY:
                    floor[ly][lx] = TILE_DIRT
                else:
                    wall[ly][lx] = TILE_DIRT

    # Load/unload nearby chunks
    load_chunks_around(player_x, player_y)

    # Compute camera so player is centered on screen
    center_x = SCREEN_W // 2
    center_y = SCREEN_H // 2
    cam_x = center_x - player_x * TILE_SIZE
    cam_y = center_y - player_y * TILE_SIZE

    # --- Draw World ---
    screen.fill((20, 20, 30))
    for (cx, cy), (floor, wall) in chunks.items():
        base_x = cx * CHUNK_SIZE * TILE_SIZE + cam_x
        base_y = cy * CHUNK_SIZE * TILE_SIZE + cam_y
        for ly in range(CHUNK_SIZE):
            for lx in range(CHUNK_SIZE):
                px = base_x + lx * TILE_SIZE
                py = base_y + ly * TILE_SIZE
                if not (-TILE_SIZE < px < SCREEN_W and -TILE_SIZE < py < SCREEN_H):
                    continue
                if floor[ly][lx] == TILE_DIRT:
                    screen.blit(floor_img, (px, py))
                if wall[ly][lx] == TILE_DIRT:
                    screen.blit(wall_img, (px, py))

    # Draw player at screen center
    screen.blit(player_img, (center_x, center_y))

    # --- Lighting Overlay ---
    darkness = pygame.Surface((SCREEN_W, SCREEN_H), flags=pygame.SRCALPHA)
    darkness.fill((0, 0, 0, 200))
    darkness.blit(
        light_mask,
        (center_x - LIGHT_RADIUS, center_y - LIGHT_RADIUS),
        special_flags=pygame.BLEND_RGBA_SUB
    )
    screen.blit(darkness, (0, 0))

    # --- Debug Grid (world‐anchored) ---
    if DEBUG_MODE:
        # Vertical lines and world X labels
        for wx in range(player_x - DEBUG_GRID_RADIUS, player_x + DEBUG_GRID_RADIUS + 1):
            sx = wx * TILE_SIZE + cam_x
            pygame.draw.line(screen, DEBUG_GRID_COLOR, (sx, 0), (sx, SCREEN_H), 1)
            label = font.render(str(wx), True, DEBUG_GRID_COLOR)
            screen.blit(label, (sx + 2, 2))
        # Horizontal lines and world Y labels
        for wy in range(player_y - DEBUG_GRID_RADIUS, player_y + DEBUG_GRID_RADIUS + 1):
            sy = wy * TILE_SIZE + cam_y
            pygame.draw.line(screen, DEBUG_GRID_COLOR, (0, sy), (SCREEN_W, sy), 1)
            label = font.render(str(wy), True, DEBUG_GRID_COLOR)
            screen.blit(label, (2, sy + 2))

    # --- Coordinate Readout ---
    coord_text = f"({player_x}, {player_y})"
    coord_surf = font.render(coord_text, True, (255, 255, 255))
    screen.blit(coord_surf, (10, 10))

    # --- Finish Frame ---
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
