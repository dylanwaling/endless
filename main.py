# main.py

import pygame
import sys

import settings
import assets
import world
import player
import render

def main():
    # ── Init Pygame & Screen ──
    pygame.init()
    info = pygame.display.Info()
    settings.SCREEN_W, settings.SCREEN_H = info.current_w, info.current_h
    screen = pygame.display.set_mode(
        (settings.SCREEN_W, settings.SCREEN_H),
        pygame.FULLSCREEN
    )

    # ── Init Rendering & Subsystems ──
    render.init_render()
    default_ts = settings.SCREEN_W // settings.DEFAULT_TILES_ACROSS
    player_state = player.init_player(default_ts)
    assets.update_zoom(default_ts)
    world.load_chunks(player_state['tx'], player_state['ty'])

    # Precompute zoom bounds in pixels
    min_px = settings.SCREEN_W // settings.MIN_TILES_ACROSS
    max_px = settings.SCREEN_W // settings.MAX_TILES_ACROSS

    # Warning timer
    warn_timer   = 0.0
    WARN_DURATION = 1.5  # seconds
    warn_font    = pygame.font.SysFont(None, 24)

    clock   = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            # Zoom in/out
            elif ev.type == pygame.MOUSEWHEEL:
                delta  = 4 if ev.y > 0 else -4
                desired = assets.TILE_SIZE + delta
                size    = max(min_px, min(max_px, desired))
                if size != assets.TILE_SIZE:
                    assets.update_zoom(size)
                    world.load_chunks(player_state['tx'], player_state['ty'])
                    # resync player pixel coords
                    player_state['px']       = player_state['tx'] * assets.TILE_SIZE
                    player_state['py']       = player_state['ty'] * assets.TILE_SIZE
                    player_state['target_x'] = player_state['px']
                    player_state['target_y'] = player_state['py']

            # Reset zoom (middle click)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 2:
                if assets.TILE_SIZE != default_ts:
                    assets.update_zoom(default_ts)
                    world.load_chunks(player_state['tx'], player_state['ty'])
                    player_state['px']       = player_state['tx'] * assets.TILE_SIZE
                    player_state['py']       = player_state['ty'] * assets.TILE_SIZE
                    player_state['target_x'] = player_state['px']
                    player_state['target_y'] = player_state['py']

            # Dig/Build
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3):
                mx, my = ev.pos
                cam_x   = settings.SCREEN_W // 2 - player_state['px']
                cam_y   = settings.SCREEN_H // 2 - player_state['py']

                gx = int((mx - cam_x) // assets.TILE_SIZE)
                gy = int((my - cam_y) // assets.TILE_SIZE)

                # spawn protection check
                if abs(gx) <= settings.SPAWN_PROTECT_WIDTH and \
                   abs(gy) <= settings.SPAWN_PROTECT_HEIGHT:
                    warn_timer = WARN_DURATION
                    continue

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
                    elif (floor[ly][lx] == settings.TILE_DIRT and
                          wall[ly][lx]  == settings.TILE_EMPTY):
                        wall[ly][lx] = settings.TILE_DIRT

        # Smooth movement
        player.update_input(player_state, assets.TILE_SIZE, dt)

        # Draw world
        render.draw_world(screen, player_state, world.chunks)

        # Draw warning if needed
        if warn_timer > 0:
            txt = "Cannot Break Spawn Area"
            surf = warn_font.render(txt, True, (255,50,50))
            x = settings.SCREEN_W//2 - surf.get_width()//2
            screen.blit(surf, (x, 10))
            warn_timer -= dt

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
