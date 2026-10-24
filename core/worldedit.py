"""WorldEdit CLI integration: data cache and headless command execution."""
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JAVA = ROOT / "jdk-25.0.4.1+1-jre" / "bin" / "java.exe"
JAR = ROOT / "bin" / "worldedit-cli-7.4.7-SNAPSHOT-dist.jar"
LOG4J = ROOT / "bin" / "log4j2.xml"
CACHE_DIR = ROOT / "worldedit" / "cli-data"
DATA_URL = "https://services.enginehub.org/cassette-deck/we-cli-data/{version}/1"

ANSI = re.compile(r"\x1b\[[0-9;]*m")
NOISE = re.compile(
    r"Log4j plugins|Please remove the `packages` attribute|logging\.apache\.org/log4j"
)


def _hidden_process_options() -> dict:
    if os.name != "nt":
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    return {
        "creationflags": subprocess.CREATE_NO_WINDOW,
        "startupinfo": startupinfo,
    }


class DataNotFound(Exception):
    def __init__(self, version: int):
        super().__init__(version)
        self.version = version


def _download_with_curl(url: str, target: Path) -> None:
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        raise FileNotFoundError("curl not available")
    tmp = target.with_suffix(".tmp")
    try:
        result = subprocess.run(
            [curl, "-fsSL", "--connect-timeout", "20", "--max-time", "120", "--retry", "2", "-o", str(tmp), url],
            capture_output=True,
            text=True,
            timeout=150,
            **_hidden_process_options(),
        )
    except subprocess.TimeoutExpired as exc:
        tmp.unlink(missing_ok=True)
        raise OSError("curl timed out") from exc
    if result.returncode != 0:
        tmp.unlink(missing_ok=True)
        message = (result.stderr or "").strip()
        if "404" in message:
            raise urllib.error.HTTPError(url, 404, message, None, None)
        raise OSError(message or f"curl exited with {result.returncode}")
    if tmp.stat().st_size < 1000:
        size = tmp.stat().st_size
        tmp.unlink(missing_ok=True)
        raise OSError(f"unexpected response size {size}")
    tmp.replace(target)


def _download_with_urllib(url: str, target: Path) -> None:
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = response.read()
    if len(payload) < 1000:
        raise OSError(f"unexpected response size {len(payload)}")
    tmp = target.with_suffix(".tmp")
    tmp.write_bytes(payload)
    tmp.replace(target)


def _download(url: str, target: Path, attempts: int = 3) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            try:
                _download_with_curl(url, target)
            except FileNotFoundError:
                _download_with_urllib(url, target)
            return
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise DataNotFound(int(target.stem.split("_")[0])) from exc
            last_error = exc
        except Exception as exc:
            last_error = exc
        if attempt < attempts:
            time.sleep(2 * attempt)
    raise OSError(f"Could not download {url}: {last_error}")


def ensure_data(version: int) -> None:
    target = CACHE_DIR / f"{version}_1.json"
    if target.exists():
        return
    _download(DATA_URL.format(version=version), target)


def _clean_log(raw: str) -> str:
    lines = []
    for line in ANSI.sub("", raw).splitlines():
        if NOISE.search(line):
            continue
        if re.fullmatch(r"[\s>]*", line):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def run_cli(schematic_path: Path, commands, timeout: int = 180) -> tuple:
    if not JAVA.exists():
        raise RuntimeError(f"找不到 Java: {JAVA}")
    if not JAR.exists():
        raise RuntimeError(f"找不到 WorldEdit CLI: {JAR}")

    lines = [line.strip() for line in commands if line.strip()]
    if not lines:
        return 0, ""
    if lines[-1] != "stop":
        lines.append("stop")

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
        script = Path(handle.name)

    command = [
        str(JAVA),
        "-Dfile.encoding=UTF-8",
        "-Dstdout.encoding=UTF-8",
        "-Dstderr.encoding=UTF-8",
        f"-Dlog4j.configurationFile={LOG4J}",
        "-jar",
        str(JAR),
        "-f",
        str(schematic_path),
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
                timeout=timeout,
                **_hidden_process_options(),
            )
            return result.returncode, _clean_log((result.stdout or "") + (result.stderr or ""))
        except subprocess.TimeoutExpired as exc:
            raw = (exc.stdout or "") + (exc.stderr or "")
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", "replace")
            return 124, _clean_log(raw) + "\n命令执行超时"
    finally:
        script.unlink(missing_ok=True)


