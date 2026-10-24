#!/usr/bin/env python3
"""Local 3D WorldEdit simulator: HTTP server + WorldEdit-CLI runner."""
import base64
import gzip
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / "static"
SCHEM_DIR = ROOT / "schematics"
WORK_DIR = ROOT / "work"
JAVA = ROOT / "jdk-25.0.4.1+1-jre" / "bin" / "java.exe"
JAR = ROOT / "bin" / "worldedit-cli-7.4.7-SNAPSHOT-dist.jar"
PORT = 8777

sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
from ensure_data import CACHE_DIR, DATA_URL, DataNotFound, download, schematic_data_version  # noqa: E402
from inspect_schem import Reader  # noqa: E402

LOCK = threading.RLock()
STATE = {"source": None, "current": None, "name": None, "data": None}
ANSI = re.compile(r"\x1b\[[0-9;]*m")
NOISE = re.compile(
    r"Log4j plugins|Please remove the `packages` attribute|logging\.apache\.org/log4j"
)


def varints(raw):
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


def read_schem(path: Path) -> dict:
    with gzip.open(path, "rb") as fh:
        name, root = Reader(fh.read()).root()

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

    palette = [""] * (max(int(i) for i in palette_raw.values()) + 1)
    for state_name, index in palette_raw.items():
        palette[int(index)] = state_name

    total = 0
    non_air = 0
    for index in varints(raw):
        total += 1
        if palette[index] != "minecraft:air":
            non_air += 1

    return {
        "name": path.name,
        "width": int(schematic["Width"]),
        "height": int(schematic["Height"]),
        "length": int(schematic["Length"]),
        "dataVersion": int(schematic.get("DataVersion", 0)),
        "formatVersion": version,
        "palette": palette,
        "data": base64.b64encode(raw).decode("ascii"),
        "blockCount": non_air,
        "totalBlocks": total,
    }


def payload() -> dict:
    data = STATE["data"]
    if data is None:
        raise RuntimeError("还没有载入投影")
    return {
        "ok": True,
        **data,
        "name": STATE["name"],
        "source": Path(STATE["source"]).name if STATE["source"] else None,
    }


def safe_name(raw: str) -> str:
    name = Path(raw).name.strip()
    if not name or name in (".", ".."):
        raise ValueError("文件名无效")
    lower = name.lower()
    if lower.endswith(".schematic"):
        raise ValueError("网页只支持 Sponge .schem 投影")
    if not lower.endswith(".schem"):
        name += ".schem"
    return name


def ensure_data(path: Path) -> int:
    version = schematic_data_version(path)
    target = CACHE_DIR / f"{version}_1.json"
    if not target.exists():
        try:
            download(DATA_URL.format(version=version), target)
        except DataNotFound:
            from retarget_schem import SUPPORTED, nearest_supported

            raise RuntimeError(
                f"DataVersion {version} 没有官方方块数据。可先运行：\n"
                f"python tools\\retarget_schem.py \"{path}\" {nearest_supported(version)}\n"
                f"已发布版本：{', '.join(map(str, SUPPORTED))}"
            ) from None
    return version


def load_file(path: Path) -> dict:
    with LOCK:
        ensure_data(path)
        WORK_DIR.mkdir(parents=True, exist_ok=True)
        current = WORK_DIR / "current.schem"
        shutil.copy2(path, current)
        STATE.update(source=path, current=current, name=path.name, data=read_schem(current))
        return payload()


def reset_file() -> dict:
    with LOCK:
        if not STATE["source"]:
            raise RuntimeError("还没有载入投影")
        return load_file(Path(STATE["source"]))


def run_commands(text: str) -> dict:
    with LOCK:
        if not STATE["current"]:
            raise RuntimeError("还没有载入投影")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return {"ok": True, "log": "", "state": payload()}
        if lines[-1] != "stop":
            lines.append("stop")
        ensure_data(Path(STATE["current"]))

        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as handle:
            handle.write("\n".join(lines) + "\n")
            script = Path(handle.name)

        command = [
            str(JAVA),
            "-Dfile.encoding=UTF-8",
            "-Dstdout.encoding=UTF-8",
            "-Dstderr.encoding=UTF-8",
            f"-Dlog4j.configurationFile={ROOT / 'bin' / 'log4j2.xml'}",
            "-jar",
            str(JAR),
            "-f",
            str(STATE["current"]),
            "-s",
            str(script),
        ]
        try:
            try:
                result = subprocess.run(
                    command,
                    cwd=ROOT,
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=180,
                )
                raw_log = (result.stdout or "") + (result.stderr or "")
                code = result.returncode
            except subprocess.TimeoutExpired as exc:
                raw_log = (exc.stdout or "") + (exc.stderr or "")
                if isinstance(raw_log, bytes):
                    raw_log = raw_log.decode("utf-8", "replace")
                return {"ok": False, "error": "命令执行超时（180 秒）", "log": ANSI.sub("", raw_log)}

            log = "\n".join(
                line
                for line in ANSI.sub("", raw_log).splitlines()
                if not NOISE.search(line) and not re.fullmatch(r"[\s>]*", line)
            ).strip()
            try:
                STATE["data"] = read_schem(Path(STATE["current"]))
            except Exception as exc:  # noqa: BLE001
                return {"ok": False, "error": f"读取结果失败：{exc}", "log": log}
            return {"ok": code == 0, "log": log, "state": payload()}
        finally:
            script.unlink(missing_ok=True)


def list_files() -> list:
    files = []
    for path in sorted(SCHEM_DIR.glob("*.schem")):
        stat = path.stat()
        files.append(
            {
                "name": path.name,
                "size": stat.st_size,
                "mtime": int(stat.st_mtime),
                "active": STATE["name"] == path.name,
            }
        )
    return files


class LocalServer(ThreadingHTTPServer):
    allow_reuse_address = False


def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def log_message(self, fmt, *args):
        if sys.stderr is not None:
            sys.stderr.write("[web] %s\n" % (fmt % args))

    def send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message, code=400):
        self.send_json({"ok": False, "error": str(message)}, code)

    def read_body(self, limit: int) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        if length > limit:
            raise ValueError("文件过大")
        return self.rfile.read(length)

    def do_GET(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/state":
                if STATE["data"] is None:
                    return self.send_error_json("还没有载入投影", 404)
                return self.send_json(payload())
            if parsed.path == "/api/files":
                return self.send_json({"ok": True, "files": list_files()})
            if parsed.path == "/api/download":
                if not STATE["current"]:
                    return self.send_error_json("还没有载入投影", 404)
                blob = Path(STATE["current"]).read_bytes()
                name = STATE["name"] or "result.schem"
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header(
                    "Content-Disposition",
                    f"attachment; filename*=UTF-8''{quote(name)}",
                )
                self.send_header("Content-Length", str(len(blob)))
                self.end_headers()
                self.wfile.write(blob)
                return
        except Exception as exc:  # noqa: BLE001
            return self.send_error_json(exc, 500)
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/load":
                body = json.loads(self.read_body(64 * 1024) or b"{}")
                name = safe_name(body.get("name", ""))
                return self.send_json({"ok": True, "state": load_file(SCHEM_DIR / name)})

            if parsed.path == "/api/run":
                body = json.loads(self.read_body(256 * 1024) or b"{}")
                return self.send_json(run_commands(body.get("commands", "")))

            if parsed.path == "/api/reset":
                return self.send_json({"ok": True, "state": reset_file()})

            if parsed.path == "/api/upload":
                query = parse_qs(parsed.query)
                name = safe_name(query.get("name", ["upload.schem"])[0])
                target = SCHEM_DIR / name
                if target.exists():
                    stem, suffix = target.stem, target.suffix
                    counter = 1
                    while target.exists():
                        target = SCHEM_DIR / f"{stem}_{counter}{suffix}"
                        counter += 1
                target.write_bytes(self.read_body(128 * 1024 * 1024))
                try:
                    state = load_file(target)
                except Exception:
                    target.unlink(missing_ok=True)
                    raise
                return self.send_json({"ok": True, "state": state})

            if parsed.path == "/api/save-as":
                body = json.loads(self.read_body(64 * 1024) or b"{}")
                if not STATE["current"]:
                    raise RuntimeError("还没有载入投影")
                name = safe_name(body.get("name", ""))
                target = SCHEM_DIR / name
                shutil.copy2(STATE["current"], target)
                return self.send_json({"ok": True, "name": target.name})
        except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
            return self.send_error_json(exc, 400)
        except Exception as exc:  # noqa: BLE001
            return self.send_error_json(exc, 500)
        return self.send_error_json("not found", 404)


def main():
    if sys.stdout is None or sys.stderr is None:
        stream = open(
            Path(tempfile.gettempdir()) / "worldedit-simulator-web.log",
            "a",
            encoding="utf-8",
            buffering=1,
        )
        if sys.stdout is None:
            sys.stdout = stream
        if sys.stderr is None:
            sys.stderr = stream

    if not JAVA.exists():
        raise SystemExit(f"找不到 Java: {JAVA}")
    if not JAR.exists():
        raise SystemExit(f"找不到 WorldEdit CLI: {JAR}")
    SCHEM_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    url = f"http://127.0.0.1:{PORT}/"
    if port_in_use(PORT):
        print(f"[web] 已有实例在运行: {url}")
        if not os.environ.get("WEB_NO_OPEN"):
            webbrowser.open(url)
        return

    demo = SCHEM_DIR / "demo.schem"
    if demo.exists():
        try:
            load_file(demo)
            print(f"[web] 已载入 {demo.name}")
        except Exception as exc:  # noqa: BLE001
            print(f"[web] 载入 demo 失败: {exc}")

    server = None
    try:
        server = LocalServer(("127.0.0.1", PORT), Handler)
    except OSError as exc:
        if getattr(exc, "errno", None) in (48, 98, 10048):
            print(f"[web] 已有实例在运行: {url}")
            if not os.environ.get("WEB_NO_OPEN"):
                webbrowser.open(url)
            return
        raise

    print(f"[web] 3D 模拟器: {url}  (Ctrl+C 退出)")
    if not os.environ.get("WEB_NO_OPEN"):
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[web] 已停止")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
