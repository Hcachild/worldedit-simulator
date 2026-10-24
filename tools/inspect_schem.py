"""Inspect a Sponge .schem (v2 or v3) and print a block histogram."""
import gzip
import struct
import sys
from collections import Counter
from pathlib import Path

TAG_SIZES = {1: 1, 2: 2, 3: 4, 4: 8, 5: 4, 6: 8}


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def take(self, n: int) -> bytes:
        chunk = self.data[self.pos:self.pos + n]
        self.pos += n
        return chunk

    def unpack(self, fmt: str):
        size = struct.calcsize(fmt)
        return struct.unpack(fmt, self.take(size))[0]

    def string(self) -> str:
        return self.take(self.unpack(">H")).decode("utf-8", "replace")

    def payload(self, tag_id: int):
        if tag_id in TAG_SIZES:
            return self.unpack({1: ">b", 2: ">h", 3: ">i", 4: ">q", 5: ">f", 6: ">d"}[tag_id])
        if tag_id == 7:
            return self.take(self.unpack(">i"))
        if tag_id == 8:
            return self.string()
        if tag_id == 9:
            item_id = self.unpack(">b")
            return [self.payload(item_id) for _ in range(self.unpack(">i"))]
        if tag_id == 10:
            result = {}
            while True:
                child_id = self.unpack(">b")
                if child_id == 0:
                    return result
                name = self.string()
                result[name] = self.payload(child_id)
        if tag_id == 11:
            return [self.unpack(">i") for _ in range(self.unpack(">i"))]
        if tag_id == 12:
            return [self.unpack(">q") for _ in range(self.unpack(">i"))]
        raise ValueError(f"unknown tag {tag_id}")

    def root(self):
        tag_id = self.unpack(">b")
        name = self.string()
        return name, self.payload(tag_id)


def read_varints(raw: bytes):
    value = 0
    shift = 0
    for byte in raw:
        value |= (byte & 0x7F) << shift
        if byte & 0x80:
            shift += 7
        else:
            yield value
            value = 0
            shift = 0


def main(path: Path) -> None:
    with gzip.open(path, "rb") as fh:
        name, root = Reader(fh.read()).root()

    if name == "Schematic":
        schematic, version = root, root.get("Version", 2)
    elif isinstance(root.get("Schematic"), dict):
        schematic, version = root["Schematic"], root["Schematic"].get("Version", 3)
    else:
        raise SystemExit("not a Sponge schematic")

    if version >= 3:
        blocks = schematic["Blocks"]
        palette = {int(v): k for k, v in blocks["Palette"].items()}
        data = blocks["Data"]
    else:
        palette = {int(v): k for k, v in schematic["Palette"].items()}
        data = schematic["BlockData"]

    counts = Counter(palette[i] for i in read_varints(data))
    print(f"file: {path}")
    print(f"format: Sponge v{version}  data version: {schematic.get('DataVersion')}")
    print(
        "size: {}x{}x{}  offset: {}".format(
            schematic.get("Width"), schematic.get("Height"), schematic.get("Length"),
            schematic.get("Offset") or schematic.get("Metadata"),
        )
    )
    for state, count in counts.most_common():
        print(f"  {count:6d}  {state}")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "demo.schem"))
