"""Sponge schematic reading, writing, and DataVersion helpers."""
import gzip
import shutil
import struct
from dataclasses import dataclass
from pathlib import Path

from .nbt import (
    Reader,
    TAG_BYTE_ARRAY,
    TAG_COMPOUND,
    TAG_INT,
    TAG_INT_ARRAY,
    TAG_LIST,
    TAG_SHORT,
    compound,
    decode_varints,
    patch_data_version,
    s,
    tag,
)

SUPPORTED_DATA_VERSIONS = (
    3698,
    3700,
    3837,
    3953,
    3955,
    4080,
    4189,
    4325,
    4435,
    4438,
    4440,
)
MCEdit_DATA_VERSION = 1631


@dataclass(frozen=True)
class Schematic:
    width: int
    height: int
    length: int
    data_version: int
    format_version: int
    palette: list
    block_data: bytes
    block_count: int
    total_blocks: int


def _read_root(path: Path):
    with gzip.open(path, "rb") as handle:
        return Reader(handle.read()).root()


def read_schem(path: Path) -> Schematic:
    name, root = _read_root(Path(path))

    if name == "Schematic":
        schematic = root
    elif isinstance(root.get("Schematic"), dict):
        schematic = root["Schematic"]
    else:
        raise ValueError("不是 Sponge .schem 文件")

    version = int(schematic.get("Version", 1))
    if version >= 3:
        blocks = schematic["Blocks"]
        palette_raw = blocks["Palette"]
        raw = blocks["Data"]
    else:
        palette_raw = schematic["Palette"]
        raw = schematic["BlockData"]

    palette = [""] * (max(int(index) for index in palette_raw.values()) + 1)
    for state, index in palette_raw.items():
        palette[int(index)] = state

    total = 0
    non_air = 0
    for index in decode_varints(raw):
        total += 1
        if palette[index] != "minecraft:air":
            non_air += 1

    return Schematic(
        width=int(schematic["Width"]),
        height=int(schematic["Height"]),
        length=int(schematic["Length"]),
        data_version=int(schematic.get("DataVersion", 0)),
        format_version=version,
        palette=palette,
        block_data=raw,
        block_count=non_air,
        total_blocks=total,
    )


def write_schem(
    path: Path,
    width: int,
    height: int,
    length: int,
    palette: dict,
    block_data: bytes,
    data_version: int = 3955,
) -> None:
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
        + tag(TAG_INT, "PaletteMax", struct.pack(">i", len(palette)))
        + tag(
            TAG_COMPOUND,
            "Palette",
            compound(
                b"".join(
                    tag(TAG_INT, name, struct.pack(">i", index))
                    for name, index in palette.items()
                )
            ),
        )
        + tag(TAG_BYTE_ARRAY, "BlockData", struct.pack(">i", len(block_data)) + block_data)
        + tag(TAG_LIST, "BlockEntities", bytes([TAG_COMPOUND]) + struct.pack(">i", 0))
    )
    payload = gzip.compress(bytes([TAG_COMPOUND]) + s("Schematic") + root)
    Path(path).write_bytes(payload)


def create_blank(path: Path, width: int, height: int, length: int, data_version: int = 3955) -> None:
    write_schem(
        path,
        width,
        height,
        length,
        {"minecraft:air": 0},
        bytes(width * height * length),
        data_version,
    )


def data_version(path: Path) -> int:
    path = Path(path)
    if path.suffix.lower() == ".schematic":
        return MCEdit_DATA_VERSION
    name, root = _read_root(path)
    if name == "Schematic":
        schematic = root
    elif isinstance(root.get("Schematic"), dict):
        schematic = root["Schematic"]
    else:
        raise ValueError("不是 Sponge .schem 文件")
    version = int(schematic.get("DataVersion", 0))
    if version <= 0:
        raise ValueError("投影没有 DataVersion")
    return version


def nearest_supported(version: int) -> int:
    higher = [item for item in SUPPORTED_DATA_VERSIONS if item >= version]
    if higher:
        return min(higher)
    return max(SUPPORTED_DATA_VERSIONS)


def retarget(path: Path, target: int) -> tuple:
    path = Path(path)
    old = data_version(path)
    if old == target:
        return old, old
    raw = path.read_bytes()
    data = gzip.decompress(raw)
    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(path, backup)
    path.write_bytes(gzip.compress(patch_data_version(data, target)))
    return old, target
