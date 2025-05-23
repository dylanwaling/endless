import sys
import pygame
from engine import settings
from engine import assets
from game import world

# ──────────────────────────────────────────────────────────────
# Player State Initialization
# ──────────────────────────────────────────────────────────────

def init_player(start_tile_size):
    """
    Initialize player state dictionary.
    """
    state = {
        'tx': 0, 'ty': 0,             # tile coordinates
        'px': 0, 'py': 0,             # pixel coordinates
        'target_x': 0, 'target_y': 0, # move target in pixels
        'moving': False,
        'hotbar': [None] * settings.HOTBAR_SLOTS,
        'selected_slot': 0,
    }
    ts = start_tile_size
    state['px'] = state['tx'] * ts
    state['py'] = state['ty'] * ts
    state['target_x'] = state['px']
    state['target_y'] = state['py']
    return state

# ──────────────────────────────────────────────────────────────
# Input & Movement
# ──────────────────────────────────────────────────────────────

def update_input(state, tile_size, dt):
    """
    Handle player input and movement.
    """
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        pygame.event.post(ev)

    # WASD movement
    if not state['moving']:
        ntx, nty = state['tx'], state['ty']
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            ntx -= 1
        elif keys[pygame.K_d]:
            ntx += 1
        elif keys[pygame.K_w]:
            nty -= 1
        elif keys[pygame.K_s]:
            nty += 1

        if (ntx, nty) != (state['tx'], state['ty']) and world.can_walk(ntx, nty):
            state['tx'], state['ty'] = ntx, nty
            state['target_x'] = ntx * tile_size
            state['target_y'] = nty * tile_size
            state['moving'] = True

    # Smooth pixel interpolation
    if state['moving']:
        dx = state['target_x'] - state['px']
        dy = state['target_y'] - state['py']
        dist = (dx * dx + dy * dy) ** 0.5
        step = assets.move_speed * dt
        if step >= dist:
            state['px'], state['py'] = state['target_x'], state['target_y']
            state['moving'] = False
        else:
            state['px'] += dx / dist * step
            state['py'] += dy / dist * step

    # Hotbar number keys 1–9,0
    keys = pygame.key.get_pressed()
    for i in range(settings.HOTBAR_SLOTS):
        key = pygame.K_1 + i if i < 9 else pygame.K_0
        if keys[key]:
            state['selected_slot'] = i

# ──────────────────────────────────────────────────────────────
# Hotbar & Inventory
# ──────────────────────────────────────────────────────────────

def add_to_hotbar(state, item_type, image):
    """
    Add one block of item_type to the selected hotbar slot, stacking if possible.
    """
    slot_idx = state['selected_slot']
    cur = state['hotbar'][slot_idx]
    if isinstance(cur, dict) and cur.get('type') == item_type:
        cur['count'] += 1
    else:
        state['hotbar'][slot_idx] = {
            'type':  item_type,
            'count': 1,
            'image': image
        }

# ──────────────────────────────────────────────────────────────
# Block Placement
# ──────────────────────────────────────────────────────────────

def place_dirt(state, gx, gy, floor, wall):
    """
    On right-click:
      1) Place a floor if that spot is empty.
      2) Else if there's a floor and no wall, place a wall.
    Consumes one dirt from the selected hotbar slot.
    """
    slot_idx = state['selected_slot']
    slot = state['hotbar'][slot_idx]

    # Must have dirt
    if not (isinstance(slot, dict) and slot.get('type') == 'dirt' and slot.get('count', 0) > 0):
        return

    lx, ly = gx % settings.CHUNK_SIZE, gy % settings.CHUNK_SIZE

    # 1) Place floor
    if floor[ly][lx] == settings.TILE_EMPTY:
        floor[ly][lx] = settings.TILE_DIRT
        slot['count'] -= 1

    # 2) Else place wall (only if floor exists)
    elif floor[ly][lx] == settings.TILE_DIRT and wall[ly][lx] == settings.TILE_EMPTY:
        wall[ly][lx] = settings.TILE_DIRT
        slot['count'] -= 1

    # Clear empty slot
    if slot['count'] <= 0:
        state['hotbar'][slot_idx] = None
