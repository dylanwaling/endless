import sys
import pygame
from engine import settings, assets
from game import world, player

# ──────────────────────────────────────────────────────────────
# Zoom Handling
# ──────────────────────────────────────────────────────────────

def set_zoom(player_state: dict, new_size: int) -> None:
    """
    Update zoom level and reposition player accordingly.
    """
    assets.update_zoom(new_size)
    world.load_chunks(player_state['tx'], player_state['ty'])
    px = player_state['tx'] * assets.TILE_SIZE
    py = player_state['ty'] * assets.TILE_SIZE
    player_state.update({
        'px': px,
        'py': py,
        'target_x': px,
        'target_y': py
    })

# ──────────────────────────────────────────────────────────────
# Digging & Building
# ──────────────────────────────────────────────────────────────

def handle_dig_build(
    ev: pygame.event.Event,
    player_state: dict,
    warn_timer: int,
    WARN_DURATION: int
) -> tuple[int, bool]:
    """
    Handle digging and building logic.
    Returns (warn_timer, block_changed).
    """
    mx, my = ev.pos
    cam_x = settings.SCREEN_W // 2 - player_state['px']
    cam_y = settings.SCREEN_H // 2 - player_state['py']
    gx = int((mx - cam_x) // assets.TILE_SIZE)
    gy = int((my - cam_y) // assets.TILE_SIZE)

    # Spawn protection
    if abs(gx) <= settings.SPAWN_PROTECT_WIDTH and abs(gy) <= settings.SPAWN_PROTECT_HEIGHT:
        return WARN_DURATION, False

    ccx, lx = divmod(gx, settings.CHUNK_SIZE)
    ccy, ly = divmod(gy, settings.CHUNK_SIZE)
    chunk = world.chunks.get((ccx, ccy))
    if not chunk:
        return warn_timer, False
    floor, wall = chunk

    # Ensure indices valid
    if not (0 <= lx < settings.CHUNK_SIZE and 0 <= ly < settings.CHUNK_SIZE):
        return warn_timer, False

    block_changed = False
    if ev.button == 1:
        # DIG: remove wall first, then floor
        if wall[ly][lx] == settings.TILE_DIRT:
            wall[ly][lx] = settings.TILE_EMPTY
            player.add_to_hotbar(player_state, 'dirt', assets.floor_img)
            block_changed = True
        elif floor[ly][lx] == settings.TILE_DIRT:
            floor[ly][lx] = settings.TILE_EMPTY
            player.add_to_hotbar(player_state, 'dirt', assets.floor_img)
            block_changed = True
    elif ev.button == 3:
        # BUILD: place dirt on floor or wall
        placed = player.place_dirt(player_state, gx, gy, floor, wall)
        if placed:
            block_changed = True
    return warn_timer, block_changed

# ──────────────────────────────────────────────────────────────
# Main Event Loop
# ──────────────────────────────────────────────────────────────

def handle_events(
    player_state: dict,
    default_tile_size: int,
    min_px: int,
    max_px: int,
    warn_timer: int,
    WARN_DURATION: int
) -> tuple[int, bool]:
    """
    Handle all pygame events for the main game loop.
    Returns (warn_timer, block_changed).
    """
    block_changed = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEWHEEL:
            delta = 4 if event.y > 0 else -4
            desired = assets.TILE_SIZE + delta
            new_size = max(min_px, min(max_px, desired))
            if new_size != assets.TILE_SIZE:
                set_zoom(player_state, new_size)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:
                if assets.TILE_SIZE != default_tile_size:
                    set_zoom(player_state, default_tile_size)
            elif event.button in (1, 3):
                warn_timer, changed = handle_dig_build(event, player_state, warn_timer, WARN_DURATION)
                if changed:
                    block_changed = True
    return warn_timer, block_changed