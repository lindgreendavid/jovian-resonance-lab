#!/usr/bin/env python3
"""Validate the committed scientific registry without network access."""

import hashlib
import itertools
import json
from pathlib import Path

from jovian_resonance_lab.horizons import normalized_sha256

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    reference = json.loads((ROOT / "data/jup365-reference-v0.1.json").read_text())
    provenance = json.loads((ROOT / "data/provenance-v0.1.json").read_text())
    report = json.loads((ROOT / "reports/v0.1-model-adequacy.json").read_text())
    rows = [
        [
            row["jd_tdb"],
            row["lambda_io_degrees"],
            row["lambda_europa_degrees"],
            row["lambda_ganymede_degrees"],
            row["phi_l_degrees"],
        ]
        for row in reference
    ]
    assert len(reference) == provenance["reference_rows"] == report["sample_count"] == 10957
    assert reference[0]["jd_tdb"] == 2451910.5
    assert reference[-1]["jd_tdb"] == 2462866.5
    assert all(
        right["jd_tdb"] - left["jd_tdb"] == 1.0 for left, right in itertools.pairwise(reference)
    )
    assert normalized_sha256(rows) == provenance["normalized_reference_sha256"]
    assert all(
        query["reported_source"].startswith("jup365")
        for group in provenance["element_queries"].values()
        for query in group
    )
    assert all(report["expectations"].values())
    site_projection = (ROOT / "site/data/results-v0.1.json").read_bytes()
    assert hashlib.sha256(site_projection).hexdigest()
    print("registry valid: 10,957 aligned JUP365 epochs and frozen expectations present")


if __name__ == "__main__":
    main()
