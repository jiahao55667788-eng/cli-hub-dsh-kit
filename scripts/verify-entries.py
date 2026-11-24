#!/usr/bin/env python3
"""Verify every registered CLI entry point actually starts and answers --help."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
MANIFEST = HOME / ".cli-hub" / "installed.json"
DIRS = [
    Path(r"C:\cli-anything\.venv\Scripts"),
    Path(os.environ.get("APPDATA", "")) / "npm",
    HOME / ".local" / "bin",
    HOME / ".cargo" / "bin",
    HOME / "bin",
]
TIMEOUT = 6


def resolve(entry: str) -> str | None:
    for d in DIRS:
        for ext in (".exe", ".cmd", ".bat"):
            p = d / (entry + ext)
            if p.exists():
                return str(p)
    return shutil.which(entry)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = []
    for name, meta in sorted(manifest.items()):
        entry = meta.get("entry_point") or name
        exe = resolve(entry)
        if not exe:
            rows.append({"name": name, "entry": entry, "status": "no-entry", "detail": ""})
            continue
        cmd = [exe, "--help"]
        if exe.lower().endswith((".cmd", ".bat")):
            cmd = ["cmd", "/c", exe, "--help"]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=TIMEOUT)
            head = (r.stdout or r.stderr).decode("utf-8", "replace").strip().splitlines()
            rows.append({
                "name": name,
                "entry": entry,
                "status": "ok" if r.returncode in (0, 1, 2) else f"exit{r.returncode}",
                "detail": head[0][:90] if head else "",
            })
        except subprocess.TimeoutExpired:
            rows.append({"name": name, "entry": entry, "status": "timeout", "detail": ""})
        except Exception as exc:  # noqa: BLE001
            rows.append({"name": name, "entry": entry, "status": "error", "detail": str(exc)[:90]})

    out = Path(__file__).resolve().parent.parent / "data" / "verify-local.json"
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    ok = [r for r in rows if r["status"] == "ok"]
    bad = [r for r in rows if r["status"] != "ok"]
    print(f"total={len(rows)} ok={len(ok)} bad={len(bad)}")
    for r in bad:
        print(f"  {r['status']:9} {r['name']:22} entry={r['entry']} {r['detail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
