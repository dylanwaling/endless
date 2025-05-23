# player.py

import sys
import pygame
import settings
import assets
import world

def init_player(start_tile_size):
    state = {
        'tx': 0, 'ty': 0,
        'px': 0, 'py': 0,
        'target_x': 0, 'target_y': 0,
        'moving': False,
        'hotbar': [None]*settings.HOTBAR_SLOTS,
        'selected_slot': 0,
    }
    ts = start_tile_size
    state['px'] = state['tx'] * ts
    state['py'] = state['ty'] * ts
    state['target_x'] = state['px']
    state['target_y'] = state['py']
    return state

def update_input(state, TILE_SIZE, dt):
    keys = pygame.key.get_pressed()
    if not state['moving']:
        ntx, nty = state['tx'], state['ty']
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
            state['target_x'] = ntx * TILE_SIZE
            state['target_y'] = nty * TILE_SIZE
            state['moving'] = True

    if state['moving']:
        dx = state['target_x'] - state['px']
        dy = state['target_y'] - state['py']
        dist = (dx*dx + dy*dy) ** 0.5
        step = assets.move_speed * dt
        if step >= dist:
            state['px'], state['py'] = state['target_x'], state['target_y']
            state['moving'] = False
        else:
            state['px'] += dx / dist * step
            state['py'] += dy / dist * step

    for i in range(settings.HOTBAR_SLOTS):
        if keys[getattr(pygame, f'K_{i+1}' if i < 9 else 'K_0')]:
            state['selected_slot'] = i

def add_to_hotbar(item, image):
    """
    Adds an item to the player's hotbar, stacking if possible.
    """
    import inspect
    # Find the caller's frame to get the player_state variable
    frame = inspect.currentframe().f_back
    player_state = frame.f_locals.get('player_state') or frame.f_locals.get('player')
    if player_state is None:
        return

    # Try to stack with existing
    for slot in player_state['hotbar']:
        if slot and slot['item'] == item:
            slot['count'] += 1
            return
    # Find empty slot
    for i in range(len(player_state['hotbar'])):
        if player_state['hotbar'][i] is None:
            player_state['hotbar'][i] = {'item': item, 'image': image, 'count': 1}
            return

def try_place_from_hotbar(gx, gy, floor, wall, layer='wall'):
    import inspect
    frame = inspect.currentframe().f_back
    player_state = frame.f_locals.get('player_state') or frame.f_locals.get('player')
    print(f"try_place_from_hotbar called with layer={layer}")
    if player_state is None:
        return

    slot = player_state['hotbar'][player_state['selected_slot']]
    if not slot or slot['item'] != 'dirt':
        print("No dirt in selected slot!")
        return

    lx, ly = gx % settings.CHUNK_SIZE, gy % settings.CHUNK_SIZE

    if layer == 'wall':
        print(f"Trying to place wall at ({lx},{ly}): wall={wall[ly][lx]}, floor={floor[ly][lx]}")
        if wall[ly][lx] == settings.TILE_EMPTY:
            if floor[ly][lx] == settings.TILE_DIRT:
                wall[ly][lx] = settings.TILE_DIRT
                slot['count'] -= 1
                print("Wall placed at", lx, ly)
            else:
                print("Can't place wall: no floor present at", lx, ly)
        else:
            print("Can't place wall: wall already present at", lx, ly)
    elif layer == 'floor':
        if floor[ly][lx] == settings.TILE_EMPTY:
            floor[ly][lx] = settings.TILE_DIRT
            slot['count'] -= 1
            print("Floor placed at", lx, ly)

    if slot['count'] <= 0:
        player_state['hotbar'][player_state['selected_slot']] = None

def draw_chunks(chunks, screen, ts):
    for (cx,cy),(floor,wall) in chunks.items():
        bx, by = cx * settings.CHUNK_SIZE * ts, cy * settings.CHUNK_SIZE * ts
        for ly in range(settings.CHUNK_SIZE):
            for lx in range(settings.CHUNK_SIZE):
                px, py = bx+lx*ts, by+ly*ts
                if px+ts<0 or px>settings.SCREEN_W or py+ts<0 or py>settings.SCREEN_H:
                    continue
                if floor[ly][lx] == settings.TILE_DIRT:
                    screen.blit(assets.floor_img, (px, py))
                if wall[ly][lx] == settings.TILE_DIRT:
                    screen.blit(assets.wall_img, (px, py))
