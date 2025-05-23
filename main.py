import sys
import pygame

import settings
import assets
import world
import player
import render

def main():
    """
    Main game loop and initialization.
    """
    # Initialize Pygame & screen
    pygame.init()
    info = pygame.display.Info()
    settings.SCREEN_W, settings.SCREEN_H = info.current_w, info.current_h
    screen = pygame.display.set_mode((settings.SCREEN_W, settings.SCREEN_H), pygame.FULLSCREEN)

    # Load assets & fonts
    assets.init_assets()
    render.init_render()

    # Initial zoom & player setup
    default_ts = settings.SCREEN_W // settings.DEFAULT_TILES_ACROSS
    player_state = player.init_player(default_ts)
    assets.update_zoom(default_ts)
    world.load_chunks(player_state['tx'], player_state['ty'])

    # Zoom bounds
    min_px = settings.SCREEN_W // settings.MIN_TILES_ACROSS
    max_px = settings.SCREEN_W // settings.MAX_TILES_ACROSS

    # Spawn-protect warning
    warn_timer = 0.0
    WARN_DURATION = 1.5
    warn_font = pygame.font.SysFont(None, 24)

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        # Event Handling
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            # Zoom in/out
            elif ev.type == pygame.MOUSEWHEEL:
                delta = 4 if ev.y > 0 else -4
                desired = assets.TILE_SIZE + delta
                new_size = max(min_px, min(max_px, desired))
                if new_size != assets.TILE_SIZE:
                    assets.update_zoom(new_size)
                    world.load_chunks(player_state['tx'], player_state['ty'])
                    px = player_state['tx'] * assets.TILE_SIZE
                    py = player_state['ty'] * assets.TILE_SIZE
                    player_state['px'] = px
                    player_state['py'] = py
                    player_state['target_x'] = px
                    player_state['target_y'] = py

            # Reset zoom
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

            # Dig / Build
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3):
                mx, my = ev.pos
                cam_x = settings.SCREEN_W // 2 - player_state['px']
                cam_y = settings.SCREEN_H // 2 - player_state['py']
                gx = int((mx - cam_x) // assets.TILE_SIZE)
                gy = int((my - cam_y) // assets.TILE_SIZE)

                # Spawn protection
                if abs(gx) <= settings.SPAWN_PROTECT_WIDTH and abs(gy) <= settings.SPAWN_PROTECT_HEIGHT:
                    warn_timer = WARN_DURATION
                    continue

                ccx, lx = divmod(gx, settings.CHUNK_SIZE)
                ccy, ly = divmod(gy, settings.CHUNK_SIZE)
                chunk = world.chunks.get((ccx, ccy))
                if not chunk:
                    continue
                floor, wall = chunk

                # Ensure indices valid
                if not (0 <= lx < settings.CHUNK_SIZE and 0 <= ly < settings.CHUNK_SIZE):
                    continue

                if ev.button == 1:
                    # DIG: remove wall first, then floor
                    if wall[ly][lx] == settings.TILE_DIRT:
                        wall[ly][lx] = settings.TILE_EMPTY
                        player.add_to_hotbar(player_state, 'dirt', assets.floor_img)
                    elif floor[ly][lx] == settings.TILE_DIRT:
                        floor[ly][lx] = settings.TILE_EMPTY
                        player.add_to_hotbar(player_state, 'dirt', assets.floor_img)
                else:
                    # BUILD: unified place—floor or wall
                    player.place_dirt(player_state, gx, gy, floor, wall)

        # Movement & Chunk Loading
        player.update_input(player_state, assets.TILE_SIZE, dt)
        world.load_chunks(player_state['tx'], player_state['ty'])

        # Compute wall depths for shading
        wall_depths = world.compute_wall_depths(world.chunks)

        # Render
        render.draw_world(screen, player_state, world.chunks, wall_depths)

        # Spawn-protect warning
        if warn_timer > 0:
            surf = warn_font.render("Cannot Break Spawn Area", True, (255, 50, 50))
            x = (settings.SCREEN_W - surf.get_width()) // 2
            screen.blit(surf, (x, 10))
            warn_timer -= dt

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
