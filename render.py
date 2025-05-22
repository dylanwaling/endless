# render.py

import pygame
import settings
import assets

# — Font for overlays & hotbar counts —
_font = None

# — Base mask for per‐tile shadows —
_mask_surf = None
_current_ts = None

def init_render():
    global _font
    _font = pygame.font.SysFont(None, 18)

def _ensure_base_mask():
    """Recreate a solid black TILE_SIZE×TILE_SIZE mask when TILE_SIZE changes."""
    global _mask_surf, _current_ts
    ts = assets.TILE_SIZE
    if _current_ts != ts:
        surf = pygame.Surface((ts, ts), flags=pygame.SRCALPHA)
        surf.fill((0, 0, 0, 255))
        _mask_surf = surf
        _current_ts = ts

def draw_hotbar(screen, player):
    slots = settings.HOTBAR_SLOTS
    sz    = settings.HOTBAR_SLOT_SIZE
    pad   = settings.HOTBAR_PADDING
    total = slots*sz + (slots-1)*pad
    start_x = (settings.SCREEN_W - total)//2
    y       = settings.SCREEN_H - sz - 10

    for i in range(slots):
        x = start_x + i*(sz+pad)
        rect = pygame.Rect(x, y, sz, sz)
        pygame.draw.rect(screen, (50,50,50), rect)
        # highlight border
        color = (200,200,50) if i==player['selected_slot'] else (100,100,100)
        pygame.draw.rect(screen, color, rect, 3 if i==player['selected_slot'] else 1)

        item = player['hotbar'][i]
        if item:
            # draw icon
            icon = pygame.transform.scale(item['image'], (sz-8, sz-8))
            screen.blit(icon, (x+4, y+4))
            # draw count
            cnt = _font.render(str(item['count']), True, (255,255,255))
            cw, ch = cnt.get_size()
            screen.blit(cnt, (x+sz-cw-4, y+sz-ch-4))

def draw_world(screen, player, chunks):
    _ensure_base_mask()
    ts    = assets.TILE_SIZE
    cam_x = settings.SCREEN_W//2 - player['px']
    cam_y = settings.SCREEN_H//2 - player['py']

    # --- Background ---
    screen.fill((20,20,30))

    # --- Tiles & shadows ---
    for (cx, cy), (floor, wall) in chunks.items():
        bx = cx*settings.CHUNK_SIZE*ts + cam_x
        by = cy*settings.CHUNK_SIZE*ts + cam_y

        for y in range(settings.CHUNK_SIZE):
            for x in range(settings.CHUNK_SIZE):
                px, py = bx + x*ts, by + y*ts
                if not (-ts<px<settings.SCREEN_W and -ts<py<settings.SCREEN_H):
                    continue

                # floor & wall
                if floor[y][x] == settings.TILE_DIRT:
                    screen.blit(assets.floor_img, (px,py))
                if wall[y][x] == settings.TILE_DIRT:
                    screen.blit(assets.wall_img, (px,py))

                # apply dynamic interior shadow on walls
                if wall[y][x] == settings.TILE_DIRT:
                    # count orthogonal wall neighbors
                    count = 0
                    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                        nx, ny = x+dx, y+dy
                        gcx, glx = divmod(cx*settings.CHUNK_SIZE+nx, settings.CHUNK_SIZE)
                        gcy, gly = divmod(cy*settings.CHUNK_SIZE+ny, settings.CHUNK_SIZE)
                        neigh = chunks.get((gcx, gcy))
                        if neigh:
                            _, w2 = neigh
                            if 0 <= gly < settings.CHUNK_SIZE and 0 <= glx < settings.CHUNK_SIZE:
                                if w2[gly][glx] == settings.TILE_DIRT:
                                    count += 1
                    # alpha mapping: 0→0,1→128,2→192,3→224,4→255
                    alpha = [0,128,192,224,255][count]
                    if alpha:
                        mask = _mask_surf.copy()
                        mask.fill((0,0,0,alpha), special_flags=pygame.BLEND_RGBA_MULT)
                        screen.blit(mask, (px,py))

    # --- Player ---
    screen.blit(assets.player_img,
                (settings.SCREEN_W//2, settings.SCREEN_H//2))

    # --- Lighting overlay ---
    dark = pygame.Surface((settings.SCREEN_W,settings.SCREEN_H),
                          flags=pygame.SRCALPHA)
    dark.fill((0,0,0,200))
    lm = assets.light_mask
    center = (settings.SCREEN_W//2 - lm.get_width()//2,
              settings.SCREEN_H//2 - lm.get_height()//2)
    dark.blit(lm, center, special_flags=pygame.BLEND_RGBA_SUB)
    screen.blit(dark, (0,0))

    # --- Debug grid (optional) ---
    if settings.DEBUG_MODE:
        r = settings.DEBUG_GRID_RADIUS; c = settings.DEBUG_GRID_COLOR
        for wx in range(player['tx']-r, player['tx']+r+1):
            sx = wx*ts + cam_x
            pygame.draw.line(screen,c,(sx,0),(sx,settings.SCREEN_H),1)
        for wy in range(player['ty']-r, player['ty']+r+1):
            sy = wy*ts + cam_y
            pygame.draw.line(screen,c,(0,sy),(settings.SCREEN_W,sy),1)

    # --- Coordinates readout ---
    coord = _font.render(f"({player['tx']}, {player['ty']})",
                         True, (255,255,255))
    screen.blit(coord, (10,10))

    # --- Hotbar UI ---
    draw_hotbar(screen, player)
