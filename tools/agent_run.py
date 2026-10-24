"""Send WorldEdit commands to the running simulator from an external agent."""
import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply WorldEdit commands to the current simulator file.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--command", "-c", help="WorldEdit commands, separated by newlines")
    group.add_argument("--file", "-f", type=Path, help="file containing WorldEdit commands")
    parser.add_argument("--actor", default="agent", help="actor label sent to the UI (default: agent)")
    parser.add_argument("--url", default="http://127.0.0.1:8777", help="simulator base URL")
    args = parser.parse_args()

    commands = args.file.read_text(encoding="utf-8") if args.file else args.command
    payload = json.dumps({"commands": commands, "actor": args.actor}).encode("utf-8")
    request = urllib.request.Request(
        args.url.rstrip("/") + "/api/run",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(exc.read().decode("utf-8", "replace"))
        return 1
    except Exception as exc:
        print(f"request failed: {exc}")
        return 1

    if data.get("log"):
        print(data["log"])
    state = data.get("state") or {}
    print(
        f"ok={data.get('ok')} actor={data.get('actor')} revision={state.get('revision')} "
        f"blocks={state.get('blockCount')} dirty={state.get('dirty')}"
    )
    return 0 if data.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
