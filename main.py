# main.py

import pygame
import sys
import settings
import assets
import world
import player
import render

def main():
    # ── Initialize Pygame & screen ──
    pygame.init()
    info = pygame.display.Info()
    settings.SCREEN_W, settings.SCREEN_H = info.current_w, info.current_h
    screen = pygame.display.set_mode(
        (settings.SCREEN_W, settings.SCREEN_H),
        pygame.FULLSCREEN
    )

    # ── Initialize rendering & subsystems ──
    render.init_render()
    default_ts = settings.SCREEN_W // settings.DEFAULT_TILES_ACROSS
    player_state = player.init_player(default_ts)
    assets.update_zoom(default_ts)
    world.load_chunks(player_state['tx'], player_state['ty'])

    # precompute zoom bounds in pixels
    min_px = settings.SCREEN_W // settings.MIN_TILES_ACROSS
    max_px = settings.SCREEN_W // settings.MAX_TILES_ACROSS

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            # Zoom in/out with mouse wheel
            elif ev.type == pygame.MOUSEWHEEL:
                delta = 4 if ev.y > 0 else -4
                desired = assets.TILE_SIZE + delta
                size = max(min_px, min(max_px, desired))
                if size != assets.TILE_SIZE:
                    assets.update_zoom(size)
                    world.load_chunks(player_state['tx'], player_state['ty'])
                    # resync pixel position
                    player_state['px'] = player_state['tx'] * assets.TILE_SIZE
                    player_state['py'] = player_state['ty'] * assets.TILE_SIZE
                    player_state['target_x'] = player_state['px']
                    player_state['target_y'] = player_state['py']

            # Reset zoom to default (middle click)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 2:
                if assets.TILE_SIZE != default_ts:
                    assets.update_zoom(default_ts)
                    world.load_chunks(player_state['tx'], player_state['ty'])
                    player_state['px'] = player_state['tx'] * assets.TILE_SIZE
                    player_state['py'] = player_state['ty'] * assets.TILE_SIZE
                    player_state['target_x'] = player_state['px']
                    player_state['target_y'] = player_state['py']

            # Dig/Build (left/right)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3):
                mx, my = ev.pos
                cam_x = settings.SCREEN_W // 2 - player_state['px']
                cam_y = settings.SCREEN_H // 2 - player_state['py']

                # cast to int to avoid float indices
                gx = int((mx - cam_x) // assets.TILE_SIZE)
                gy = int((my - cam_y) // assets.TILE_SIZE)

                ccx, lx = divmod(gx, settings.CHUNK_SIZE)
                ccy, ly = divmod(gy, settings.CHUNK_SIZE)
                floor, wall = world.chunks[(ccx, ccy)]

                if ev.button == 1:  # dig
                    if wall[ly][lx] == settings.TILE_DIRT:
                        wall[ly][lx] = settings.TILE_EMPTY
                    elif floor[ly][lx] == settings.TILE_DIRT:
                        floor[ly][lx] = settings.TILE_EMPTY

                elif ev.button == 3:  # build
                    if floor[ly][lx] == settings.TILE_EMPTY:
                        floor[ly][lx] = settings.TILE_DIRT
                    elif (floor[ly][lx] == settings.TILE_DIRT
                          and wall[ly][lx] == settings.TILE_EMPTY):
                        wall[ly][lx] = settings.TILE_DIRT

        # Update smooth movement
        player.update_input(player_state, assets.TILE_SIZE, dt)

        # Draw everything
        render.draw_world(screen, player_state, world.chunks)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
