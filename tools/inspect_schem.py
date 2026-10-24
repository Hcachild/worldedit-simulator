"""Inspect a Sponge .schem file and print a block histogram."""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from core.nbt import decode_varints  # noqa: E402
from core.schematic import read_schem  # noqa: E402


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "demo.schem").resolve()
    data = read_schem(path)
    counts = Counter(data.palette[index] for index in decode_varints(data.block_data))
    print(f"file: {path}")
    print(f"format: Sponge v{data.format_version}  data version: {data.data_version}")
    print(f"size: {data.width}x{data.height}x{data.length}")
    print(f"blocks: {data.block_count} non-air / {data.total_blocks} total")
    for state, count in counts.most_common():
        print(f"  {count:6d}  {state}")


if __name__ == "__main__":
    main()
