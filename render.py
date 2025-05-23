import pygame
import settings
import assets

_font = None
_radial_mask = None
_current_radius_px = None

def init_render():
    global _font
    _font = pygame.font.SysFont(None, 18)

def _make_radial_mask(R):
    size = R*2
    surf = pygame.Surface((size, size), flags=pygame.SRCALPHA)
    max_a = settings.MAX_DARKNESS
    cx = cy = R
    for y in range(size):
        for x in range(size):
            dx, dy = x-cx, y-cy
            d = (dx*dx + dy*dy)**0.5
            if d < R:
                a = int(max_a * (1 - d/R))
                surf.set_at((x, y), (0,0,0,a))
    return surf

def _ensure_radial_mask():
    global _radial_mask, _current_radius_px
    ts = assets.TILE_SIZE
    R_px = settings.LIGHT_RADIUS_TILES * ts
    if R_px != _current_radius_px:
        _radial_mask = _make_radial_mask(R_px)
        _current_radius_px = R_px

def draw_hotbar(screen, player):
    slots, sz, pad = settings.HOTBAR_SLOTS, settings.HOTBAR_SLOT_SIZE, settings.HOTBAR_PADDING
    total = slots*sz + (slots-1)*pad
    x0 = (settings.SCREEN_W - total)//2
    y0 = settings.SCREEN_H - sz - 10
    for i in range(slots):
        x = x0 + i*(sz+pad)
        rect = pygame.Rect(x, y0, sz, sz)
        pygame.draw.rect(screen, (50,50,50), rect)
        color = (200,200,50) if i==player['selected_slot'] else (100,100,100)
        pygame.draw.rect(screen, color, rect, 3 if i==player['selected_slot'] else 1)
        itm = player['hotbar'][i]
        if itm:
            icon = pygame.transform.scale(itm['image'], (sz-8, sz-8))
            screen.blit(icon,(x+4, y0+4))
            cnt = _font.render(str(itm['count']), True, (255,255,255))
            cw, ch = cnt.get_size()
            screen.blit(cnt, (x+sz-cw-4, y0+sz-ch-4))

def draw_world(screen, player, chunks, wall_depths):
    ts = assets.TILE_SIZE
    cam_x = settings.SCREEN_W//2 - player['px']
    cam_y = settings.SCREEN_H//2 - player['py']

    _ensure_radial_mask()

    # 1) Draw tiles
    screen.fill((20,20,30))
    for (cx,cy),(floor,wall) in chunks.items():
        bx = cx*settings.CHUNK_SIZE*ts + cam_x
        by = cy*settings.CHUNK_SIZE*ts + cam_y
        for ly in range(settings.CHUNK_SIZE):
            for lx in range(settings.CHUNK_SIZE):
                px, py = bx+lx*ts, by+ly*ts
                if px+ts<0 or px>settings.SCREEN_W or py+ts<0 or py>settings.SCREEN_H:
                    continue
                if floor[ly][lx] == settings.TILE_DIRT:
                    screen.blit(assets.floor_img, (px, py))
                if wall[ly][lx] == settings.TILE_DIRT:
                    screen.blit(assets.wall_img, (px, py))

    # 2) Subtractive radial darkness
    dark = pygame.Surface((settings.SCREEN_W, settings.SCREEN_H), flags=pygame.SRCALPHA)
    dark.fill((0,0,0, settings.MAX_DARKNESS))
    R = _current_radius_px
    dark.blit(_radial_mask,
              (settings.SCREEN_W//2 - R, settings.SCREEN_H//2 - R),
              special_flags=pygame.BLEND_RGBA_SUB)
    screen.blit(dark, (0,0))

    # 3) Depth-based gradient shading (draw on a temp surface, then blit)
    MAX_DIST = settings.MAX_CORE_DEPTH
    W, H = settings.SCREEN_W, settings.SCREEN_H

    shade = pygame.Surface((W, H), flags=pygame.SRCALPHA)
    for (cx,cy),(floor,wall) in chunks.items():
        base_x = cx*settings.CHUNK_SIZE
        base_y = cy*settings.CHUNK_SIZE
        bx = base_x*ts + cam_x
        by = base_y*ts + cam_y

        for ly in range(settings.CHUNK_SIZE):
            for lx in range(settings.CHUNK_SIZE):
                if wall[ly][lx] != settings.TILE_DIRT:
                    continue

                wx, wy = base_x+lx, base_y+ly
                d = wall_depths.get((wx,wy), 0)
                if d == 0:
                    continue  # bright rim

                frac = min(d, MAX_DIST) / MAX_DIST
                alpha = int(frac * settings.MAX_DARKNESS)

                px, py = bx+lx*ts, by+ly*ts
                if px+ts<0 or px>W or py+ts<0 or py>H:
                    continue

                rect = pygame.Rect(px, py, ts, ts)
                shade.fill((0,0,0,alpha), rect=rect)
    screen.blit(shade, (0,0))

    # 4) Draw player
    screen.blit(assets.player_img,
                (settings.SCREEN_W//2, settings.SCREEN_H//2))

    # Debug grid
    if settings.DEBUG_MODE:
        r, col = settings.DEBUG_GRID_RADIUS, settings.DEBUG_GRID_COLOR
        for wx in range(player['tx']-r, player['tx']+r+1):
            sx = wx*ts + cam_x
            pygame.draw.line(screen, col, (sx,0), (sx,settings.SCREEN_H), 1)
        for wy in range(player['ty']-r, player['ty']+r+1):
            sy = wy*ts + cam_y
            pygame.draw.line(screen, col, (0,sy), (settings.SCREEN_W,sy), 1)

    # 5) Coordinates
    coord = _font.render(f"({player['tx']}, {player['ty']})", True, (255,255,255))
    screen.blit(coord, (10,10))

    # 6) Hotbar
    draw_hotbar(screen, player)

def try_place_from_hotbar(gx, gy, floor, wall, layer='wall'):
    print(f"try_place_from_hotbar called with layer={layer}")
    # ...rest of your code...
