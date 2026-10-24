"""Rewrite the DataVersion of a Sponge .schem without touching anything else.

WorldEdit-CLI only publishes block data for some Minecraft versions. If a
schematic was saved by a version without published data, retarget it to a
nearby published version before running the CLI:

    python tools/retarget_schem.py schematics/old.schem 3955

A .bak copy is created next to the original file.
"""
import gzip
import shutil
import struct
import sys
from pathlib import Path

SUPPORTED = (3698, 3700, 3837, 3953, 3955, 4080, 4189, 4325, 4435, 4438, 4440)


def nearest_supported(version: int) -> int:
    higher = [v for v in SUPPORTED if v >= version]
    if higher:
        return min(higher)
    return max(SUPPORTED)


def find_data_version_offset(data: bytes) -> int:
    marker = b"\x03\x00\x0bDataVersion"
    start = 0
    while True:
        index = data.find(marker, start)
        if index < 0:
            raise SystemExit("DataVersion tag not found (not a Sponge schematic?)")
        value_offset = index + len(marker)
        if len(data) >= value_offset + 4:
            return value_offset
        start = index + 1


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: retarget_schem.py <file.schem> [target DataVersion]")
    path = Path(sys.argv[1]).resolve()
    raw = path.read_bytes()
    data = gzip.decompress(raw)
    offset = find_data_version_offset(data)
    current = struct.unpack(">i", data[offset:offset + 4])[0]
    target = int(sys.argv[2]) if len(sys.argv) > 2 else nearest_supported(current)
    if target == current:
        print(f"{path.name}: already DataVersion {current}")
        return
    patched = data[:offset] + struct.pack(">i", target) + data[offset + 4:]
    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(path, backup)
    path.write_bytes(gzip.compress(patched))
    print(f"{path.name}: DataVersion {current} -> {target} (backup: {backup.name})")


if __name__ == "__main__":
    main()
