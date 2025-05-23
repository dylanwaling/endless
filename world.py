# world.py

import settings
from noise import pnoise2
from collections import deque

# ──────────────────────────────────────────────────────────────
# Chunk Storage
# ──────────────────────────────────────────────────────────────

chunks = {}

# ──────────────────────────────────────────────────────────────
# Chunk Generation & Loading
# ──────────────────────────────────────────────────────────────

def gen_chunk(cx, cy):
    """
    Generate a chunk at (cx, cy) with floor and wall data.
    """
    floor = [[settings.TILE_EMPTY] * settings.CHUNK_SIZE for _ in range(settings.CHUNK_SIZE)]
    wall  = [[settings.TILE_EMPTY] * settings.CHUNK_SIZE for _ in range(settings.CHUNK_SIZE)]
    for ly in range(settings.CHUNK_SIZE):
        for lx in range(settings.CHUNK_SIZE):
            wx = cx * settings.CHUNK_SIZE + lx
            wy = cy * settings.CHUNK_SIZE + ly
            n  = pnoise2(wx * 0.1, wy * 0.1, octaves=2)
            floor[ly][lx] = settings.TILE_DIRT
            if n <= 0.0:
                wall[ly][lx] = settings.TILE_DIRT
    return floor, wall

def load_chunks(px, py):
    """
    Load all chunks within LOAD_RADIUS of the player.
    """
    pcx, _ = divmod(px, settings.CHUNK_SIZE)
    pcy, _ = divmod(py, settings.CHUNK_SIZE)
    needed = {
        (pcx + dx, pcy + dy)
        for dx in range(-settings.LOAD_RADIUS, settings.LOAD_RADIUS + 1)
        for dy in range(-settings.LOAD_RADIUS, settings.LOAD_RADIUS + 1)
    }
    for coord in needed:
        if coord not in chunks:
            chunks[coord] = gen_chunk(*coord)
    for coord in list(chunks):
        if coord not in needed:
            del chunks[coord]
    # Carve spawn
    if (0, 0) in chunks:
        f, w = chunks[(0, 0)]
        f[0][0] = settings.TILE_DIRT
        w[0][0] = settings.TILE_EMPTY

# ──────────────────────────────────────────────────────────────
# Tile Logic
# ──────────────────────────────────────────────────────────────

def can_walk(tx, ty):
    """
    Return True if the tile at (tx, ty) is walkable.
    """
    ccx, ilx = divmod(tx, settings.CHUNK_SIZE)
    ccy, ily = divmod(ty, settings.CHUNK_SIZE)
    c = chunks.get((ccx, ccy))
    if not c:
        return False
    floor, wall = c
    if not (0 <= ilx < settings.CHUNK_SIZE and 0 <= ily < settings.CHUNK_SIZE):
        return False
    return floor[ily][ilx] == settings.TILE_DIRT and wall[ily][ilx] == settings.TILE_EMPTY

# ──────────────────────────────────────────────────────────────
# Wall Depth Calculation
# ──────────────────────────────────────────────────────────────

def compute_wall_depths(chunks_dict):
    """
    Compute the depth of each wall tile for shading.
    """
    depth = {}
    q = deque()
    for (cx, cy), (floor, wall) in chunks_dict.items():
        base_x = cx * settings.CHUNK_SIZE
        base_y = cy * settings.CHUNK_SIZE
        for ly in range(settings.CHUNK_SIZE):
            for lx in range(settings.CHUNK_SIZE):
                if wall[ly][lx] != settings.TILE_DIRT:
                    continue
                wx, wy = base_x + lx, base_y + ly
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = wx + dx, wy + dy
                    ccx, ilx = divmod(nx, settings.CHUNK_SIZE)
                    ccy, ily = divmod(ny, settings.CHUNK_SIZE)
                    nb = chunks_dict.get((ccx, ccy))
                    if not nb or not (0 <= ilx < settings.CHUNK_SIZE and 0 <= ily < settings.CHUNK_SIZE) or nb[1][ily][ilx] != settings.TILE_DIRT:
                        depth[(wx, wy)] = 0
                        q.append((wx, wy))
                        break
    while q:
        wx, wy = q.popleft()
        d = depth[(wx, wy)]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = wx + dx, wy + dy
            if (nx, ny) in depth:
                continue
            ccx, ilx = divmod(nx, settings.CHUNK_SIZE)
            ccy, ily = divmod(ny, settings.CHUNK_SIZE)
            nb = chunks_dict.get((ccx, ccy))
            if nb and (0 <= ilx < settings.CHUNK_SIZE and 0 <= ily < settings.CHUNK_SIZE) and nb[1][ily][ilx] == settings.TILE_DIRT:
                depth[(nx, ny)] = d + 1
                q.append((nx, ny))
    return depth
