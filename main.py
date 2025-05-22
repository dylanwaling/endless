# main.py

import pygame, sys, os
from noise import pnoise2  # pip install noise

# === Debug Options ===
DEBUG_MODE       = True
DEBUG_GRID_COLOR = (255, 0, 0)
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

# — Pygame Init —
pygame.init()
pygame.key.set_repeat(200, 100)  # hold arrow keys
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock  = pygame.time.Clock()
font   = pygame.font.SysFont(None, 18)

# — Load & scale sprites —
def load_sprite(fn):
    img = pygame.image.load(os.path.join(ASSETS_DIR, fn)).convert_alpha()
    return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

floor_img  = load_sprite(FLOOR_TILE_FILE)
wall_img   = load_sprite(WALL_TILE_FILE)
player_img = load_sprite(PLAYER_SPRITE_FILE)

# — Light mask for torch effect —
def make_light_mask(r):
    surf = pygame.Surface((r*2, r*2), flags=pygame.SRCALPHA)
    for radius in range(r, 0, -1):
        alpha = int(255 * (radius / r))
        pygame.draw.circle(surf, (0,0,0,alpha), (r, r), radius)
    return surf

LIGHT_RADIUS = TILE_SIZE * 3
light_mask   = make_light_mask(LIGHT_RADIUS)

# — Chunk storage: (cx,cy) → (floor,wall) arrays —
chunks = {}

def gen_chunk(cx, cy):
    floor = [[TILE_EMPTY]*CHUNK_SIZE for _ in range(CHUNK_SIZE)]
    wall  = [[TILE_EMPTY]*CHUNK_SIZE for _ in range(CHUNK_SIZE)]
    for ly in range(CHUNK_SIZE):
        for lx in range(CHUNK_SIZE):
            wx = cx*CHUNK_SIZE + lx
            wy = cy*CHUNK_SIZE + ly
            n = pnoise2(wx*0.1, wy*0.1, octaves=2)
            if n > 0.0:
                floor[ly][lx] = TILE_DIRT
    return floor, wall

def load_chunks_around(px, py):
    pcx, plx = divmod(px, CHUNK_SIZE)
    pcy, ply = divmod(py, CHUNK_SIZE)
    needed = set()
    for dx in range(-LOAD_RADIUS, LOAD_RADIUS+1):
        for dy in range(-LOAD_RADIUS, LOAD_RADIUS+1):
            needed.add((pcx+dx, pcy+dy))
    for coord in needed:
        if coord not in chunks:
            chunks[coord] = gen_chunk(*coord)
    for coord in list(chunks):
        if coord not in needed:
            del chunks[coord]

# — Player state (in tile coords) —
player_x = CHUNK_SIZE//2
player_y = CHUNK_SIZE//2

def can_walk(x, y):
    cx, lx = divmod(x, CHUNK_SIZE)
    cy, ly = divmod(y, CHUNK_SIZE)
    floor, wall = chunks.get((cx,cy), (None,None))
    if floor is None: return False
    return floor[ly][lx] == TILE_DIRT and wall[ly][lx] == TILE_EMPTY

# — Main Loop —
running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        # continuous movement
        elif ev.type == pygame.KEYDOWN:
            nx, ny = player_x, player_y
            if ev.key == pygame.K_LEFT:  nx -= 1
            if ev.key == pygame.K_RIGHT: nx += 1
            if ev.key == pygame.K_UP:    ny -= 1
            if ev.key == pygame.K_DOWN:  ny += 1
            if can_walk(nx, ny):
                player_x, player_y = nx, ny

        # dig/place
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = ev.pos
            # convert screen→world tile
            center_x = SCREEN_W//2
            center_y = SCREEN_H//2
            world_x = (mx - center_x)//TILE_SIZE + player_x
            world_y = (my - center_y)//TILE_SIZE + player_y
            cx, lx = divmod(world_x, CHUNK_SIZE)
            cy, ly = divmod(world_y, CHUNK_SIZE)
            floor, wall = chunks[(cx,cy)]
            if ev.button == 1:
                # dig wall then floor
                if wall[ly][lx] != TILE_EMPTY:
                    wall[ly][lx] = TILE_EMPTY
                else:
                    floor[ly][lx] = TILE_EMPTY
            elif ev.button == 3:
                # build floor then wall
                if floor[ly][lx] == TILE_EMPTY:
                    floor[ly][lx] = TILE_DIRT
                else:
                    wall[ly][lx] = TILE_DIRT

    # load nearby chunks
    load_chunks_around(player_x, player_y)

    # camera offsets so player is at center
    center_x = SCREEN_W//2
    center_y = SCREEN_H//2
    cam_x = center_x - player_x*TILE_SIZE
    cam_y = center_y - player_y*TILE_SIZE

    # draw background
    screen.fill((20,20,30))

    # draw chunks
    for (cx, cy), (floor, wall) in chunks.items():
        base_x = cx*CHUNK_SIZE*TILE_SIZE + cam_x
        base_y = cy*CHUNK_SIZE*TILE_SIZE + cam_y
        for ly in range(CHUNK_SIZE):
            for lx in range(CHUNK_SIZE):
                px = base_x + lx*TILE_SIZE
                py = base_y + ly*TILE_SIZE
                if not (-TILE_SIZE < px < SCREEN_W and -TILE_SIZE < py < SCREEN_H):
                    continue
                if floor[ly][lx] == TILE_DIRT:
                    screen.blit(floor_img, (px, py))
                if wall[ly][lx] == TILE_DIRT:
                    screen.blit(wall_img,  (px, py))

    # draw player at center
    screen.blit(player_img, (center_x, center_y))

    # lighting mask
    darkness = pygame.Surface((SCREEN_W,SCREEN_H), flags=pygame.SRCALPHA)
    darkness.fill((0,0,0,200))
    darkness.blit(light_mask, (center_x-LIGHT_RADIUS, center_y-LIGHT_RADIUS),
                  special_flags=pygame.BLEND_RGBA_SUB)
    screen.blit(darkness, (0,0))

    # debug grid anchored to world
    if DEBUG_MODE:
        # vertical, world-aligned
        for wx in range(player_x-DEBUG_GRID_RADIUS, player_x+DEBUG_GRID_RADIUS+1):
            sx = wx*TILE_SIZE + cam_x
            pygame.draw.line(screen, DEBUG_GRID_COLOR, (sx,0),(sx,SCREEN_H),1)
            label = font.render(str(wx), True, DEBUG_GRID_COLOR)
            screen.blit(label, (sx+2, 2))
        # horizontal
        for wy in range(player_y-DEBUG_GRID_RADIUS, player_y+DEBUG_GRID_RADIUS+1):
            sy = wy*TILE_SIZE + cam_y
            pygame.draw.line(screen, DEBUG_GRID_COLOR, (0,sy),(SCREEN_W,sy),1)
            label = font.render(str(wy), True, DEBUG_GRID_COLOR)
            screen.blit(label, (2, sy+2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
