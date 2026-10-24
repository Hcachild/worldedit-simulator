#!/usr/bin/env python3
"""HTTP layer for the local 3D WorldEdit simulator."""
import json
import mimetypes
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / "static"
ASSETS_DIR = ROOT / "assets"
PORT = 8777

sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from core.workspace import Workspace, WorkspaceError  # noqa: E402
from core.worldedit import JAR, JAVA  # noqa: E402

WORKSPACE = None


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

    def end_headers(self):
        if not self.path.startswith(("/api/", "/assets/")):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message, status=400):
        self.send_json({"ok": False, "error": str(message)}, status)

    def read_body(self, limit: int) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        if length > limit:
            raise ValueError("请求体过大")
        return self.rfile.read(length)

    def read_json(self, limit: int = 256 * 1024) -> dict:
        return json.loads(self.read_body(limit) or b"{}")

    def stream_events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.close_connection = True
        last = None
        try:
            self.wfile.write(b"retry: 1000\n\n")
            self.wfile.flush()
            while True:
                revision = WORKSPACE.revision
                if revision != last:
                    snapshot = WORKSPACE.snapshot()
                    data = json.dumps(snapshot, ensure_ascii=False)
                    self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    last = snapshot["revision"]
                time.sleep(0.3)
        except (BrokenPipeError, ConnectionResetError, OSError):
            return

    def send_asset(self, relative: str):
        target = (ASSETS_DIR / unquote(relative)).resolve()
        try:
            target.relative_to(ASSETS_DIR.resolve())
        except ValueError:
            return self.send_error_json("not found", 404)
        if not target.is_file():
            return self.send_error_json("not found", 404)
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(target.stat().st_size))
        self.send_header("Cache-Control", "public, max-age=86400")
        self.end_headers()
        with target.open("rb") as handle:
            shutil.copyfileobj(handle, self.wfile)

    def do_GET(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path.startswith("/assets/"):
                return self.send_asset(parsed.path[len("/assets/"):])
            if parsed.path == "/api/state":
                snapshot = WORKSPACE.snapshot()
                return self.send_json({"ok": True, "revision": snapshot["revision"], "state": snapshot["state"]})
            if parsed.path == "/api/events":
                return self.stream_events()
            if parsed.path == "/api/files":
                return self.send_json({"ok": True, "files": WORKSPACE.files()})
            if parsed.path == "/api/download":
                query = parse_qs(parsed.query)
                blob, name = WORKSPACE.download(query.get("name", [None])[0])
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(name)}")
                self.send_header("Content-Length", str(len(blob)))
                self.end_headers()
                self.wfile.write(blob)
                return
        except WorkspaceError as exc:
            return self.send_error_json(exc, 400)
        except Exception as exc:
            return self.send_error_json(exc, 500)
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/load":
                body = self.read_json()
                return self.send_json({"ok": True, "state": WORKSPACE.load(body.get("name", ""))})

            if parsed.path == "/api/new":
                body = self.read_json()
                state = WORKSPACE.new(
                    body.get("name", ""),
                    body.get("width", 16),
                    body.get("height", 16),
                    body.get("length", 16),
                )
                return self.send_json({"ok": True, "state": state})

            if parsed.path == "/api/upload":
                query = parse_qs(parsed.query)
                state = WORKSPACE.upload(query.get("name", ["upload.schem"])[0], self.read_body(128 * 1024 * 1024))
                return self.send_json({"ok": True, "state": state})

            if parsed.path == "/api/rename":
                body = self.read_json()
                state = WORKSPACE.rename(body.get("name", ""), body.get("newName", ""))
                return self.send_json({"ok": True, "state": state})

            if parsed.path == "/api/duplicate":
                body = self.read_json()
                name = WORKSPACE.duplicate(body.get("name", ""), body.get("newName"))
                return self.send_json({"ok": True, "name": name})

            if parsed.path == "/api/delete":
                body = self.read_json()
                return self.send_json({"ok": True, "state": WORKSPACE.delete(body.get("name", ""))})

            if parsed.path == "/api/close":
                return self.send_json({"ok": True, "state": WORKSPACE.close()})

            if parsed.path == "/api/save":
                return self.send_json({"ok": True, "state": WORKSPACE.save()})

            if parsed.path == "/api/save-as":
                body = self.read_json()
                state = WORKSPACE.save_as(body.get("name", ""), bool(body.get("overwrite", False)))
                return self.send_json({"ok": True, "state": state})

            if parsed.path == "/api/reset":
                return self.send_json({"ok": True, "state": WORKSPACE.reset()})

            if parsed.path == "/api/run":
                body = self.read_json()
                return self.send_json(WORKSPACE.run(body.get("commands", ""), body.get("actor", "user")))

            if parsed.path == "/api/reveal":
                WORKSPACE.reveal()
                return self.send_json({"ok": True})
        except (WorkspaceError, ValueError) as exc:
            return self.send_error_json(exc, 400)
        except Exception as exc:
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

    if not JAVA.exists() or not JAR.exists():
        raise SystemExit("缺少 WorldEdit CLI 或 Java 25，请先运行 setup.cmd")

    url = f"http://127.0.0.1:{PORT}/"
    if port_in_use(PORT):
        print(f"[web] 已有实例在运行: {url}")
        if not os.environ.get("WEB_NO_OPEN"):
            webbrowser.open(url)
        return

    try:
        server = LocalServer(("127.0.0.1", PORT), Handler)
    except OSError as exc:
        if getattr(exc, "errno", None) in (48, 98, 10048):
            print(f"[web] 已有实例在运行: {url}")
            if not os.environ.get("WEB_NO_OPEN"):
                webbrowser.open(url)
            return
        raise

    global WORKSPACE
    WORKSPACE = Workspace(ROOT)

    print(f"[web] 3D 模拟器: {url}")
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



