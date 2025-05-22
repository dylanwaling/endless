# world.py

import settings
from noise import pnoise2

# chunk store: (cx,cy) → (floor_2d_list, wall_2d_list)
chunks = {}

def gen_chunk(cx, cy):
    """
    Every cell has a floor (dirt).  Where perlin noise ≤ 0,
    we put a wall (rock) on top.
    """
    floor = [[settings.TILE_DIRT]*settings.CHUNK_SIZE
             for _ in range(settings.CHUNK_SIZE)]
    wall  = [[settings.TILE_EMPTY]*settings.CHUNK_SIZE
             for _ in range(settings.CHUNK_SIZE)]

    for y in range(settings.CHUNK_SIZE):
        for x in range(settings.CHUNK_SIZE):
            wx = cx * settings.CHUNK_SIZE + x
            wy = cy * settings.CHUNK_SIZE + y
            n  = pnoise2(wx*0.1, wy*0.1, octaves=2)
            if n <= 0.0:
                wall[y][x] = settings.TILE_DIRT

    return floor, wall

def load_chunks(px, py):
    """Generate/unload chunks around (px,py), then carve spawn at (0,0)."""
    pcx, pcy = px // settings.CHUNK_SIZE, py // settings.CHUNK_SIZE
    needed = [
        (pcx+dx, pcy+dy)
        for dx in range(-settings.LOAD_RADIUS, settings.LOAD_RADIUS+1)
        for dy in range(-settings.LOAD_RADIUS, settings.LOAD_RADIUS+1)
    ]

    # generate missing
    for coord in needed:
        if coord not in chunks:
            chunks[coord] = gen_chunk(*coord)
    # unload far away
    for coord in list(chunks):
        if coord not in needed:
            del chunks[coord]

    # carve spawn at world (0,0)
    if (0,0) in chunks:
        f, w = chunks[(0,0)]
        f[0][0] = settings.TILE_DIRT
        w[0][0] = settings.TILE_EMPTY

def collide(tx, ty):
    """Return True if tile (tx,ty) is walkable (floor & no wall)."""
    cx, lx = divmod(tx, settings.CHUNK_SIZE)
    cy, ly = divmod(ty, settings.CHUNK_SIZE)
    floor, wall = chunks.get((cx, cy), (None, None))
    return bool(floor and
                floor[ly][lx] == settings.TILE_DIRT and
                wall[ly][lx]  == settings.TILE_EMPTY)
