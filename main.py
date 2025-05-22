# main.py

import pygame
import sys
import os
from noise import pnoise2  # pip install noise

# === Debug Options ===
DEBUG_MODE        = False
DEBUG_GRID_COLOR  = (255, 0, 0)
DEBUG_GRID_RADIUS = 10

# === Screen & Frame Settings ===
FPS = 60

# === Chunk Settings ===
CHUNK_SIZE  = 16
LOAD_RADIUS = 2

# === Asset Filenames ===
ASSETS_DIR         = "assets"
FLOOR_TILE_FILE    = "tile_floor_dirt.png"
WALL_TILE_FILE     = "tile_wall_dirt.png"
PLAYER_SPRITE_FILE = "sprite_player.png"

# === Tile IDs ===
TILE_EMPTY = 0
TILE_DIRT  = 1

# === Zoom Range Settings ===
MIN_TILES_ACROSS     = 50
MAX_TILES_ACROSS     = 16
DEFAULT_TILES_ACROSS = 28

# === Movement Speed (tiles/sec) ===
SPEED_TILES_PER_SEC = 8

# --- Initialize Pygame & Fullscreen ---
pygame.init()
info     = pygame.display.Info()
SCREEN_W = info.current_w
SCREEN_H = info.current_h
screen   = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
pygame.display.set_caption("Mini Dig 'n' Build")
clock    = pygame.time.Clock()
font     = pygame.font.SysFont(None, 18)

# --- Compute tile‐size bounds ---
MIN_TILE_SIZE     = max(1, SCREEN_W // MIN_TILES_ACROSS)
MAX_TILE_SIZE     = max(1, SCREEN_W // MAX_TILES_ACROSS)
DEFAULT_TILE_SIZE = max(1, SCREEN_W // DEFAULT_TILES_ACROSS)

# === Player State ===
player_tx = 0
player_ty = 0
player_px = player_tx * DEFAULT_TILE_SIZE
player_py = player_ty * DEFAULT_TILE_SIZE
target_px = player_px
target_py = player_py
moving    = False

# --- Load raw assets ---
def load_original(fn):
    return pygame.image.load(os.path.join(ASSETS_DIR, fn)).convert_alpha()

floor_orig  = load_original(FLOOR_TILE_FILE)
wall_orig   = load_original(WALL_TILE_FILE)
player_orig = load_original(PLAYER_SPRITE_FILE)

# placeholders for scaled
TILE_SIZE    = None
floor_img    = wall_img    = player_img = None
LIGHT_RADIUS = None
light_mask   = None
move_speed   = None

def make_light_mask(r):
    mask = pygame.Surface((r*2, r*2), flags=pygame.SRCALPHA)
    for rad in range(r, 0, -1):
        alpha = int(255 * (rad / r))
        pygame.draw.circle(mask, (0,0,0,alpha), (r, r), rad)
    return mask

def update_zoom(new_size):
    global TILE_SIZE, floor_img, wall_img, player_img
    global LIGHT_RADIUS, light_mask, move_speed
    global player_px, player_py, target_px, target_py

    TILE_SIZE = max(MIN_TILE_SIZE, min(MAX_TILE_SIZE, new_size))

    floor_img  = pygame.transform.scale(floor_orig,  (TILE_SIZE, TILE_SIZE))
    wall_img   = pygame.transform.scale(wall_orig,   (TILE_SIZE, TILE_SIZE))
    player_img = pygame.transform.scale(player_orig, (TILE_SIZE, TILE_SIZE))

    LIGHT_RADIUS = TILE_SIZE * 3
    light_mask   = make_light_mask(LIGHT_RADIUS)

    move_speed = SPEED_TILES_PER_SEC * TILE_SIZE

    # re‐sync pixel position
    player_px = player_tx * TILE_SIZE
    player_py = player_ty * TILE_SIZE
    target_px = player_px
    target_py = player_py

# initialize zoom
update_zoom(DEFAULT_TILE_SIZE)

# === Chunk storage ===
chunks = {}

def gen_chunk(cx, cy):
    """Generate a chunk where every cell has a floor,
    and walls appear (on top) where noise ≤ 0."""
    floor = [[TILE_DIRT]*CHUNK_SIZE for _ in range(CHUNK_SIZE)]
    wall  = [[TILE_EMPTY]*CHUNK_SIZE for _ in range(CHUNK_SIZE)]
    for ly in range(CHUNK_SIZE):
        for lx in range(CHUNK_SIZE):
            wx = cx*CHUNK_SIZE + lx
            wy = cy*CHUNK_SIZE + ly
            n  = pnoise2(wx*0.1, wy*0.1, octaves=2)
            if n <= 0.0:
                wall[ly][lx] = TILE_DIRT
    return floor, wall

def load_chunks_around(px, py):
    pcx, _ = divmod(px, CHUNK_SIZE)
    pcy, _ = divmod(py, CHUNK_SIZE)
    needed = {
        (pcx+dx, pcy+dy)
        for dx in range(-LOAD_RADIUS, LOAD_RADIUS+1)
        for dy in range(-LOAD_RADIUS, LOAD_RADIUS+1)
    }
    # generate
    for coord in needed:
        if coord not in chunks:
            chunks[coord] = gen_chunk(*coord)
    # unload
    for coord in list(chunks):
        if coord not in needed:
            del chunks[coord]
    # ensure spawn open
    if (0,0) in chunks:
        f, w = chunks[(0,0)]
        f[0][0] = TILE_DIRT
        w[0][0] = TILE_EMPTY

def can_walk(tx, ty):
    cx, lx = divmod(tx, CHUNK_SIZE)
    cy, ly = divmod(ty, CHUNK_SIZE)
    floor, wall = chunks.get((cx, cy), (None, None))
    return floor and floor[ly][lx]==TILE_DIRT and wall[ly][lx]==TILE_EMPTY

# preload
load_chunks_around(player_tx, player_ty)

# === Main Loop ===
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    # continuous WASD movement
    keys = pygame.key.get_pressed()
    if not moving:
        ntx, nty = player_tx, player_ty
        if keys[pygame.K_a]: ntx -= 1
        elif keys[pygame.K_d]: ntx += 1
        elif keys[pygame.K_w]: nty -= 1
        elif keys[pygame.K_s]: nty += 1
        if (ntx, nty)!=(player_tx,player_ty) and can_walk(ntx,nty):
            player_tx, player_ty = ntx, nty
            target_px = player_tx * TILE_SIZE
            target_py = player_ty * TILE_SIZE
            moving = True

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        # zoom
        elif ev.type == pygame.MOUSEWHEEL:
            if ev.y>0: update_zoom(TILE_SIZE+4)
            else:      update_zoom(TILE_SIZE-4)
            load_chunks_around(player_tx, player_ty)

        # reset zoom
        elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==2:
            update_zoom(DEFAULT_TILE_SIZE)
            load_chunks_around(player_tx, player_ty)

        # dig/build
        elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button in (1,3):
            mx,my = ev.pos
            cam_x = SCREEN_W//2 - player_px
            cam_y = SCREEN_H//2 - player_py
            gx = (mx-cam_x)//TILE_SIZE
            gy = (my-cam_y)//TILE_SIZE
            ccx,lx = divmod(gx, CHUNK_SIZE)
            ccy,ly = divmod(gy, CHUNK_SIZE)
            floor, wall = chunks[(ccx,ccy)]
            if ev.button==1:  # dig
                if wall[ly][lx]==TILE_DIRT:
                    wall[ly][lx]=TILE_EMPTY
                elif floor[ly][lx]==TILE_DIRT:
                    floor[ly][lx]=TILE_EMPTY
            else:  # build
                if floor[ly][lx]==TILE_EMPTY:
                    floor[ly][lx]=TILE_DIRT
                elif wall[ly][lx]==TILE_EMPTY and floor[ly][lx]==TILE_DIRT:
                    wall[ly][lx]=TILE_DIRT

    # smooth movement
    if moving:
        dx = target_px - player_px
        dy = target_py - player_py
        dist = (dx*dx+dy*dy)**0.5
        step = move_speed * dt
        if step>=dist:
            player_px,player_py=target_px,target_py
            moving=False
        else:
            player_px += dx/dist*step
            player_py += dy/dist*step

    # reload & camera
    load_chunks_around(player_tx, player_ty)
    cam_x = SCREEN_W//2 - player_px
    cam_y = SCREEN_H//2 - player_py

    # draw world
    screen.fill((20,20,30))
    for (cx,cy),(floor,wall) in chunks.items():
        bx = cx*CHUNK_SIZE*TILE_SIZE + cam_x
        by = cy*CHUNK_SIZE*TILE_SIZE + cam_y
        for ly in range(CHUNK_SIZE):
            for lx in range(CHUNK_SIZE):
                px = bx + lx*TILE_SIZE
                py = by + ly*TILE_SIZE
                if not (-TILE_SIZE<px<SCREEN_W and -TILE_SIZE<py<SCREEN_H):
                    continue
                if floor[ly][lx]==TILE_DIRT:
                    screen.blit(floor_img,(px,py))
                if wall[ly][lx]==TILE_DIRT:
                    screen.blit(wall_img,(px,py))

    # draw player
    screen.blit(player_img,(SCREEN_W//2, SCREEN_H//2))

    # lighting
    dark = pygame.Surface((SCREEN_W,SCREEN_H),flags=pygame.SRCALPHA)
    dark.fill((0,0,0,200))
    dark.blit(light_mask,
              (SCREEN_W//2-LIGHT_RADIUS,SCREEN_H//2-LIGHT_RADIUS),
              special_flags=pygame.BLEND_RGBA_SUB)
    screen.blit(dark,(0,0))

    # debug grid
    if DEBUG_MODE:
        for wx in range(player_tx-DEBUG_GRID_RADIUS,player_tx+DEBUG_GRID_RADIUS+1):
            sx = wx*TILE_SIZE+cam_x
            pygame.draw.line(screen,DEBUG_GRID_COLOR,(sx,0),(sx,SCREEN_H),1)
            l=font.render(str(wx),True,DEBUG_GRID_COLOR)
            screen.blit(l,(sx+2,2))
        for wy in range(player_ty-DEBUG_GRID_RADIUS,player_ty+DEBUG_GRID_RADIUS+1):
            sy = wy*TILE_SIZE+cam_y
            pygame.draw.line(screen,DEBUG_GRID_COLOR,(0,sy),(SCREEN_W,sy),1)
            l=font.render(str(wy),True,DEBUG_GRID_COLOR)
            screen.blit(l,(2,sy+2))

    # coord readout
    cs = font.render(f"({player_tx},{player_ty})",True,(255,255,255))
    screen.blit(cs,(10,10))

    pygame.display.flip()

pygame.quit()
sys.exit()
