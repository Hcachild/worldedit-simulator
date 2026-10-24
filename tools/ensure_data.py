"""Ensure WorldEdit-CLI has the block data file for a schematic's DataVersion.

WorldEdit-CLI 7.4.x downloads block registries from EngineHub on first use and
caches them in <cwd>/worldedit/cli-data/<dataVersion>_1.json. That download has
no timeout in Java, so a blocked network makes the CLI hang forever. This
helper pre-fetches the file with a timeout and gives a clear error message.
"""
import gzip
import shutil
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "worldedit" / "cli-data"
DATA_URL = "https://services.enginehub.org/cassette-deck/we-cli-data/{version}/1"
MCEdit_DATA_VERSION = 1631

TAG_SIZES = {1: 1, 2: 2, 3: 4, 4: 8, 5: 4, 6: 8}
TAG_FORMATS = {1: ">b", 2: ">h", 3: ">i", 4: ">q", 5: ">f", 6: ">d"}


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def take(self, n: int) -> bytes:
        chunk = self.data[self.pos:self.pos + n]
        if len(chunk) != n:
            raise ValueError("truncated NBT")
        self.pos += n
        return chunk

    def unpack(self, fmt: str):
        size = struct.calcsize(fmt)
        return struct.unpack(fmt, self.take(size))[0]

    def string(self) -> str:
        return self.take(self.unpack(">H")).decode("utf-8", "replace")

    def payload(self, tag_id: int):
        if tag_id in TAG_SIZES:
            return self.unpack(TAG_FORMATS[tag_id])
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
        raise ValueError(f"unknown NBT tag {tag_id}")

    def root(self):
        tag_id = self.unpack(">b")
        name = self.string()
        return name, self.payload(tag_id)


def schematic_data_version(path: Path) -> int:
    if path.name.lower().endswith(".schematic"):
        return MCEdit_DATA_VERSION
    with gzip.open(path, "rb") as fh:
        name, root = Reader(fh.read()).root()
    if name == "Schematic":
        version = root.get("DataVersion")
    elif isinstance(root.get("Schematic"), dict):
        version = root["Schematic"].get("DataVersion")
    else:
        raise SystemExit(f"{path} is not a Sponge schematic")
    if version is None:
        raise SystemExit(f"{path} has no DataVersion; WorldEdit-CLI cannot load it")
    return int(version)


class DataNotFound(Exception):
    def __init__(self, version: int):
        super().__init__(version)
        self.version = version


def download_with_curl(url: str, target: Path) -> None:
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        raise FileNotFoundError("curl not available")
    tmp = target.with_suffix(".tmp")
    result = subprocess.run(
        [curl, "-fsSL", "--connect-timeout", "20", "--max-time", "120", "--retry", "2", "-o", str(tmp), url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = (result.stderr or "").strip()
        if "404" in message:
            raise urllib.error.HTTPError(url, 404, message, None, None)
        raise OSError(message or f"curl exited with {result.returncode}")
    if tmp.stat().st_size < 1000:
        raise OSError(f"unexpected response size {tmp.stat().st_size}")
    tmp.replace(target)


def download_with_urllib(url: str, target: Path) -> None:
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = response.read()
    if len(payload) < 1000:
        raise OSError(f"unexpected response size {len(payload)}")
    tmp = target.with_suffix(".tmp")
    tmp.write_bytes(payload)
    tmp.replace(target)


def download(url: str, target: Path, attempts: int = 3) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            try:
                download_with_curl(url, target)
            except FileNotFoundError:
                download_with_urllib(url, target)
            return
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise DataNotFound(int(target.stem.split("_")[0])) from exc
            last_error = exc
        except Exception as exc:  # noqa: BLE001 - report any network failure
            last_error = exc
        if attempt < attempts:
            time.sleep(2 * attempt)
    raise SystemExit(f"Could not download {url}: {last_error}")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: ensure_data.py <file.schem> [more.schem ...]")
    for arg in sys.argv[1:]:
        path = Path(arg).resolve()
        if not path.exists():
            raise SystemExit(f"file not found: {path}")
        data_version = schematic_data_version(path)
        target = CACHE_DIR / f"{data_version}_1.json"
        if target.exists():
            print(f"[data] {path.name}: DataVersion {data_version} (cached)")
            continue
        print(f"[data] {path.name}: DataVersion {data_version}, downloading...", flush=True)
        try:
            download(DATA_URL.format(version=data_version), target)
        except DataNotFound:
            from retarget_schem import SUPPORTED, nearest_supported

            raise SystemExit(
                f"No CLI data published for DataVersion {data_version}.\n"
                f"Published versions: {', '.join(map(str, SUPPORTED))}\n"
                "Retarget the schematic first, e.g.\n"
                f'  python tools\\retarget_schem.py "{path}" {nearest_supported(data_version)}'
            ) from None
        print(f"[data] saved {target}")


if __name__ == "__main__":
    main()
