# main.py

import sys
import pygame

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

    # ── Load assets & prepare rendering ──
    assets.init_assets()               # load original images now that display is ready
    render.init_render()               # initialize fonts, etc.

    # ── Initial zoom & player setup ──
    default_ts   = settings.SCREEN_W // settings.DEFAULT_TILES_ACROSS
    player_state = player.init_player(default_ts)
    assets.update_zoom(default_ts)
    world.load_chunks(player_state['tx'], player_state['ty'])

    # ── Compute zoom bounds in pixels ──
    min_px = settings.SCREEN_W // settings.MIN_TILES_ACROSS
    max_px = settings.SCREEN_W // settings.MAX_TILES_ACROSS

    # ── Spawn‐protection warning ──
    warn_timer    = 0.0
    WARN_DURATION = 1.5
    warn_font     = pygame.font.SysFont(None, 24)

    clock   = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        # ── Event handling ──
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            # Zoom in/out with mouse wheel
            elif ev.type == pygame.MOUSEWHEEL:
                delta   = 4 if ev.y > 0 else -4
                desired = assets.TILE_SIZE + delta
                size    = max(min_px, min(max_px, desired))
                if size != assets.TILE_SIZE:
                    assets.update_zoom(size)
                    world.load_chunks(player_state['tx'], player_state['ty'])
                    # Re‐sync player pixel position
                    px = player_state['tx'] * assets.TILE_SIZE
                    py = player_state['ty'] * assets.TILE_SIZE
                    player_state['px'] = px
                    player_state['py'] = py
                    player_state['target_x'] = px
                    player_state['target_y'] = py

            # Reset zoom on middle‐click
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 2:
                if assets.TILE_SIZE != default_ts:
                    assets.update_zoom(default_ts)
                    world.load_chunks(player_state['tx'], player_state['ty'])
                    px = player_state['tx'] * assets.TILE_SIZE
                    py = player_state['ty'] * assets.TILE_SIZE
                    player_state['px'] = px
                    player_state['py'] = py
                    player_state['target_x'] = px
                    player_state['target_y'] = py

            # Dig / Build with left/right click
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3):
                mx, my = ev.pos
                cam_x   = settings.SCREEN_W//2 - player_state['px']
                cam_y   = settings.SCREEN_H//2 - player_state['py']

                gx = int((mx - cam_x) // assets.TILE_SIZE)
                gy = int((my - cam_y) // assets.TILE_SIZE)

                # spawn protection
                if abs(gx) <= settings.SPAWN_PROTECT_WIDTH and abs(gy) <= settings.SPAWN_PROTECT_HEIGHT:
                    warn_timer = WARN_DURATION
                    continue

                ccx, lx = divmod(gx, settings.CHUNK_SIZE)
                ccy, ly = divmod(gy, settings.CHUNK_SIZE)
                floor, wall = world.chunks[(ccx, ccy)]

                # Dig
                if ev.button == 1:
                    broken = False
                    if wall[ly][lx] == settings.TILE_DIRT:
                        wall[ly][lx] = settings.TILE_EMPTY
                        broken = True
                    elif floor[ly][lx] == settings.TILE_DIRT:
                        floor[ly][lx] = settings.TILE_EMPTY
                        broken = True
                    if broken:
                        slot = player_state['selected_slot']
                        itm  = player_state['hotbar'][slot]
                        if itm and itm['type'] == 'dirt':
                            itm['count'] += 1
                        else:
                            player_state['hotbar'][slot] = {
                                'type': 'dirt',
                                'count': 1,
                                'image': assets.floor_img
                            }

                # Build
                else:  # ev.button == 3
                    slot = player_state['selected_slot']
                    itm  = player_state['hotbar'][slot]
                    if itm and itm['count'] > 0 and itm['type'] == 'dirt':
                        if floor[ly][lx] == settings.TILE_EMPTY:
                            floor[ly][lx] = settings.TILE_DIRT
                            itm['count'] -= 1
                        elif floor[ly][lx] == settings.TILE_DIRT and wall[ly][lx] == settings.TILE_EMPTY:
                            wall[ly][lx] = settings.TILE_DIRT
                            itm['count'] -= 1
                        if itm['count'] == 0:
                            player_state['hotbar'][slot] = None

        # ── Update movement & chunks ──
        player.update_input(player_state, assets.TILE_SIZE, dt)
        world.load_chunks(player_state['tx'], player_state['ty'])

        # ── Compute wall‐depth map for interior shading ──
        wall_depths = world.compute_wall_depths(world.chunks)

        # ── Render everything ──
        render.draw_world(screen, player_state, world.chunks, wall_depths)

        # ── Spawn‐protect warning ──
        if warn_timer > 0:
            surf = warn_font.render("Cannot Break Spawn Area", True, (255,50,50))
            x = (settings.SCREEN_W - surf.get_width()) // 2
            screen.blit(surf, (x, 10))
            warn_timer -= dt

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
