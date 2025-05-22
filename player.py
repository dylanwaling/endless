# player.py

import sys
import pygame
import settings
import assets
import world

def init_player(start_tile_size):
    # initial tile coords
    state = {
        'tx': 0, 'ty': 0,             # tile coords
        'px': 0, 'py': 0,             # pixel coords
        'target_x': 0, 'target_y': 0, # movement target
        'moving': False,
        'hotbar': [None]*settings.HOTBAR_SLOTS,
        'selected_slot': 0,
    }
    # sync pixels to tile center at (0,0)
    ts = start_tile_size
    state['px'] = state['tx'] * ts
    state['py'] = state['ty'] * ts
    state['target_x'] = state['px']
    state['target_y'] = state['py']
    return state

def update_input(state, TILE_SIZE, dt):
    # handle quit here
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # you can forward other events (zoom, dig/build) back to main if desired

    # continuous WASD movement
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

    # smooth movement interpolation
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
