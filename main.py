# main.py

import pygame
import sys
import os

# === Debug Options ===
DEBUG_MODE       = True            # Set to True to show the red grid
DEBUG_GRID_COLOR = (255, 0, 0)      # Solid red lines

# === Constants ===
SCREEN_WIDTH   = 640
SCREEN_HEIGHT  = 480
TILE_SIZE      = 48
GRID_COLS      = SCREEN_WIDTH  // TILE_SIZE
GRID_ROWS      = SCREEN_HEIGHT // TILE_SIZE
FPS            = 60

ASSETS_DIR             = "assets"
FLOOR_TILE_FILENAME    = "tile_floor_dirt.png"
WALL_TILE_FILENAME     = "tile_wall_dirt.png"
PLAYER_SPRITE_FILENAME = "sprite_player.png"

TILE_EMPTY = 0
TILE_DIRT  = 1

# === Initialization ===
pygame.init()
pygame.key.set_repeat(200, 100)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock  = pygame.time.Clock()

# === Asset Loading ===
def load_sprite(filename: str) -> pygame.Surface:
    path = os.path.join(ASSETS_DIR, filename)
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))

floor_img  = load_sprite(FLOOR_TILE_FILENAME)
wall_img   = load_sprite(WALL_TILE_FILENAME)
player_img = load_sprite(PLAYER_SPRITE_FILENAME)

# === Lighting Mask ===
def make_light_mask(radius: int) -> pygame.Surface:
    mask = pygame.Surface((radius*2, radius*2), flags=pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        alpha = int(255 * (r / radius))
        pygame.draw.circle(mask, (0, 0, 0, alpha), (radius, radius), r)
    return mask

LIGHT_RADIUS = TILE_SIZE * 3
light_mask   = make_light_mask(LIGHT_RADIUS)

# === World Layers ===
floor_layer = [[TILE_DIRT for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
wall_layer  = [[TILE_EMPTY for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

# === Player State ===
player_x = GRID_COLS // 2
player_y = GRID_ROWS // 2

# === Helpers ===
def can_walk(x: int, y: int) -> bool:
    """Return True if (x,y) is in-bounds, has a floor, and no wall."""
    if not (0 <= x < GRID_COLS and 0 <= y < GRID_ROWS):
        return False
    return (floor_layer[y][x] == TILE_DIRT and wall_layer[y][x] == TILE_EMPTY)

# === Main Loop ===
running = True
while running:
    # — Event Handling —
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        # Movement with collision
        elif ev.type == pygame.KEYDOWN:
            nx, ny = player_x, player_y
            if ev.key == pygame.K_LEFT:  nx -= 1
            if ev.key == pygame.K_RIGHT: nx += 1
            if ev.key == pygame.K_UP:    ny -= 1
            if ev.key == pygame.K_DOWN:  ny += 1
            if can_walk(nx, ny):
                player_x, player_y = nx, ny

        # Dig (left-click) & Build (right-click)
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = ev.pos
            gx, gy = mx // TILE_SIZE, my // TILE_SIZE
            if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                # Dig: remove wall first, then floor
                if ev.button == 1:
                    if wall_layer[gy][gx] == TILE_DIRT:
                        wall_layer[gy][gx] = TILE_EMPTY
                    elif floor_layer[gy][gx] == TILE_DIRT:
                        floor_layer[gy][gx] = TILE_EMPTY
                # Build: floor if empty, else wall
                elif ev.button == 3:
                    if floor_layer[gy][gx] == TILE_EMPTY:
                        floor_layer[gy][gx] = TILE_DIRT
                    elif wall_layer[gy][gx] == TILE_EMPTY:
                        wall_layer[gy][gx] = TILE_DIRT

    # — Rendering World —
    screen.fill((30, 30, 40))  # background color

    # Draw floor & wall layers
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            px, py = col * TILE_SIZE, row * TILE_SIZE
            if floor_layer[row][col] == TILE_DIRT:
                screen.blit(floor_img, (px, py))
            if wall_layer[row][col] == TILE_DIRT:
                screen.blit(wall_img, (px, py))

    # Draw player
    screen.blit(player_img,
                (player_x * TILE_SIZE, player_y * TILE_SIZE))

    # — Dynamic Lighting Overlay —
    darkness = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SRCALPHA)
    darkness.fill((0, 0, 0, 200))
    mask_x = player_x * TILE_SIZE + TILE_SIZE//2 - LIGHT_RADIUS
    mask_y = player_y * TILE_SIZE + TILE_SIZE//2 - LIGHT_RADIUS
    darkness.blit(light_mask, (mask_x, mask_y), special_flags=pygame.BLEND_RGBA_SUB)
    screen.blit(darkness, (0, 0))

    # — Debug Grid Overlay —
    if DEBUG_MODE:
        # vertical lines
        for x in range(GRID_COLS + 1):
            pygame.draw.line(
                screen,
                DEBUG_GRID_COLOR,
                (x * TILE_SIZE, 0),
                (x * TILE_SIZE, SCREEN_HEIGHT),
                1
            )
        # horizontal lines
        for y in range(GRID_ROWS + 1):
            pygame.draw.line(
                screen,
                DEBUG_GRID_COLOR,
                (0, y * TILE_SIZE),
                (SCREEN_WIDTH, y * TILE_SIZE),
                1
            )

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
