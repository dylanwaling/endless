import pygame
from settings import SPEED_TILES_PER_SEC
from world import collide, load_chunks

def init_player(default_tile_size):
    return {
        'tx': 0, 'ty': 0,
        'px': 0, 'py': 0,
        'target_x': 0, 'target_y': 0,
        'moving': False,
        'speed': SPEED_TILES_PER_SEC * default_tile_size
    }

def update_input(player, tile_size, dt):
    if not player['moving']:
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] - keys[pygame.K_a])
        dy = (keys[pygame.K_s] - keys[pygame.K_w])
        ntx = player['tx'] + dx
        nty = player['ty'] + dy
        if (dx or dy) and collide(ntx, nty):
            player['tx'], player['ty'] = ntx, nty
            player['target_x'] = ntx * tile_size
            player['target_y'] = nty * tile_size
            player['moving'] = True
    else:
        dx = player['target_x'] - player['px']
        dy = player['target_y'] - player['py']
        dist = (dx*dx + dy*dy)**0.5
        step = player['speed'] * dt
        if step >= dist:
            player['px'], player['py'] = player['target_x'], player['target_y']
            player['moving'] = False
            load_chunks(player['tx'], player['ty'])
        else:
            player['px'] += dx/dist * step
            player['py'] += dy/dist * step
