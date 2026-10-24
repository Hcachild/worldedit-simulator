"""Download the vanilla Minecraft client jar used as the block asset pack."""
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
TARGET = ASSETS_DIR / "client.jar"
VERSION = "1.21.1"
MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
MIRROR = "https://bmclapi2.bangbang93.com/version/{version}/client"


def curl() -> str:
    path = shutil.which("curl.exe") or shutil.which("curl")
    if not path:
        raise RuntimeError("curl not available")
    return path


def download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    result = subprocess.run(
        [curl(), "-L", "--retry", "5", "--retry-delay", "5", "--connect-timeout", "30", "--max-time", "900", "-o", str(tmp), url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        tmp.unlink(missing_ok=True)
        raise RuntimeError((result.stderr or "").strip() or f"curl exited {result.returncode}")
    tmp.replace(target)


def fetch_json(url: str) -> dict:
    result = subprocess.run(
        [curl(), "-fsSL", "--retry", "3", "--connect-timeout", "30", "--max-time", "120", url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or "").strip())
    return json.loads(result.stdout)


def valid_jar(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 1_000_000:
        return False
    try:
        with zipfile.ZipFile(path) as archive:
            return "assets/minecraft/blockstates/stone.json" in archive.namelist()
    except zipfile.BadZipFile:
        return False


def find_local_jar() -> Path | None:
    candidates = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        versions = Path(appdata) / ".minecraft" / "versions"
        candidates.extend(
            [
                versions / VERSION / f"{VERSION}.jar",
                versions / VERSION / "client.jar",
            ]
        )
        if versions.exists():
            candidates.extend(versions.glob(f"{VERSION}*/**/*.jar"))
    for candidate in candidates:
        if valid_jar(candidate):
            return candidate
    return None


def main() -> int:
    if valid_jar(TARGET):
        print(f"[assets] {TARGET} already present ({TARGET.stat().st_size} bytes)")
        return 0

    local = find_local_jar()
    if local:
        print(f"[assets] copying local client jar: {local}")
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local, TARGET)
    else:
        print(f"[assets] downloading Minecraft {VERSION} client jar...")
        try:
            manifest = fetch_json(MANIFEST)
            entry = next((item for item in manifest["versions"] if item["id"] == VERSION), None)
            if not entry:
                raise RuntimeError(f"version {VERSION} not found in manifest")
            version = fetch_json(entry["url"])
            url = version["downloads"]["client"]["url"]
            download(url, TARGET)
        except Exception as exc:
            print(f"[assets] direct download failed: {exc}")
            print(f"[assets] retrying mirror...")
            download(MIRROR.format(version=VERSION), TARGET)

    if not valid_jar(TARGET):
        TARGET.unlink(missing_ok=True)
        print("[assets] downloaded file is not a valid Minecraft client jar")
        return 1
    print(f"[assets] ready: {TARGET} ({TARGET.stat().st_size} bytes)")
    print("[assets] these files are for local rendering only and are not committed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

