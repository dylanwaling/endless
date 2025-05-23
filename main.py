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

    assets.init_assets()
    render.init_render()

    default_ts = settings.SCREEN_W // settings.DEFAULT_TILES_ACROSS
    player_state = player.init_player(default_ts)
    assets.update_zoom(default_ts)
    world.load_chunks(player_state['tx'], player_state['ty'])

    min_px = settings.SCREEN_W // settings.MIN_TILES_ACROSS
    max_px = settings.SCREEN_W // settings.MAX_TILES_ACROSS

    warn_font = pygame.font.SysFont(None, 24)

    return screen, player_state, default_ts, min_px, max_px, warn_font

def game_loop(screen, player_state, default_ts, min_px, max_px, warn_font):
    warn_timer = 0.0
    WARN_DURATION = 1.5
    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        warn_timer = events.handle_events(player_state, default_ts, min_px, max_px, warn_timer, WARN_DURATION)
        player.update_input(player_state, assets.TILE_SIZE, dt)
        world.load_chunks(player_state['tx'], player_state['ty'])
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
    screen, player_state, default_ts, min_px, max_px, warn_font = initialize()
    game_loop(screen, player_state, default_ts, min_px, max_px, warn_font)

if __name__ == "__main__":
    main()
