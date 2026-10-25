"""Apply a smooth Y-axis colour curve to a white schematic.

The script is deliberately data-first: it reads the white model, analyses the
non-air Y distribution, maps each block through a monotone colour curve with
ordered dithering, then writes:

  * a fully coloured .schem
  * a colour-only overlay .schem
  * (optional) a WorldEdit clipboard + paste command pair sent to the local API

The overlay + //paste -a -o route lets the existing white model stay intact
while BlockData is applied per block.  It is useful for models such as the
tornado where a hard //replace band would look artificial.
"""
import argparse
import json
import math
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from core.nbt import decode_varints, encode_varint  # noqa: E402
from core.schematic import read_schem, write_schem  # noqa: E402

# Ordered 4x4 Bayer matrix. It keeps transitions structured instead of adding
# per-block random speckle.
BAYER = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)

PALETTES = {
    "tornado": [
        (0.00, "minecraft:deepslate_tiles"),
        (0.12, "minecraft:gray_concrete"),
        (0.32, "minecraft:light_gray_concrete"),
        (0.50, "minecraft:white_concrete"),
        (0.65, "minecraft:light_gray_concrete"),
        (0.78, "minecraft:white_concrete"),
        (0.90, "minecraft:light_gray_concrete"),
        (1.00, "minecraft:gray_concrete"),
    ],
    "tornado_glass_layers": [
        (0.00, "minecraft:deepslate_tiles"),
        (0.10, "minecraft:gray_concrete"),
        (0.26, "minecraft:light_gray_concrete"),
        (0.42, "minecraft:white_concrete"),
        (0.50, "minecraft:white_stained_glass"),
        (0.58, "minecraft:light_blue_stained_glass"),
        (0.66, "minecraft:cyan_stained_glass"),
        (0.74, "minecraft:blue_stained_glass"),
        (0.82, "minecraft:light_blue_stained_glass"),
        (0.90, "minecraft:white_stained_glass"),
        (1.00, "minecraft:gray_stained_glass"),
    ],
    "tornado_glass": [
        (0.00, "minecraft:deepslate_tiles"),
        (0.10, "minecraft:gray_concrete"),
        (0.26, "minecraft:light_gray_concrete"),
        (0.40, "minecraft:white_concrete"),
        (0.50, "minecraft:white_stained_glass"),
        (0.58, "minecraft:light_gray_concrete"),
        (0.66, "minecraft:light_blue_stained_glass"),
        (0.74, "minecraft:cyan_stained_glass"),
        (0.82, "minecraft:white_stained_glass"),
        (0.90, "minecraft:light_gray_concrete"),
        (0.96, "minecraft:blue_stained_glass"),
        (1.00, "minecraft:white_stained_glass"),
    ],
}


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def smoothstep(value):
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def hash3(x, y, z, seed=0):
    value = math.sin(x * 12.9898 + y * 78.233 + z * 37.719 + seed * 19.19) * 43758.5453
    return value - math.floor(value)


def color_at(t, palette):
    stops = PALETTES[palette]
    for index in range(len(stops) - 1):
        lo_t, lo_name = stops[index]
        hi_t, hi_name = stops[index + 1]
        if t <= hi_t:
            span = max(hi_t - lo_t, 1e-9)
            frac = (t - lo_t) / span
            return lo_name, hi_name, clamp(frac)
    return stops[-1][1], stops[-1][1], 0.0


def main():
    parser = argparse.ArgumentParser(description="Map a Y colour curve onto a white schematic")
    parser.add_argument("input", type=Path, help="white source .schem")
    parser.add_argument("--output", type=Path, default=None, help="coloured full .schem")
    parser.add_argument("--overlay", type=Path, default=None, help="colour-only overlay .schem")
    parser.add_argument("--palette", choices=sorted(PALETTES), default="tornado")
    parser.add_argument("--send", action="store_true", help="load overlay as clipboard and paste with -a -o")
    parser.add_argument("--url", default="http://127.0.0.1:8777")
    parser.add_argument("--name", default=None, help="clipboard name; defaults to output stem")
    parser.add_argument("--target", default="minecraft:white_concrete", help="only recolour this block state")
    args = parser.parse_args()

    source = read_schem(args.input)
    width, height, length = source.width, source.height, source.length
    total = width * height * length
    indices = list(decode_varints(source.block_data))
    if len(indices) != total:
        raise SystemExit(f"block data length {len(indices)} != {total}")

    air_index = source.palette.index("minecraft:air") if "minecraft:air" in source.palette else 0
    target_index = source.palette.index(args.target) if args.target in source.palette else None
    if target_index is None:
        raise SystemExit(f"target block not found: {args.target}")
    counts = [0] * height
    ys = []
    for index, palette_index in enumerate(indices):
        if palette_index != target_index:
            continue
        y = (index // (width * length)) % height
        counts[y] += 1
        ys.append(y)
    if not ys:
        raise SystemExit("no non-air blocks")
    min_y, max_y = min(ys), max(ys)
    span_y = max(max_y - min_y, 1)
    total_target = max(sum(counts), 1)
    cumulative = []
    running = 0
    for count in counts:
        cumulative.append(running + count / 2.0)
        running += count
    print(f"Y range {min_y}..{max_y}; non-air {len(ys)}; peak {max(counts)}")
    for y in range(min_y, max_y + 1, max(1, span_y // 12)):
        q = cumulative[y] / total_target
        print(f"  y={y:3d} {counts[y]:6d}  q={q:.3f}")

    palette_names = list(source.palette)
    for _, name in PALETTES[args.palette]:
        if name not in palette_names:
            palette_names.append(name)
    palette_index = {name: i for i, name in enumerate(palette_names)}
    full_data = bytearray()
    overlay_data = bytearray()
    used = {name: 0 for name in palette_names}
    for index, source_index in enumerate(indices):
        x = index % width
        z = (index // width) % length
        y = index // (width * length)
        if source_index == air_index:
            full_data.extend(encode_varint(palette_index["minecraft:air"]))
            overlay_data.extend(encode_varint(palette_index["minecraft:air"]))
            continue
        if source_index != target_index:
            full_data.extend(encode_varint(source_index))
            overlay_data.extend(encode_varint(palette_index["minecraft:air"]))
            continue
        # Quantile mapping: wide/top-heavy vortex gets balanced colour area
        # rather than letting the broad top rim dominate the palette.
        t = cumulative[y] / total_target
        t = smoothstep(t)
        # Organic, low-frequency wobble so the transition is not a clean ring.
        t += 0.025 * math.sin(x * 0.09 + y * 0.05 + z * 0.11)
        t = clamp(t)
        lo, hi, frac = color_at(t, args.palette)
        bayer = BAYER[(x & 3)][(z & 3)] / 16.0
        choice = hi if frac > bayer else lo
        # Sparse pale-blue cells in the mid/upper vortex, driven by a cell hash.
        if 0.55 < t < 0.86 and y > 50:
            cell = hash3(x // 6, y // 6, z // 6, seed=7)
            if cell > 0.86:
                choice = "minecraft:light_blue_concrete"
                if choice not in palette_index:
                    palette_index[choice] = len(palette_names)
                    palette_names.append(choice)
        full_data.extend(encode_varint(palette_index[choice]))
        overlay_data.extend(encode_varint(palette_index[choice]))
        used[choice] = used.get(choice, 0) + 1

    # write_schem expects a palette dict in the order of the varint indices.
    palette = {name: i for i, name in enumerate(palette_names)}
    output = args.output or args.input.with_name(args.input.stem + "_colored.schem")
    overlay = args.overlay or args.input.with_name(args.input.stem + "_overlay.schem")
    write_schem(output, width, height, length, palette, bytes(full_data), source.data_version)
    write_schem(overlay, width, height, length, palette, bytes(overlay_data), source.data_version)
    print(f"wrote {output} ({output.stat().st_size} bytes)")
    print(f"wrote {overlay} ({overlay.stat().st_size} bytes)")
    print("colours:", ", ".join(f"{k}={v}" for k, v in sorted(used.items(), key=lambda p: -p[1])))

    if args.send:
        name = args.name or output.stem.replace("_colored", "")
        # A 128^3 clipboard is too large for WorldEdit-CLI's //paste path.
        # Upload the fully coloured schematic and let the server load it.
        import urllib.parse
        import urllib.request
        upload_name = name if name.endswith(".schem") else f"{name}.schem"
        url = args.url.rstrip("/") + "/api/upload?name=" + urllib.parse.quote(upload_name)
        request = urllib.request.Request(
            url,
            data=output.read_bytes(),
            headers={"Content-Type": "application/octet-stream"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=600) as response:
            result = json.loads(response.read().decode("utf-8"))
        print(f"uploaded={result.get('state', {}).get('name')} blocks={result.get('state', {}).get('blockCount')}")


if __name__ == "__main__":
    main()
