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
    validation_reference = json.loads((ROOT / "data/jup365-reference-v1.0.json").read_text())
    validation_provenance = json.loads((ROOT / "data/provenance-v1.0.json").read_text())
    validation = json.loads((ROOT / "reports/v1.0-validation.json").read_text())
    validation_rows = [
        [
            row["jd_tdb"],
            row["lambda_io_degrees"],
            row["lambda_europa_degrees"],
            row["lambda_ganymede_degrees"],
            row["phi_l_degrees"],
        ]
        for row in validation_reference
    ]
    assert len(validation_reference) == validation_provenance["reference_rows"] == 3653
    assert validation_reference[0]["jd_tdb"] == 2462867.5
    assert validation_reference[-1]["jd_tdb"] == 2466519.5
    assert all(
        right["jd_tdb"] - left["jd_tdb"] == 1.0
        for left, right in itertools.pairwise(validation_reference)
    )
    assert (
        normalized_sha256(validation_rows) == validation_provenance["normalized_reference_sha256"]
    )
    assert validation_provenance["protocol_commit"] == validation["protocol_commit"]
    assert all(validation["ordering_gates"].values())
    assert all(validation["convergence"]["gates"].values())
    assert all(validation["reference_adequacy_gate"].values())
    assert validation["all_confirmatory_gates_pass"] is True
    site_projection = (ROOT / "site/data/results-v0.1.json").read_bytes()
    assert hashlib.sha256(site_projection).hexdigest()
    validation_projection = (ROOT / "site/data/results-v1.0.json").read_bytes()
    assert hashlib.sha256(validation_projection).hexdigest()
    print("registry valid: 14,610 aligned JUP365 epochs and all frozen gates present")


if __name__ == "__main__":
    main()
