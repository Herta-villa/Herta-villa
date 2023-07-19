from __future__ import annotations

from pathlib import Path


def resource(name: str) -> Path:
    path = Path() / "local_resource" / name
    path.mkdir(parents=True, exist_ok=True)
    return path
