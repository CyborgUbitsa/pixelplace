import zlib, io, itertools
from .models import TILE_SIZE

def decompress_tile(blob: bytes) -> bytearray:
    return bytearray(zlib.decompress(blob))

def compress_tile(buf: bytearray) -> bytes:
    return zlib.compress(buf, level=6)

def set_pixel(buf: bytearray, local_x: int, local_y: int, rgb: int):
    r = (rgb >> 16) & 0xFF
    g = (rgb >> 8)  & 0xFF
    b =  rgb        & 0xFF

    row_from_top = TILE_SIZE - 1 - local_y          
    off = (row_from_top * TILE_SIZE + local_x) * 3 
    buf[off : off + 3] = (r, g, b)
