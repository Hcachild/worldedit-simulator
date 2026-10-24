"""Workspace state and file operations for the simulator."""
import base64
import os
import shutil
import subprocess
import threading
from pathlib import Path

from .schematic import (
    SUPPORTED_DATA_VERSIONS,
    create_blank,
    nearest_supported,
    read_schem,
)
from .worldedit import DataNotFound, ensure_data, run_cli


class WorkspaceError(Exception):
    pass


def safe_name(raw) -> str:
    name = Path(str(raw)).name.strip()
    if not name or name in (".", "..") or "/" in name or "\\" in name:
        raise WorkspaceError("文件名无效")
    lower = name.lower()
    if lower.endswith(".schematic"):
        raise WorkspaceError("只支持 Sponge .schem 投影")
    if not lower.endswith(".schem"):
        name += ".schem"
    return name


def unique_name(directory: Path, name: str) -> Path:
    target = directory / name
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    counter = 1
    while True:
        candidate = directory / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


class Workspace:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.schematics = self.root / "schematics"
        self.work_dir = self.root / "work"
        self.current = self.work_dir / "current.schem"
        self.schematics.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.current.unlink(missing_ok=True)
        self._lock = threading.RLock()
        self._source = None
        self._name = None
        self._data = None
        self._dirty = False

    def _path(self, name) -> Path:
        path = self.schematics / safe_name(name)
        if not path.exists():
            raise WorkspaceError(f"文件不存在: {path.name}")
        return path

    def _payload(self):
        if self._data is None:
            return None
        data = self._data
        return {
            "name": self._name,
            "source": self._source.name if self._source else None,
            "dirty": self._dirty,
            "width": data.width,
            "height": data.height,
            "length": data.length,
            "dataVersion": data.data_version,
            "formatVersion": data.format_version,
            "palette": list(data.palette),
            "data": base64.b64encode(data.block_data).decode("ascii"),
            "blockCount": data.block_count,
            "totalBlocks": data.total_blocks,
        }

    def _data_error(self, version: int, path: Path) -> WorkspaceError:
        return WorkspaceError(
            f"DataVersion {version} 没有官方方块数据。\n"
            f"Published versions: {', '.join(map(str, SUPPORTED_DATA_VERSIONS))}\n"
            f"可先运行：python tools\\retarget_schem.py \"{path}\" {nearest_supported(version)}"
        )

    def state(self):
        with self._lock:
            return self._payload()

    def files(self) -> list:
        with self._lock:
            items = []
            for path in sorted(self.schematics.glob("*.schem")):
                stat = path.stat()
                active = path.name == self._name
                items.append(
                    {
                        "name": path.name,
                        "size": stat.st_size,
                        "mtime": int(stat.st_mtime),
                        "active": active,
                        "dirty": self._dirty if active else False,
                    }
                )
            return items

    def load(self, name):
        with self._lock:
            source = self._path(name)
            try:
                data = read_schem(source)
            except Exception as exc:
                raise WorkspaceError(f"无法读取 {source.name}: {exc}") from exc
            if data.data_version <= 0:
                raise WorkspaceError(f"{source.name} 没有 DataVersion")
            try:
                ensure_data(data.data_version)
            except DataNotFound:
                raise self._data_error(data.data_version, source) from None
            shutil.copy2(source, self.current)
            self._source = source
            self._name = source.name
            self._data = data
            self._dirty = False
            return self._payload()

    def new(self, name, width, height, length):
        with self._lock:
            target = self.schematics / safe_name(name)
            try:
                width, height, length = int(width), int(height), int(length)
            except (TypeError, ValueError):
                raise WorkspaceError("尺寸必须是整数") from None
            if not all(1 <= value <= 256 for value in (width, height, length)):
                raise WorkspaceError("尺寸必须在 1–256 之间")
            if target.exists():
                raise WorkspaceError(f"文件已存在: {target.name}")
            try:
                create_blank(target, width, height, length)
            except Exception:
                target.unlink(missing_ok=True)
                raise
            try:
                return self.load(target.name)
            except Exception:
                target.unlink(missing_ok=True)
                raise

    def upload(self, name, payload: bytes):
        with self._lock:
            name = safe_name(name)
            tmp = self.work_dir / "upload.schem"
            tmp.write_bytes(payload)
            try:
                try:
                    data = read_schem(tmp)
                except Exception as exc:
                    raise WorkspaceError(f"无法读取上传文件: {exc}") from exc
                try:
                    ensure_data(data.data_version)
                except DataNotFound:
                    raise self._data_error(data.data_version, tmp) from None
                target = unique_name(self.schematics, name)
                shutil.move(tmp, target)
            except Exception:
                tmp.unlink(missing_ok=True)
                raise
            try:
                return self.load(target.name)
            except Exception:
                target.unlink(missing_ok=True)
                raise

    def rename(self, name, new_name):
        with self._lock:
            source = self._path(name)
            target = self.schematics / safe_name(new_name)
            if target == source:
                return self._payload()
            if target.exists():
                raise WorkspaceError(f"文件已存在: {target.name}")
            source.rename(target)
            if self._source == source:
                self._source = target
                self._name = target.name
            return self._payload()

    def duplicate(self, name, new_name=None):
        with self._lock:
            source = self._path(name)
            if new_name:
                target = self.schematics / safe_name(new_name)
                if target.exists():
                    raise WorkspaceError(f"文件已存在: {target.name}")
            else:
                target = unique_name(self.schematics, f"{source.stem}_copy{source.suffix}")
            shutil.copy2(source, target)
            return target.name

    def delete(self, name):
        with self._lock:
            source = self._path(name)
            if self._source == source:
                self.close()
            source.unlink()
            return self._payload()

    def close(self):
        with self._lock:
            self._source = None
            self._name = None
            self._data = None
            self._dirty = False
            self.current.unlink(missing_ok=True)
            return None

    def save(self):
        with self._lock:
            if self._data is None:
                raise WorkspaceError("还没有载入投影")
            shutil.copy2(self.current, self._source)
            self._dirty = False
            return self._payload()

    def save_as(self, name, overwrite=False):
        with self._lock:
            if self._data is None:
                raise WorkspaceError("还没有载入投影")
            target = self.schematics / safe_name(name)
            if target.exists() and not overwrite:
                raise WorkspaceError(f"文件已存在: {target.name}")
            shutil.copy2(self.current, target)
            self._source = target
            self._name = target.name
            self._dirty = False
            return self._payload()

    def reset(self):
        with self._lock:
            if self._data is None:
                raise WorkspaceError("还没有载入投影")
            shutil.copy2(self._source, self.current)
            self._data = read_schem(self.current)
            self._dirty = False
            return self._payload()

    def run(self, commands: str) -> dict:
        with self._lock:
            if self._data is None:
                raise WorkspaceError("还没有载入投影")
            if not isinstance(commands, str):
                raise WorkspaceError("命令格式无效")
            try:
                ensure_data(self._data.data_version)
            except DataNotFound:
                raise self._data_error(self._data.data_version, self._source) from None
            before = self.current.stat()
            code, log = run_cli(self.current, commands.splitlines())
            after = self.current.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                self._dirty = True
            self._data = read_schem(self.current)
            result = {"ok": code == 0, "log": log, "state": self._payload()}
            if code != 0:
                result["error"] = f"WorldEdit 退出码 {code}"
            return result

    def download(self, name=None):
        with self._lock:
            if name:
                path = self._path(name)
            else:
                if self._data is None:
                    raise WorkspaceError("还没有载入投影")
                path = self.current
            return path.read_bytes(), path.name

    def reveal(self):
        with self._lock:
            if os.name == "nt":
                os.startfile(self.schematics)
            else:
                subprocess.Popen(["xdg-open", str(self.schematics)])
