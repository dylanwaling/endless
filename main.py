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
    default_ts   = settings.SCREEN_W // settings.DEFAULT_TILES_ACROSS
    player_state = player.init_player(default_ts)
    assets.update_zoom(default_ts)
    world.load_chunks(player_state['tx'], player_state['ty'])

    # Precompute zoom bounds in pixels
    min_px = settings.SCREEN_W // settings.MIN_TILES_ACROSS
    max_px = settings.SCREEN_W // settings.MAX_TILES_ACROSS

    # Warning timer
    warn_timer    = 0.0
    WARN_DURATION = 1.5  # seconds
    warn_font     = pygame.font.SysFont(None, 24)

    clock   = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(settings.FPS) / 1000.0

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
                    # resync pixel position
                    px = player_state['tx'] * assets.TILE_SIZE
                    py = player_state['ty'] * assets.TILE_SIZE
                    player_state.update(px=px, py=py,
                                        target_x=px, target_y=py)

            # Reset zoom to default (middle click)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 2:
                if assets.TILE_SIZE != default_ts:
                    assets.update_zoom(default_ts)
                    world.load_chunks(player_state['tx'], player_state['ty'])
                    px = player_state['tx'] * assets.TILE_SIZE
                    py = player_state['ty'] * assets.TILE_SIZE
                    player_state.update(px=px, py=py,
                                        target_x=px, target_y=py)

            # Dig/Build (left/right)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3):
                mx, my = ev.pos
                cam_x   = settings.SCREEN_W // 2 - player_state['px']
                cam_y   = settings.SCREEN_H // 2 - player_state['py']

                # compute world tile coords
                gx = int((mx - cam_x) // assets.TILE_SIZE)
                gy = int((my - cam_y) // assets.TILE_SIZE)

                # spawn protection
                if abs(gx) <= settings.SPAWN_PROTECT_WIDTH and \
                   abs(gy) <= settings.SPAWN_PROTECT_HEIGHT:
                    warn_timer = WARN_DURATION
                    continue

                ccx, lx = divmod(gx, settings.CHUNK_SIZE)
                ccy, ly = divmod(gy, settings.CHUNK_SIZE)
                floor, wall = world.chunks[(ccx, ccy)]

                if ev.button == 1:  # DIG
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
                        if itm and itm['type']=='dirt':
                            itm['count'] += 1
                        elif itm is None:
                            player_state['hotbar'][slot] = {
                                'type':  'dirt',
                                'count': 1,
                                'image': assets.floor_img
                            }

                elif ev.button == 3:  # BUILD
                    slot = player_state['selected_slot']
                    itm  = player_state['hotbar'][slot]
                    # only place if you have at least one dirt
                    if itm and itm['type']=='dirt' and itm['count'] > 0:
                        if floor[ly][lx] == settings.TILE_EMPTY:
                            floor[ly][lx] = settings.TILE_DIRT
                            itm['count'] -= 1
                        elif floor[ly][lx] == settings.TILE_DIRT and wall[ly][lx] == settings.TILE_EMPTY:
                            wall[ly][lx] = settings.TILE_DIRT
                            itm['count'] -= 1
                        # remove if empty
                        if itm['count'] == 0:
                            player_state['hotbar'][slot] = None

        # Update player input & movement
        player.update_input(player_state, assets.TILE_SIZE, dt)

        # Draw world + hotbar
        render.draw_world(screen, player_state, world.chunks)

        # Draw warning if active
        if warn_timer > 0:
            surf = warn_font.render("Cannot Break Spawn Area", True, (255,50,50))
            x = settings.SCREEN_W//2 - surf.get_width()//2
            screen.blit(surf, (x, 10))
            warn_timer -= dt

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
