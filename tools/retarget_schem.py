"""Retarget a Sponge .schem to a DataVersion with published CLI data."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from core.schematic import (  # noqa: E402
    SUPPORTED_DATA_VERSIONS,
    data_version,
    nearest_supported,
    retarget,
)


def main():
    if len(sys.argv) < 2:
        print("usage: retarget_schem.py <file.schem> [target DataVersion]")
        return 1
    path = Path(sys.argv[1]).resolve()
    current = data_version(path)
    target = int(sys.argv[2]) if len(sys.argv) > 2 else nearest_supported(current)
    if target not in SUPPORTED_DATA_VERSIONS:
        print(f"warning: {target} is not in the published list: {', '.join(map(str, SUPPORTED_DATA_VERSIONS))}")
    old, new = retarget(path, target)
    if old == new:
        print(f"{path.name}: already DataVersion {old}")
    else:
        print(f"{path.name}: DataVersion {old} -> {new} (backup: {path.name}.bak)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
