from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

PIPELINE_STEPS: list[tuple[str, Path]] = [
    ("Ingestion", PROJECT_ROOT / "02_Ingestion" / "ingest_to_raw.py"),
    ("Transform", PROJECT_ROOT / "04_Transform" / "transform_pipeline.py"),
]


def _run_step(name: str, script_path: Path) -> None:
    if not script_path.exists():
        raise FileNotFoundError(f"Pipeline step '{name}' not found: {script_path}")

    print(f"\n[{name}] Running {script_path.relative_to(PROJECT_ROOT)}", flush=True)
    result = subprocess.run([sys.executable, str(script_path)], cwd=PROJECT_ROOT, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Pipeline step '{name}' failed with exit code {result.returncode}.")


def main() -> None:
    print("Starting root pipeline run...", flush=True)
    for step_name, step_path in PIPELINE_STEPS:
        _run_step(step_name, step_path)
    print("\nPipeline completed successfully.", flush=True)


if __name__ == "__main__":
    main()
