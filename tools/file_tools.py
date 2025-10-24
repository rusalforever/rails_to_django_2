# tools/file_tools.py
import os
import json
import shutil
from pathlib import Path


def list_tree(root: str, globs: list[str] | None = None) -> dict:
    """Recursively list directories and files under a root path."""
    dirs, files = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        for d in dirnames:
            dirs.append(os.path.join(dirpath, d))
        for f in filenames:
            if globs:
                if not any(f.endswith(ext) for ext in globs):
                    continue
            files.append(os.path.join(dirpath, f))
    return {"dirs": dirs, "files": files}


def read_files(paths: list[str], max_bytes_per_file: int = 80000) -> dict:
    """Read text content from files, skipping directories and binaries."""
    results = {}
    for path in paths:
        if not os.path.exists(path):
            continue
        if os.path.isdir(path):
            print(f"⚠️ Skipping directory: {path}")
            continue
        try:
            with open(path, "rb") as f:
                raw = f.read(max_bytes_per_file)
            if b"\x00" in raw:
                print(f"⚠️ Skipping binary file: {path}")
                continue
            content = raw.decode("utf-8", errors="ignore")
            results[path] = {"content": content, "truncated": len(raw) >= max_bytes_per_file}
        except Exception as e:
            print(f"⚠️ Failed to read {path}: {e}")
    return results


def write_file(path: str, content: str, makedirs: bool = True) -> dict:
    """Write text file safely (backward compatible)."""
    if isinstance(path, Path):
        path = str(path)
    if makedirs:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return {"written": True, "path": path}


def write_json(path: str, obj: dict, makedirs: bool = True) -> dict:
    """Write JSON file safely (backward compatible)."""
    if isinstance(path, Path):
        path = str(path)
    if makedirs:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    return {"written": True, "path": path}


def ensure_dir(path: str | Path) -> None:
    """Ensure a single directory exists (for newer nodes)."""
    os.makedirs(path, exist_ok=True)


def ensure_dirs(paths: list[str]) -> dict:
    """Ensure one or more directories exist (legacy)."""
    for p in paths:
        os.makedirs(p, exist_ok=True)
    return {"created": paths}


def copy_files(pairs: list[dict]) -> dict:
    """Copy files between src/dst pairs."""
    copied = []
    for pair in pairs:
        src, dst = pair.get("src"), pair.get("dst")
        if not os.path.isfile(src):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(dst)
    return {"copied": copied}


def read_json(path: str) -> dict:
    """Read a JSON file safely (useful for reading state files)."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to read JSON {path}: {e}")
        return {}
