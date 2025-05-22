# player.py

import pygame
import settings
from world import collide, load_chunks

def init_player(default_tile_size):
    """Return initial player state dict, including hotbar."""
    return {
        'tx': 0, 'ty': 0,               # tile coords
        'px': 0.0, 'py': 0.0,           # pixel coords
        'target_x': 0.0, 'target_y': 0.0,# movement target in pixels
        'moving': False,                # currently tweening?
        'speed': settings.SPEED_TILES_PER_SEC * default_tile_size,
        # hotbar state:
        'hotbar': [None] * settings.HOTBAR_SLOTS,
        'selected_slot': 0,
    }

def update_input(player, tile_size, dt):
    """
    Handle continuous WASD movement toward next tile, plus
    number-keys 1–0 to pick hotbar slots.
    """
    # movement
    keys = pygame.key.get_pressed()
    if not player['moving']:
        ntx, nty = player['tx'], player['ty']
        if keys[pygame.K_a]:
            ntx -= 1
        elif keys[pygame.K_d]:
            ntx += 1
        elif keys[pygame.K_w]:
            nty -= 1
        elif keys[pygame.K_s]:
            nty += 1

        if (ntx, nty) != (player['tx'], player['ty']) and collide(ntx, nty):
            player['tx'], player['ty'] = ntx, nty
            player['target_x'] = ntx * tile_size
            player['target_y'] = nty * tile_size
            player['moving'] = True

    # slot selection: 1–9, then 0 → slot 9
    for i in range(settings.HOTBAR_SLOTS):
        key = pygame.K_1 + i if i < 9 else pygame.K_0
        if keys[key]:
            player['selected_slot'] = i
            break

    # smooth move tweening
    if player['moving']:
        dx = player['target_x'] - player['px']
        dy = player['target_y'] - player['py']
        dist = (dx*dx + dy*dy) ** 0.5
        step = player['speed'] * dt
        if step >= dist:
            player['px'], player['py'] = player['target_x'], player['target_y']
            player['moving'] = False
            load_chunks(player['tx'], player['ty'])
        else:
            player['px'] += dx / dist * step
            player['py'] += dy / dist * step
