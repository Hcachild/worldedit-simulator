"""Ensure WorldEdit-CLI has the block data for a schematic's DataVersion."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from core.schematic import SUPPORTED_DATA_VERSIONS, data_version, nearest_supported  # noqa: E402
from core.worldedit import DataNotFound, ensure_data  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: ensure_data.py <file.schem> [more.schem ...]")
        return 1
    status = 0
    for arg in sys.argv[1:]:
        path = Path(arg).resolve()
        if not path.exists():
            print(f"file not found: {path}")
            status = 1
            continue
        if path.suffix.lower() == ".schematic":
            print(f"{path.name}: 旧 .schematic 不支持，请先在 WorldEdit 中另存为 .schem")
            status = 1
            continue
        try:
            version = data_version(path)
        except Exception as exc:
            print(f"{path.name}: {exc}")
            status = 1
            continue
        try:
            ensure_data(version)
        except DataNotFound:
            print(
                f"No CLI data published for DataVersion {version}.\n"
                f"Published versions: {', '.join(map(str, SUPPORTED_DATA_VERSIONS))}\n"
                f'Retarget first: python tools\\retarget_schem.py "{path}" {nearest_supported(version)}'
            )
            status = 1
        except Exception as exc:
            print(f"Could not download data for DataVersion {version}: {exc}")
            status = 1
        else:
            print(f"[data] {path.name}: DataVersion {version} ready")
    return status


if __name__ == "__main__":
    sys.exit(main())
