import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_v1_frozen_gates_and_identifiers() -> None:
    report = json.loads((ROOT / "reports/v1.0-validation.json").read_text(encoding="utf-8"))
    provenance = json.loads((ROOT / "data/provenance-v1.0.json").read_text(encoding="utf-8"))
    assert report["protocol_commit"] == provenance["protocol_commit"]
    assert report["interval"]["sample_count"] == provenance["reference_rows"] == 3653
    assert all(report["ordering_gates"].values())
    assert all(report["convergence"]["gates"].values())
    assert all(report["reference_adequacy_gate"].values())
    assert report["convergence"]["medium_vs_fine"]["circular_rmse_degrees"] == pytest.approx(
        0.5734733621
    )
    assert report["convergence"]["estimated_order"] == pytest.approx(1.9840933874)
    assert report["fine_g4j2_reference"]["circular_rmse_degrees"] == pytest.approx(0.4699300640)


def test_v1_public_surfaces_preserve_core_numbers_and_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    report = (ROOT / "docs/research-report-v1.0.md").read_text(encoding="utf-8")
    site = (ROOT / "site/index.html").read_text(encoding="utf-8")
    for text in (readme, report, site):
        assert "3,653" in text
        assert "0.5735°" in text
        assert "1.984" in text
        assert "0.4699°" in text or "0.470°" in text
    assert "not a forty-year blind forecast" in readme
    assert "not an uninterrupted forty-year prediction" in " ".join(report.split())
    assert "not an uninterrupted forty-year forecast" in site
