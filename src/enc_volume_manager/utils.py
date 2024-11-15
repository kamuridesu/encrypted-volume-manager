import sys
from pathlib import Path

units = {"B": 1, "KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}


def get_driver_path(path: str) -> Path:
    if sys.platform == "win32":
        return Path(f"{path}:\\")
    return Path(path)
