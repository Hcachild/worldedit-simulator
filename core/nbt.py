"""Minimal NBT reader and writer for Sponge schematic files."""
import struct

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

TAG_FORMATS = {
    TAG_BYTE: ">b",
    TAG_SHORT: ">h",
    TAG_INT: ">i",
    TAG_LONG: ">q",
    TAG_FLOAT: ">f",
    TAG_DOUBLE: ">d",
}


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def take(self, count: int) -> bytes:
        chunk = self.data[self.pos:self.pos + count]
        if len(chunk) != count:
            raise ValueError("truncated NBT data")
        self.pos += count
        return chunk

    def unpack(self, fmt: str):
        size = struct.calcsize(fmt)
        return struct.unpack(fmt, self.take(size))[0]

    def string(self) -> str:
        return self.take(self.unpack(">H")).decode("utf-8", "replace")

    def payload(self, tag_id: int):
        if tag_id in TAG_FORMATS:
            return self.unpack(TAG_FORMATS[tag_id])
        if tag_id == TAG_BYTE_ARRAY:
            return self.take(self.unpack(">i"))
        if tag_id == TAG_STRING:
            return self.string()
        if tag_id == TAG_LIST:
            item_id = self.unpack(">b")
            return [self.payload(item_id) for _ in range(self.unpack(">i"))]
        if tag_id == TAG_COMPOUND:
            value = {}
            while True:
                child_id = self.unpack(">b")
                if child_id == TAG_END:
                    return value
                name = self.string()
                value[name] = self.payload(child_id)
        if tag_id == TAG_INT_ARRAY:
            return [self.unpack(">i") for _ in range(self.unpack(">i"))]
        if tag_id == TAG_LONG_ARRAY:
            return [self.unpack(">q") for _ in range(self.unpack(">i"))]
        raise ValueError(f"unknown NBT tag {tag_id}")

    def root(self):
        tag_id = self.unpack(">b")
        name = self.string()
        return name, self.payload(tag_id)


def s(value: str) -> bytes:
    raw = value.encode("utf-8")
    return struct.pack(">H", len(raw)) + raw


def tag(tag_id: int, name: str, payload: bytes) -> bytes:
    return bytes([tag_id]) + s(name) + payload


def compound(entries: bytes) -> bytes:
    return entries + b"\x00"


def encode_varint(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def decode_varints(raw: bytes):
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


def find_data_version_offset(data: bytes) -> int:
    marker = b"\x03\x00\x0bDataVersion"
    start = 0
    while True:
        index = data.find(marker, start)
        if index < 0:
            raise ValueError("DataVersion tag not found")
        offset = index + len(marker)
        if len(data) >= offset + 4:
            return offset
        start = index + 1


def patch_data_version(data: bytes, target: int) -> bytes:
    offset = find_data_version_offset(data)
    return data[:offset] + struct.pack(">i", target) + data[offset + 4:]
