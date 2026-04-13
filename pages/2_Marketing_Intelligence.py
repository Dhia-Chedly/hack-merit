from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from streamlit_bootstrap import run_bi_script


run_bi_script("pages/2_Marketing_Intelligence.py")
