"""Command-line entrypoint for lightweight registry validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Jovian Resonance Lab artifacts")
    parser.add_argument("report", nargs="?", type=Path, help="machine-readable report to inspect")
    args = parser.parse_args()
    if args.report is None:
        parser.print_help()
        return 0
    data = json.loads(args.report.read_text(encoding="utf-8"))
    print(f"schema={data.get('schema_version')} product={data.get('product_version')}")
    return 0
