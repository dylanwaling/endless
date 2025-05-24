# world.py

from engine import settings
from noise import pnoise2
from collections import deque
from typing import Dict, Tuple, List

# ──────────────────────────────────────────────────────────────
# Chunk Storage
# ──────────────────────────────────────────────────────────────

# Chunks are stored as {(cx, cy): (floor, wall)}
chunks: Dict[Tuple[int, int], Tuple[List[List[int]], List[List[int]]]] = {}

# ──────────────────────────────────────────────────────────────
# Chunk Generation & Loading
# ──────────────────────────────────────────────────────────────

def gen_chunk(cx: int, cy: int) -> Tuple[List[List[int]], List[List[int]]]:
    """
    Generate a chunk at (cx, cy) with floor and wall data.
    """
    size = settings.CHUNK_SIZE
    floor = [[settings.TILE_EMPTY for _ in range(size)] for _ in range(size)]
    wall  = [[settings.TILE_EMPTY for _ in range(size)] for _ in range(size)]

    for ly in range(size):
        for lx in range(size):
            wx = cx * size + lx
            wy = cy * size + ly
            n = pnoise2(wx * 0.1, wy * 0.1, octaves=2)
            floor[ly][lx] = settings.TILE_DIRT
            if n <= 0.0:
                wall[ly][lx] = settings.TILE_DIRT
    return floor, wall

def chunk_coords_around(px: int, py: int, radius: int) -> set:
    """
    Return a set of chunk coordinates within a square radius of (px, py).
    """
    pcx, _ = divmod(px, settings.CHUNK_SIZE)
    pcy, _ = divmod(py, settings.CHUNK_SIZE)
    return {
        (pcx + dx, pcy + dy)
        for dx in range(-radius, radius + 1)
        for dy in range(-radius, radius + 1)
    }

def load_chunks(px: int, py: int) -> None:
    """
    Load all chunks within LOAD_RADIUS of the player and unload distant ones.
    Also carves the spawn point at (0, 0).
    """
    needed = chunk_coords_around(px, py, settings.LOAD_RADIUS)

    # Load missing chunks
    for coord in needed:
        if coord not in chunks:
            chunks[coord] = gen_chunk(*coord)

    # Unload chunks not needed
    for coord in list(chunks):
        if coord not in needed:
            del chunks[coord]

    # Carve spawn at (0, 0)
    if (0, 0) in chunks:
        floor, wall = chunks[(0, 0)]
        floor[0][0] = settings.TILE_DIRT
        wall[0][0] = settings.TILE_EMPTY

# ──────────────────────────────────────────────────────────────
# Tile Logic
# ──────────────────────────────────────────────────────────────

def can_walk(tx: int, ty: int) -> bool:
    """
    Return True if the tile at (tx, ty) is walkable (dirt floor, empty wall).
    """
    ccx, ilx = divmod(tx, settings.CHUNK_SIZE)
    ccy, ily = divmod(ty, settings.CHUNK_SIZE)
    chunk = chunks.get((ccx, ccy))
    if not chunk:
        return False
    floor, wall = chunk
    if not (0 <= ilx < settings.CHUNK_SIZE and 0 <= ily < settings.CHUNK_SIZE):
        return False
    return floor[ily][ilx] == settings.TILE_DIRT and wall[ily][ilx] == settings.TILE_EMPTY

# ──────────────────────────────────────────────────────────────
# Wall Depth Calculation
# ──────────────────────────────────────────────────────────────

def compute_wall_depths(
    chunks_dict: Dict[Tuple[int, int], Tuple[List[List[int]], List[List[int]]]]
) -> Dict[Tuple[int, int], int]:
    """
    Compute the depth of each wall tile for shading.
    Returns a dict mapping (wx, wy) to depth.
    """
    depth: Dict[Tuple[int, int], int] = {}
    q = deque()

    # Find all wall edges (depth 0)
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
                    neighbor = chunks_dict.get((ccx, ccy))
                    if (
                        not neighbor or
                        not (0 <= ilx < settings.CHUNK_SIZE and 0 <= ily < settings.CHUNK_SIZE) or
                        neighbor[1][ily][ilx] != settings.TILE_DIRT
                    ):
                        depth[(wx, wy)] = 0
                        q.append((wx, wy))
                        break

    # BFS to fill in depths
    while q:
        wx, wy = q.popleft()
        d = depth[(wx, wy)]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = wx + dx, wy + dy
            if (nx, ny) in depth:
                continue
            ccx, ilx = divmod(nx, settings.CHUNK_SIZE)
            ccy, ily = divmod(ny, settings.CHUNK_SIZE)
            neighbor = chunks_dict.get((ccx, ccy))
            if (
                neighbor and
                (0 <= ilx < settings.CHUNK_SIZE and 0 <= ily < settings.CHUNK_SIZE) and
                neighbor[1][ily][ilx] == settings.TILE_DIRT
            ):
                depth[(nx, ny)] = d + 1
                q.append((nx, ny))
    return depth
