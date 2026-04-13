from __future__ import annotations

import runpy
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BI_ROOT = PROJECT_ROOT / "05_BI"


def _ensure_bi_on_path() -> None:
    bi_root = str(BI_ROOT)
    if bi_root not in sys.path:
        sys.path.insert(0, bi_root)


def run_bi_script(relative_path: str) -> None:
    target = BI_ROOT / relative_path
    if not target.exists():
        raise FileNotFoundError(f"Target Streamlit script was not found: {target}")

    _ensure_bi_on_path()
    runpy.run_path(str(target), run_name="__main__")
