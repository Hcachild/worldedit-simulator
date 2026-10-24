"""Generate a solid Sponge .schem for testing."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from core.schematic import write_schem  # noqa: E402


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "test.schem")
    size = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    block = sys.argv[3] if len(sys.argv) > 3 else "minecraft:stone"
    data_version = int(sys.argv[4]) if len(sys.argv) > 4 else 3955
    count = size * size * size
    write_schem(path, size, size, size, {block: 0}, bytes(count), data_version)
    print(f"wrote {path} ({path.stat().st_size} bytes, DataVersion {data_version})")


if __name__ == "__main__":
    main()
