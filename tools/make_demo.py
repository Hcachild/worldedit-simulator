"""Build the 13x8x13 cottage used as the demo schematic."""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from core.nbt import encode_varint  # noqa: E402
from core.schematic import write_schem  # noqa: E402

WIDTH, HEIGHT, LENGTH = 13, 8, 13
DATA_VERSION = 3955


def build_blocks():
    blocks = [[["minecraft:air"] * LENGTH for _ in range(HEIGHT)] for _ in range(WIDTH)]

    def put(x, y, z, name):
        blocks[x][y][z] = name

    for x in range(WIDTH):
        for z in range(LENGTH):
            put(x, 0, z, "minecraft:stone_bricks")

    for y in range(1, 5):
        for x in range(WIDTH):
            for z in range(LENGTH):
                if x in (0, WIDTH - 1) or z in (0, LENGTH - 1):
                    corner = x in (0, WIDTH - 1) and z in (0, LENGTH - 1)
                    put(x, y, z, "minecraft:oak_log" if corner else "minecraft:oak_planks")

    for x in (3, 4, 8, 9):
        put(x, 2, 0, "minecraft:glass")
        put(x, 2, LENGTH - 1, "minecraft:glass")
    for z in (3, 4, 8, 9):
        put(0, 2, z, "minecraft:glass")
        put(WIDTH - 1, 2, z, "minecraft:glass")

    for y in (1, 2):
        put(6, y, 0, "minecraft:air")

    for x in range(WIDTH):
        for z in range(LENGTH):
            put(x, 5, z, "minecraft:spruce_planks")
    for x in range(1, WIDTH - 1):
        for z in range(1, LENGTH - 1):
            put(x, 6, z, "minecraft:spruce_planks")
    for x in range(2, WIDTH - 2):
        for z in range(2, LENGTH - 2):
            put(x, 7, z, "minecraft:spruce_planks")

    for y in (6, 7):
        put(10, y, 10, "minecraft:stone_bricks")

    return blocks


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "examples" / "demo.schem"
    blocks = build_blocks()
    palette = {}
    indices = []
    counts = Counter()
    for y in range(HEIGHT):
        for z in range(LENGTH):
            for x in range(WIDTH):
                name = blocks[x][y][z]
                counts[name] += 1
                if name not in palette:
                    palette[name] = len(palette)
                indices.append(palette[name])

    block_data = b"".join(encode_varint(index) for index in indices)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_schem(out, WIDTH, HEIGHT, LENGTH, palette, block_data, DATA_VERSION)
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    for name, count in counts.most_common():
        if name != "minecraft:air":
            print(f"  {count:5d}  {name}")


if __name__ == "__main__":
    main()
