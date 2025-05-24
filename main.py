import sys
import pygame

from engine import settings, assets, render
from game import world, player
from engine import events

def initialize():
    """Initialize pygame, screen, assets, player, and return all state."""
    pygame.init()
    info = pygame.display.Info()
    settings.SCREEN_W, settings.SCREEN_H = info.current_w, info.current_h
    screen = pygame.display.set_mode((settings.SCREEN_W, settings.SCREEN_H), pygame.FULLSCREEN)

    assets.init_assets()  # <-- Call after display is set!
    render.init_render()

    default_tile_size = settings.SCREEN_W // settings.DEFAULT_TILES_ACROSS
    player_state = player.init_player(default_tile_size)
    assets.update_zoom(default_tile_size)
    world.load_chunks(player_state['tx'], player_state['ty'])

    # Calculate min/max tile size in pixels (min = most zoomed out, max = most zoomed in)
    min_px = settings.SCREEN_W // settings.MAX_TILES_ACROSS
    max_px = settings.SCREEN_W // settings.MIN_TILES_ACROSS

    warn_font = pygame.font.SysFont(None, 24)

    # Track last player tile position for chunk loading
    player_state['_last_tx'] = player_state['tx']
    player_state['_last_ty'] = player_state['ty']

    # Compute wall depths once at start
    wall_depths = world.compute_wall_depths(world.chunks)

    return screen, player_state, default_tile_size, min_px, max_px, warn_font, wall_depths

def game_loop(screen, player_state, default_tile_size, min_px, max_px, warn_font, wall_depths):
    warn_timer = 0.0
    WARN_DURATION = 1.5
    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        # Handle events (including quit)
        warn_timer, block_changed = events.handle_events(
            player_state, default_tile_size, min_px, max_px, warn_timer, WARN_DURATION
        )

        # Update player input and movement (no event.get() here)
        player.update_input(player_state, assets.TILE_SIZE, dt)

        # Only reload chunks if player moved to a new tile (no wall_depths update here)
        if (player_state['tx'], player_state['ty']) != (player_state['_last_tx'], player_state['_last_ty']):
            world.load_chunks(player_state['tx'], player_state['ty'])
            player_state['_last_tx'] = player_state['tx']
            player_state['_last_ty'] = player_state['ty']

        # Only recompute wall depths if a block was placed or broken
        if block_changed:
            wall_depths = world.compute_wall_depths(world.chunks)

        render.draw_world(screen, player_state, world.chunks, wall_depths)

        if warn_timer > 0:
            surf = warn_font.render("Cannot Break Spawn Area", True, (255, 50, 50))
            x = (settings.SCREEN_W - surf.get_width()) // 2
            screen.blit(surf, (x, 10))
            warn_timer -= dt

        pygame.display.flip()
    pygame.quit()
    sys.exit()

def main():
    screen, player_state, default_tile_size, min_px, max_px, warn_font, wall_depths = initialize()
    game_loop(screen, player_state, default_tile_size, min_px, max_px, warn_font, wall_depths)

if __name__ == "__main__":
    main()
