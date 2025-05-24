import pygame
from engine import settings, assets

# ──────────────────────────────────────────────────────────────
# Globals
# ──────────────────────────────────────────────────────────────

_font: pygame.font.Font = None
_radial_mask: pygame.Surface = None
_current_radius_px: int = None

# ──────────────────────────────────────────────────────────────
# Initialization
# ──────────────────────────────────────────────────────────────

def init_render() -> None:
    """Initialize font for rendering."""
    global _font
    _font = pygame.font.SysFont(None, 18)

# ──────────────────────────────────────────────────────────────
# Radial Mask Utilities
# ──────────────────────────────────────────────────────────────

def _make_radial_mask(radius: int) -> pygame.Surface:
    """Create a radial darkness mask with smooth falloff."""
    size = radius * 2
    surf = pygame.Surface((size, size), flags=pygame.SRCALPHA)
    max_a = settings.MAX_DARKNESS
    cx = cy = radius
    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            d = (dx * dx + dy * dy) ** 0.5
            if d < radius:
                a = int(max_a * (1 - d / radius))
                surf.set_at((x, y), (0, 0, 0, a))
    return surf

def _ensure_radial_mask() -> None:
    """Ensure the radial mask matches the current zoom."""
    global _radial_mask, _current_radius_px
    ts = assets.TILE_SIZE
    radius_px = settings.LIGHT_RADIUS_TILES * ts
    if radius_px != _current_radius_px:
        _radial_mask = _make_radial_mask(radius_px)
        _current_radius_px = radius_px

# ──────────────────────────────────────────────────────────────
# Hotbar Rendering
# ──────────────────────────────────────────────────────────────

def draw_hotbar(screen: pygame.Surface, player: dict) -> None:
    """Draw the player's hotbar."""
    slots, sz, pad = settings.HOTBAR_SLOTS, settings.HOTBAR_SLOT_SIZE, settings.HOTBAR_PADDING
    total = slots * sz + (slots - 1) * pad
    x0 = (settings.SCREEN_W - total) // 2
    y0 = settings.SCREEN_H - sz - 10
    for i in range(slots):
        x = x0 + i * (sz + pad)
        rect = pygame.Rect(x, y0, sz, sz)
        pygame.draw.rect(screen, (50, 50, 50), rect)
        color = (200, 200, 50) if i == player['selected_slot'] else (100, 100, 100)
        pygame.draw.rect(screen, color, rect, 3 if i == player['selected_slot'] else 1)
        itm = player['hotbar'][i]
        if itm:
            icon = pygame.transform.scale(itm['image'], (sz - 8, sz - 8))
            screen.blit(icon, (x + 4, y0 + 4))
            cnt = _font.render(str(itm['count']), True, (255, 255, 255))
            cw, ch = cnt.get_size()
            screen.blit(cnt, (x + sz - cw - 4, y0 + sz - ch - 4))

# ──────────────────────────────────────────────────────────────
# World Rendering
# ──────────────────────────────────────────────────────────────

def draw_world(
    screen: pygame.Surface,
    player: dict,
    chunks: dict,
    wall_depths: dict
) -> None:
    """
    Draw the world, player, overlays, and UI with rim-lighting style.
    """
    ts = assets.TILE_SIZE
    cam_x = settings.SCREEN_W // 2 - player['px']
    cam_y = settings.SCREEN_H // 2 - player['py']

    # Asset sizes
    edge_thickness = 16  # Your rim edge images are 48x16 (W x H)
    corner_size = 16     # Your rim corner images are 16x16

    # 1) Draw background
    screen.fill((20, 20, 30))

    # 2) Draw tiles (dark tops)
    for (cx, cy), (floor, wall) in chunks.items():
        bx = cx * settings.CHUNK_SIZE * ts + cam_x
        by = cy * settings.CHUNK_SIZE * ts + cam_y
        for ly in range(settings.CHUNK_SIZE):
            for lx in range(settings.CHUNK_SIZE):
                px, py = bx + lx * ts, by + ly * ts
                if px + ts < 0 or px > settings.SCREEN_W or py + ts < 0 or py > settings.SCREEN_H:
                    continue
                # Draw floor if present
                if floor[ly][lx] == settings.TILE_DIRT:
                    screen.blit(assets.floor_img, (px, py))
                # Draw dark wall top if present
                if wall[ly][lx] == settings.TILE_DIRT:
                    screen.blit(assets.wall_img, (px, py))

    # 3) Draw rim highlights for wall tiles
    for (cx, cy), (floor, wall) in chunks.items():
        base_x = cx * settings.CHUNK_SIZE
        base_y = cy * settings.CHUNK_SIZE
        bx = base_x * ts + cam_x
        by = base_y * ts + cam_y
        for ly in range(settings.CHUNK_SIZE):
            for lx in range(settings.CHUNK_SIZE):
                if wall[ly][lx] != settings.TILE_DIRT:
                    continue
                wx, wy = base_x + lx, base_y + ly
                px, py = bx + lx * ts, by + ly * ts

                # North edge (top)
                if _get_wall_tile(chunks, wx, wy - 1) != settings.TILE_DIRT:
                    screen.blit(assets.rim_north_img, (px, py))
                # South edge (bottom)
                if _get_wall_tile(chunks, wx, wy + 1) != settings.TILE_DIRT:
                    screen.blit(assets.rim_south_img, (px, py))
                # West edge (left)
                if _get_wall_tile(chunks, wx - 1, wy) != settings.TILE_DIRT:
                    screen.blit(assets.rim_west_img, (px, py))
                # East edge (right)
                if _get_wall_tile(chunks, wx + 1, wy) != settings.TILE_DIRT:
                    screen.blit(assets.rim_east_img, (px, py))

                # North-West corner (top-left)
                if (
                    _get_wall_tile(chunks, wx, wy - 1) == settings.TILE_DIRT and
                    _get_wall_tile(chunks, wx - 1, wy) == settings.TILE_DIRT and
                    _get_wall_tile(chunks, wx - 1, wy - 1) != settings.TILE_DIRT
                ):
                    screen.blit(assets.rim_nw_img, (px, py))
                # North-East corner (top-right)
                if (
                    _get_wall_tile(chunks, wx, wy - 1) == settings.TILE_DIRT and
                    _get_wall_tile(chunks, wx + 1, wy) == settings.TILE_DIRT and
                    _get_wall_tile(chunks, wx + 1, wy - 1) != settings.TILE_DIRT
                ):
                    screen.blit(assets.rim_ne_img, (px, py))
                # South-West corner (bottom-left)
                if (
                    _get_wall_tile(chunks, wx, wy + 1) == settings.TILE_DIRT and
                    _get_wall_tile(chunks, wx - 1, wy) == settings.TILE_DIRT and
                    _get_wall_tile(chunks, wx - 1, wy + 1) != settings.TILE_DIRT
                ):
                    screen.blit(assets.rim_sw_img, (px, py))
                # South-East corner (bottom-right)
                if (
                    _get_wall_tile(chunks, wx, wy + 1) == settings.TILE_DIRT and
                    _get_wall_tile(chunks, wx + 1, wy) == settings.TILE_DIRT and
                    _get_wall_tile(chunks, wx + 1, wy + 1) != settings.TILE_DIRT
                ):
                    screen.blit(assets.rim_se_img, (px, py))

    # 4) Draw player
    screen.blit(assets.player_img, (settings.SCREEN_W // 2, settings.SCREEN_H // 2))

    # 5) Debug grid overlay
    if settings.DEBUG_MODE:
        _draw_debug_grid(screen, player, ts, cam_x, cam_y)

    # 6) Coordinates
    coord = _font.render(f"({player['tx']}, {player['ty']})", True, (255, 255, 255))
    screen.blit(coord, (10, 10))

    # 7) Hotbar
    draw_hotbar(screen, player)

def _get_wall_tile(chunks, wx, wy):
    """Helper to get wall tile type at world (wx, wy)."""
    cx, lx = divmod(wx, settings.CHUNK_SIZE)
    cy, ly = divmod(wy, settings.CHUNK_SIZE)
    key = (cx, cy)
    if key not in chunks:
        return None
    _, wall = chunks[key]
    if 0 <= lx < settings.CHUNK_SIZE and 0 <= ly < settings.CHUNK_SIZE:
        return wall[ly][lx]
    return None

def _draw_debug_grid(
    screen: pygame.Surface,
    player: dict,
    ts: int,
    cam_x: int,
    cam_y: int
) -> None:
    """Draw a debug grid overlay centered on the player."""
    r, col = settings.DEBUG_GRID_RADIUS, settings.DEBUG_GRID_COLOR
    for wx in range(player['tx'] - r, player['tx'] + r + 1):
        sx = wx * ts + cam_x
        pygame.draw.line(screen, col, (sx, 0), (sx, settings.SCREEN_H), 1)
    for wy in range(player['ty'] - r, player['ty'] + r + 1):
        sy = wy * ts + cam_y
        pygame.draw.line(screen, col, (0, sy), (settings.SCREEN_W, sy), 1)

# ──────────────────────────────────────────────────────────────
# Utility: Hotbar Placement (stub)
# ──────────────────────────────────────────────────────────────

def try_place_from_hotbar(gx, gy, floor, wall, layer='wall'):
    print(f"try_place_from_hotbar called with layer={layer}")
    # ...rest of your code...
