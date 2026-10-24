"""Create a minimal Sponge v2 .schem (gzipped NBT) for testing WorldEdit CLI."""
import gzip
import struct
import sys
from pathlib import Path

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_BYTE_ARRAY = 0, 1, 2, 3, 7
TAG_STRING, TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY = 8, 9, 10, 11


def s(value: str) -> bytes:
    raw = value.encode("utf-8")
    return struct.pack(">H", len(raw)) + raw


def tag(tag_id: int, name: str, payload: bytes) -> bytes:
    return bytes([tag_id]) + s(name) + payload


def compound(entries: bytes) -> bytes:
    return entries + b"\x00"


def make_schem(width=5, height=5, length=5, data_version=3955) -> bytes:
    count = width * height * length
    root = compound(
        tag(TAG_INT, "Version", struct.pack(">i", 2))
        + tag(TAG_INT, "DataVersion", struct.pack(">i", data_version))
        + tag(TAG_SHORT, "Width", struct.pack(">h", width))
        + tag(TAG_SHORT, "Height", struct.pack(">h", height))
        + tag(TAG_SHORT, "Length", struct.pack(">h", length))
        + tag(TAG_INT_ARRAY, "Offset", struct.pack(">i", 3) + struct.pack(">iii", 0, 0, 0))
        + tag(
            TAG_COMPOUND,
            "Metadata",
            compound(
                tag(TAG_INT, "WEOffsetX", struct.pack(">i", 0))
                + tag(TAG_INT, "WEOffsetY", struct.pack(">i", 0))
                + tag(TAG_INT, "WEOffsetZ", struct.pack(">i", 0))
            ),
        )
        + tag(TAG_INT, "PaletteMax", struct.pack(">i", 2))
        + tag(
            TAG_COMPOUND,
            "Palette",
            compound(
                tag(TAG_INT, "minecraft:stone", struct.pack(">i", 0))
                + tag(TAG_INT, "minecraft:gold_block", struct.pack(">i", 1))
            ),
        )
        + tag(TAG_BYTE_ARRAY, "BlockData", struct.pack(">i", count) + bytes(count))
        + tag(TAG_LIST, "BlockEntities", bytes([TAG_COMPOUND]) + struct.pack(">i", 0))
    )
    return gzip.compress(bytes([TAG_COMPOUND]) + s("Schematic") + root)


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("demo.schem")
    data_version = int(sys.argv[2]) if len(sys.argv) > 2 else 3955
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(make_schem(data_version=data_version))
    print(f"wrote {out} ({out.stat().st_size} bytes, DataVersion {data_version})")
